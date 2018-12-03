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
# this plugin can be called from quick action

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

plugin = {"VERSION": "1.4", "NAME": "downloadfile", "TYPE": "master"}


def create_path(type="windows", host="", ipordomain="", path=""):
    """
        warning you must enter a raw string for parameter path
        eg ( a= create_path(host="pulse", ipordomain="192.168.56.103", path=r"C:\Program Files (x86)\Pulse\var\tmp\packages\a170890e-d060-11e7-ade3-0800278dc04d")
    """
    if path == "":
        return ""
    if type == "windows":
        if host != "" and ipordomain != "":
            return "%s@%s:\"\\\"%s\\\"\"" % (host,
                                             ipordomain,
                                             path)
        else:
            return "\"\\\"%s\\\"\"" % (path)
    elif type == "linux":
        if host != "" and ipordomain != "":
            return "%s@%s:\"%s\"" % (host,
                                     ipordomain,
                                     path)
        else:
            return "\"%s\"" % (path)


def scpfile(src, dest):
    cmdpre = "scp -r -o IdentityFile=/root/.ssh/id_rsa "\
        "-o StrictHostKeyChecking=no "\
        "-o UserKnownHostsFile=/dev/null "\
        "-o Batchmode=yes "\
        "-o PasswordAuthentication=no "\
        "-o ServerAliveInterval=10 "\
        "-o CheckHostIP=no "\
        "-o ConnectTimeout=10 "\
        "%s %s" % (src, dest)
    return cmdpre


def isconf():
    if 'CONF' in plugin and plugin['CONF'] is not None and len(plugin['CONF']) > 0:
        return True
    else:
        return False


def fileconf():
    if isconf():
        return os.path.join(*plugin['CONF'])
    return None


def createnamefile(user, prefixe="", suffixe=""):
    now = datetime.datetime.now()
    return "%s_%s_%s%s" % (prefixe, user, str(now.isoformat()), suffixe)


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    try:
        print json.dumps(data[0], indent=4)
        transpxmpp = True
        if 'taillefile' in data[0]:
            # determine si fichier est transportable dans un message xmppmaster
            if "Mo" in data[0]['taillefile']:
                transpxmpp = False
                print "Mo"
            else:
                if "ko" in data[0]['taillefile']:
                    data[0]['taillefile'] = float(data[0]['taillefile'][:-2]) * 1024
                else:
                    data[0]['taillefile'] = float(data[0]['taillefile'])
                if data[0]['taillefile'] > 256000:
                    transpxmpp = False
    except KeyError as e:
        logging.getLogger().debug(
            "data[0] not found while calling %s. The plugin is probably called from a quick action." % (plugin['NAME']))
        pass

    # if transpxmpp:
        # la taille du fichier permet de faire le transfert dans un message xmpp pas encore implemente

    if 'dest' in data and 'src' in data and 'jidmachine' in data:
        jidmachine = data['jidmachine']
        Machineinfo = XmppMasterDatabase().getMachinefromjid(jidmachine)
        dest = data['dest']
        src = data['src']
    else:
        try:
            jidmachine = data[0]['jidmachine']
            Machineinfo = XmppMasterDatabase().getMachinefromjid(jidmachine)
            dest = data[0]['dest']
            src = data[0]['src']
        except KeyError:
            print json.dumps(data, indent=4)
            jidmachine = data['data'][0]
            Machineinfo = XmppMasterDatabase().getMachinefromjid(jidmachine)
            params = data['data'][2]
            if len(params) > 1:
                # if params[1]:
                dest = params[1]
            else:
                machdir = os.path.join(xmppMasterConfig().defaultdir, Machineinfo['hostname'])
                now = datetime.datetime.now()
                try:
                    # Run on a machine
                    datedir = "%s-%s" % (data['data'][1][1]['user'],
                                         now.strftime("%Y-%m-%d-%H:%M:%S"))
                except KeyError:
                    # Run on a group
                    datedir = "%s-%s" % (data['data'][1]['user'], now.strftime("%Y-%m-%d-%H:%M:%S"))
                    pass
                destdir = os.path.join(machdir, datedir)
                if not os.path.exists(machdir):
                    os.mkdir(machdir)
                    os.chmod(machdir, 0777)
                if not os.path.exists(destdir):
                    logging.getLogger().debug("Creating folder: %s" % destdir)
                    os.mkdir(destdir)
                if '\\' in params[0]:
                    final_folder = os.path.basename(os.path.normpath(
                        params[0].replace('\\', '/').replace(':', '')))
                else:
                    final_folder = os.path.basename(os.path.normpath(params[0]))
                dest = os.path.join(destdir, final_folder)
            src = params[0]

    relayserver = XmppMasterDatabase().getMachinefromjid(Machineinfo['groupdeploy'])
    relayserinfo = XmppMasterDatabase().getRelayServerfromjid(Machineinfo['groupdeploy'])

    print json.dumps(relayserinfo, indent=4)
    datasend = {
        'session_id': sessionid,
        'action': "downloadfile",
        'data': {'jidrelayser': Machineinfo['groupdeploy'],
                 'path_src_machine': src,
                 'path_dest_master': dest,
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

    # print json.dumps(datasend, indent = 4)
    try:
        if datasend['data']['ipars'] != str(xmppobject.config.Server):
            cmd = scpfile("root@%s:/root/.ssh/id_rsa.pub" %
                          (datasend['data']['ipars']), "/tmp/id_rsa.pub")
            print cmd
            z = simplecommand(cmd)
            # print z['result']
            # print z['code']
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
                    print authorized_key

        # send message to relayserver for get file on machine
        # to ARS
        xmppobject.send_message(mto=Machineinfo['groupdeploy'],
                                mbody=json.dumps(datasend),
                                mtype='chat')

    except Exception as e:
        logging.getLogger().error("Error in plugin %s : %s" % (plugin['NAME'], str(e)))
        traceback.print_exc(file=sys.stdout)
