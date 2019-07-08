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
            # on ajoute 1 au compteur syncthing dans le groupe.
            #XmppMasterDatabase().incr_count_transfert_terminate(data["iddeploybase"])
            pass
        elif "initialisation" in data["subaction"]:
            #logger.debug("%s"%json.dumps(data, indent=4))
            #logger.debug("=====================================================")
            # le plugin a pour mission de deployer les partage sur les ARS du cluster.
            # puis propager les partages vers les machines. les machines en fonction de leur ARS attribués.
            # pour les partages entre ARS, il faut choisir 1 ARS comme le patron.
            # on appelle cette tache l election syncthing.
            # On choisie au hazard 1 ars static, dans la liste des ars du cluster.
            # la function getCluster_deploy_syncthing renvoi les ARS du cluster
            #logger.debug("=====================================================")
            listclusterobjet = XmppMasterDatabase().getCluster_deploy_syncthing(data['iddeploy'])
            #print "yyyy"
            #print listclusterobjet
            #print "yyyy"
            for clusterobjet in listclusterobjet:
                namedeploy = clusterobjet[0]
                repertoiredeploy = clusterobjet[1]
                packagedeploy = clusterobjet[2]
                clusterdescriptor = json.loads(clusterobjet[6])
                listarsdeploy = clusterdescriptor["listarscluster"]
                listkey = clusterdescriptor["keysyncthing"]
                groupdeploy = clusterobjet[6]
                cmddeploy = clusterobjet[7]
                elected = clusterobjet[4]
                ### todo voir pour plusieurs clusters differents
                keyelected = listkey[listarsdeploy.index(elected)]
                ##### election ####
                #nbr_ars_in_cluster = len(listarsdeploy)
                #if nbr_ars_in_cluster == 0:
                    ##  probleme a voir le cluster des relay
                    #print "probleme a voir le cluster des relay et deploy %s"%data['iddeploy']
                    #return

                #{"listarscluster": ["rspulse@pulse/dev-mmc"], "keysyncthing": ["IGQIW2T-OHEFK3P-JHSB6KH-OHHYABS-YEWJRVC-M6F4NLZ-D6U55ES-VXIVMA3"], "namecluster": "Public", "numcluster": 1}

                #indexarselected = randint(0,nbr_ars_in_cluster -1)
                #elected = listarsdeploy[indexarselected]
                #keyelected = listkey[indexarselected]

                datasend = {'action' : "deploysyncthing",
                            "sessionid" : name_randomplus(30, "syncthingclusterinit"),
                            "ret" : 0,
                            "base64" : False,
                            "data" : { "subaction" : "syncthingdeploycluster",
                                    "namedeploy" : namedeploy,
                                    "packagedeploy" : packagedeploy,
                                    "repertoiredeploy" : repertoiredeploy,
                                    "clusterdescriptor" : clusterdescriptor,
                                    "listarsdeploy" : listarsdeploy,
                                    "listkey" : listkey,
                                    "groupdeploy" : groupdeploy,
                                    "cmddeploy" : cmddeploy,
                                    "elected" : elected,
                                    "keyelected" : keyelected,
                                    "id" : data['iddeploy']
                                    }
                            }
                for t in listarsdeploy:
                    updatedata=[]
                    machines = XmppMasterDatabase().getMachine_deploy_Syncthing(data['iddeploy'], 
                                                                                ars = t, 
                                                                                status=2)

                    partagemachine = []
                    for machine in machines:
                        partagemachine.append({ 'mach' : machine[2],
                                                "rel"  : machine[1],
                                                "ses"  : machine[0],
                                                "devi" : machine[3]})
                        updatedata.append(machine[5])
                    # chang status machine dans table
                    XmppMasterDatabase().updateMachine_deploy_Syncthing(updatedata,
                                                                        statusold=2,
                                                                        statusnew=3)
                    datasend['data']['machinespartage'] = partagemachine
                    xmppobject.send_message(mto=t,
                                            mbody=json.dumps(datasend),
                                            mtype='chat')
