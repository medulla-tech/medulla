#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016-2017 siveo, http://www.siveo.net
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
# file /pluginsmaster/plugin_deploysyncthing.py


import base64
import json
import os
import sys
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
import traceback
from utils import name_random, name_randomplus


import logging
from random import randint

logger = logging.getLogger()
# plugin run wake on lan on mac adress

plugin = {"VERSION": "1.0", "NAME": "deploysyncthing", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, dataobj):
    logger.debug("=====================================================")
    logger.debug(plugin)
    logger.debug("=====================================================")
    if "subaction" in data:
        # this action is calling for machine after terminate transfert syncthing
        if "counttransfertterminate" in data["subaction"]:
            XmppMasterDatabase().incr_count_transfert_terminate(data["iddeploybase"])
            XmppMasterDatabase().update_transfert_progress(100,
                                                           data["iddeploybase"],
                                                           message['from'])
        elif "completion" in data["subaction"]:
            XmppMasterDatabase().update_transfert_progress(data["completion"],
                                                           data["iddeploybase"],
                                                           message['from'])
        elif "initialisation" in data["subaction"]:
            # logger.debug("=====================================================")
            # le plugin a pour mission de deployer les partage sur les ARS du cluster.
            # puis propager les partages vers les machines. les machines en fonction de leur ARS attribués.
            # pour les partages entre ARS, il faut choisir 1 ARS comme le patron.
            # on appelle cette tache l election syncthing.
            # On choisie au hazard 1 ars static, dans la liste des ars du cluster.
            # la function getCluster_deploy_syncthing renvoi les ARS du cluster
            # la fonction getRelayServerfromjid renvoit les toutes les informations de ars
            # logger.debug("=====================================================")
            listclusterobjet = XmppMasterDatabase().getCluster_deploy_syncthing(data['iddeploy'])

            deploy_syncthing_information = {}
            deploy_syncthing_information['namedeploy'] = listclusterobjet[0][0]
            deploy_syncthing_information['namecluster'] = listclusterobjet[0][2]
            deploy_syncthing_information['repertoiredeploy'] = listclusterobjet[0][1]

            clustersdata = json.loads(listclusterobjet[0][6])
            logging.getLogger().debug(json.dumps(clustersdata, indent=4))

            clu = {}
            clu['arslist'] = {}
            clu['arsip'] = {}
            clu['numcluster'] = clustersdata['numcluster']
            nb = random.randint(0, clu['numcluster'] - 1)
            for index, value, in enumerate(clustersdata['listarscluster']):
                val = "%s" % jid.JID(value).bare
                if index == nb:
                    clu['elected'] = val
                clu['arslist'][val] = clustersdata['keysyncthing'][index]
                infoars = XmppMasterDatabase().getRelayServerfromjid(val)
                keycheck = ['syncthing_port', 'ipserver', 'ipconnection']
                if [x for x in keycheck if x in infoars] == keycheck:
                    adressipserver = "tcp://%s:%s" % (infoars['ipserver'],
                                                      infoars['syncthing_port'])
                    adressconnection = "tcp://%s:%s" % (infoars['ipconnection'],
                                                        infoars['syncthing_port'])
                    clu['arsip'][val] = list(set([str(adressipserver), str(adressconnection), str('dynamic')]))
                else:
                    logging.getLogger().error("verify syncthing info for ars %s" % val)
                    clu['arsip'][val] = [str('dynamic')]
            clu['namecluster'] = clustersdata['namecluster']
            deploy_syncthing_information['agentdeploy'] = str(xmppobject.boundjid.bare)
            deploy_syncthing_information['cluster'] = clu
            deploy_syncthing_information['packagedeploy'] = listclusterobjet[0][2]
            deploy_syncthing_information['grp'] = listclusterobjet[0][7]
            deploy_syncthing_information['cmd'] = listclusterobjet[0][8]
            deploy_syncthing_information['syncthing_deploy_group'] = data['iddeploy']

            # List of the machines for this share

            updatedata = []
            machines = XmppMasterDatabase().getMachine_deploy_Syncthing(data['iddeploy'],
                                                                        ars=None,
                                                                        status=2)

            partagemachine = []
            for machine in machines:
                partagemachine.append({'mach': "%s" % jid.JID(machine[2]).bare,
                                       "ses": machine[0],
                                       "devi": machine[3]})
                updatedata.append(machine[5])

            deploy_syncthing_information['machines'] = partagemachine
            # chang status machine partager
            XmppMasterDatabase().updateMachine_deploy_Syncthing(updatedata,
                                                                statusold=2,
                                                                statusnew=3)

            datasend = {'action': "deploysyncthing",
                        "sessionid": name_randomplus(30, "syncthingclusterinit"),
                        "ret": 0,
                        "base64": False,
                        "data": {"subaction": "syncthingdeploycluster"}
                        }
            datasend['data']["objpartage"] = deploy_syncthing_information

            logging.getLogger().error(json.dumps(datasend, indent=4))

            for ars in deploy_syncthing_information['cluster']['arslist']:
                datasend['data']['ARS'] = ars
                xmppobject.send_message(mto=ars,
                                        mbody=json.dumps(datasend),
                                        mtype='chat')
