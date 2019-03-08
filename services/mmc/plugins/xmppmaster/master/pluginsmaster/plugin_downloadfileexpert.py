#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2018 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# file pluginsmaster/plugin_downloadfile.py


import base64
import json
import os
import sys
from utils import simplecommand, file_get_content, file_put_content
import pprint
import logging

import traceback

import datetime
import ConfigParser

from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.xmppmaster.config import xmppMasterConfig

plugin = {"VERSION": "1.0", "NAME": "downloadfileexpert", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("=====================================================")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("=====================================================")

    data=data[0]
    print json.dumps(data, indent=4)

    if 'dest' in data and 'directory' in data and 'listfile' in data and 'jidmachine' in data:
        jidmachine = data['jidmachine']
        try:
            #### reduit enregistrement 
            listdirectory = [ x.strip() for x in data['listdirectory'].split(";") if x.strip() != ""]
            listfile = [ x.strip() for x in data['listfile'].split(";") if x.strip() != ""]
            listdirectory.sort()
            listfile.sort()

            remfile=[]
            for i in listdirectory:
                for t in listfile:
                    if i in t:
                        remfile.append(t)
            for t in list(set(remfile)):
                listfile.remove(t)

            dd=[]
            a=0
            nb = len(listdirectory)
            for y in range (nb - 1):
                if y > a : a = y
                for index in range(a+1, nb):
                    if listdirectory[a] in listdirectory[index]:
                        dd.append( listdirectory[index] )

            for t in list(set(dd)):
                listdirectory.remove(t)

        except Exception as e:
            logging.getLogger().error("Error in plugin %s" % ( str(e) ))
            traceback.print_exc(file=sys.stdout)


        Machineinfo = XmppMasterDatabase().getMachinefromjid(jidmachine)
        #dest = 
        #src = data['src']
        relayserver = XmppMasterDatabase().getMachinefromjid(Machineinfo['groupdeploy'])
        relayserinfo = XmppMasterDatabase().getRelayServerfromjid(Machineinfo['groupdeploy'])
        print "relayserver"
        print json.dumps(relayserver, indent = 4 )
        print "relayserinfo"
        print json.dumps(relayserinfo, indent = 4 )

        if str(Machineinfo['platform']).startswith('Linux') or str(Machineinfo['platform']).startswith('darwin'):
            separator = "/"
        else:
            separator = "\\"
        listdirstr=[ ]
        for t in listdirectory:
            if t.lower() != "c:\\\\" and t.lower() != "d:\\\\":
                listdirstr.append ("%s%s"%(t, separator))
            else:
                listdirstr.append (t)

        datasend = {
        'session_id': sessionid,
        'action': "downloadfileexpert",
        'data': {'jidrelayser': Machineinfo['groupdeploy'],
                 'path_src_machine_dir': listdirstr,
                 'path_src_machine_file': listfile,
                 'path_dest_master': data['dest'],
                 'jidmachine': jidmachine,
                 # item host is uuid glpi machine
                 'host': Machineinfo['uuid_inventorymachine'],
                 'ipars': relayserver['ip_xmpp'],
                 'ipserverars': relayserinfo['ipserver'],
                 'iparspublic': relayserver['ippublic'],
                 'package_server_ip': relayserinfo['package_server_ip'],
                 'ipmachine': Machineinfo['ip_xmpp'],
                 'ipmachinepublic': Machineinfo['ippublic'],
                 'ipmaster': str(xmppobject.config.Server),
                 'osmachine': Machineinfo['platform'],
                 'jidmachine': jidmachine,
                 'hostname': Machineinfo['hostname']
                 }
        }

    # On permet au relay server d'ecrire sur master en ssh.
    try:
        if datasend['data']['ipars'] != str(xmppobject.config.Server):
            cmd = scpfile("root@%s:/root/.ssh/id_rsa.pub" %
                          (datasend['data']['ipars']), "/tmp/id_rsa.pub")
            z = simplecommand(cmd)
            if z['code'] != 0:
                logging.getLogger().warning(z['result'])
                pass
            else:
                dede = file_get_content("/tmp/id_rsa.pub")
                authorized_key = file_get_content("/root/.ssh/authorized_keys")
                # verify key exist in authorized_key for ARS.
                if not dede in authorized_key:
                    logging.getLogger().debug("Add key %s" % datasend['data']['jidmachine'])
                    file_put_content("/root/.ssh/authorized_keysold", "\n" + dede, mode="a")
        xmppobject.send_message(mto=Machineinfo['groupdeploy'],
                                mbody=json.dumps(datasend),
                                mtype='chat')

    except Exception as e:
        logging.getLogger().error("Error in plugin %s : %s" % (plugin['NAME'], str(e)))
        traceback.print_exc(file=sys.stdout)


def scpfile(scr, dest):
    cmdpre = "scp -C -rp3 "\
                "-o IdentityFile=/root/.ssh/id_rsa "\
                "-o StrictHostKeyChecking=no "\
                "-o LogLevel=ERROR "\
                "-o UserKnownHostsFile=/dev/null "\
                "-o Batchmode=yes "\
                "-o PasswordAuthentication=no "\
                "-o ServerAliveInterval=10 "\
                "-o CheckHostIP=no "\
                "-o ConnectTimeout=10 "
    cmdpre =  "%s %s %s"%(cmdpre, scr, dest)
    return cmdpre

