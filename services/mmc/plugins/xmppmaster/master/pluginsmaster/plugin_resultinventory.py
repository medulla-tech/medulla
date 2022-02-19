#!/usr/bin/python3
# -*- coding: utf-8; -*-
#
# (c) 2016-2022 siveo, http://www.siveo.net
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
# file pluginsmaster/plugin_resultinventory.py

import zlib
import base64
import traceback
import os
import sys
import urllib.request, urllib.error, urllib.parse
import time
import json
import logging
from mmc.plugins.glpi.database import Glpi
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.xmppmaster.master.lib.utils import file_put_contents


logger = logging.getLogger()

plugin = {"VERSION": "1.2", "NAME": "resultinventory", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, objsessiondata):
    HEADER = {"Pragma": "no-cache",
              "User-Agent": "Proxy:FusionInventory/Pulse2/GLPI",
              "Content-Type": "application/x-compress",
              }
    try:
        logging.getLogger().debug("===============MASTER============================")
        logging.getLogger().debug(plugin)
        logging.getLogger().debug("=====================================================")

        if not 'inventoryslot' in xmppobject.config.__dict__:
            xmppobject.config.__dict__['inventoryslot'] = False
        else:
            if isinstance(xmppobject.config.__dict__['inventoryslot'], str):
                if xmppobject.config.__dict__['inventoryslot'].lower() == "true" or\
                    xmppobject.config.__dict__['inventoryslot'].lower() == "1" or\
                        xmppobject.config.__dict__['inventoryslot'].lower() == "yes":
                    xmppobject.config.__dict__['inventoryslot'] = True
                else:
                    xmppobject.config.__dict__['inventoryslot'] = False
        logger.debug("inventoryslot %s" % (xmppobject.config.__dict__['inventoryslot']))
        # Directory inventaire.
        RecvInventory = os.path.abspath(  os.path.join( os.path.dirname( __file__), "..", "RecvInventory"))
        if not os.path.exists(RecvInventory):
            os.makedirs( RecvInventory, 0o755 )
            logger.debug("create %s" % RecvInventory)
        try:
            url = xmppobject.config.inventory_url
        except:
            url = "http://localhost:9999/"
        logger.debug("url %s" % (url))
        inventory = zlib.decompress(base64.b64decode(data['inventory']))
        if xmppobject.config.inventoryslot:
            # copy fichier to
            namefile = os.path.join(RecvInventory, "%s_%s.xml"%(time.time(), message['from'].user))
            file_put_contents(namefile,  inventory)
            logger.debug("copy file to %s" % namefile)
            return
        else:
            logger.debug("injection direct of inventory")
            request = urllib2.Request(url, inventory, HEADER)
            try:
                response = urllib2.urlopen(request)
                logger.debug("inject intentory to %s code wed %s" % (url, response.getcode()))
            except urllib2.URLError:
                logger.error("The inventory server is not reachable. Please check pulse2-inventory-server service")
                return

            machine = XmppMasterDatabase().getMachinefromjid(message['from'])
            if not machine:
                logger.error("machine missing in table %s" % (message['from']))
                return
            nbsize = len(inventory)
            XmppMasterDatabase().setlogxmpp("inject inventory to Glpi",
                                            "Master",
                                            "",
                                            0,
                                            message['from'],
                                            'Manuel',
                                            '',
                                            'QuickAction |Inventory | Inventory requested',
                                            '',
                                            '',
                                            "Master")
            if nbsize < 250:
                XmppMasterDatabase().setlogxmpp('<font color="Orange">Warning, Inventory XML size %s byte</font>' % nbsize,
                                                "Master",
                                                "",
                                                0,
                                                message['from'],
                                                'Manuel',
                                                '',
                                                'Inventory | Notify',
                                                '',
                                                '',
                                                "Master")
        if not xmppobject.config.inventoryslot:
            timedata = 6
        else:
            timedata = 15
        time.sleep(timedata)

        logger.debug("** update table after injection")



        if not XmppUpdateInventoried(message['from'], machine):
        #if not xmppobject.XmppUpdateInventoried(message['from']):
            XmppMasterDatabase().setlogxmpp('<font color="deeppink">Error Injection Inventory for Machine %s</font>' % (message['from']),
                                            "Inventory Server",
                                            "",
                                            0,
                                            message['from'],
                                            'auto',
                                            '',
                                            'Inventory | Notify | Error',
                                            '',
                                            '',
                                            "InvServer")
        # save registry inventory
        try:
            reginventory = json.loads(base64.b64decode(data['reginventory']))
        except:
            reginventory = False
        # send inventory to inventory server
        XmppMasterDatabase().setlogxmpp("inject inventory to Glpi",
                                        "Master",
                                        "",
                                        0,
                                        message['from'],
                                        'Manuel',
                                        '',
                                        'QuickAction |Inventory | Inventory requested',
                                        '',
                                        '',
                                        "Master")

        if reginventory:
            counter = 0
            while True:
                computers_id = XmppMasterDatabase().getUuidFromJid(message['from'])
                time.sleep(counter)
                if computers_id or counter >= 10:
                    break
            logging.getLogger().debug("Computers ID: %s" % computers_id)
            nb_iter = int(reginventory['info']['max_key_index']) + 1
            for num in range(1, nb_iter):
                reg_key_num = 'reg_key_'+str(num)
                try:
                    reg_key = reginventory[reg_key_num]['key'].strip('"')
                    reg_key_value = reginventory[reg_key_num]['value'].strip('"')
                    key_name = reg_key.split('\\')[-1]
                    logging.getLogger().debug("Registry information:")
                    logging.getLogger().debug("  reg_key_num: %s" % reg_key_num)
                    logging.getLogger().debug("  reg_key: %s" % reg_key)
                    logging.getLogger().debug("  reg_key_value: %s" % reg_key_value)
                    logging.getLogger().debug("  key_name: %s" % key_name)
                    registry_id = Glpi().getRegistryCollect(reg_key)
                    logging.getLogger().debug("  registry_id: %s" % registry_id)
                    XmppMasterDatabase().setlogxmpp("Inventory Registry information: [machine :  %s][reg_key_num : %s]"
                                                    "[reg_key: %s][reg_key_value : %s]"
                                                    "[key_name : %s]" % (
                                                        message['from'], reg_key_num, reg_key, reg_key_value, key_name),
                                                    "Master",
                                                    "",
                                                    0,
                                                    message['from'],
                                                    'Manuel',
                                                    '',
                                                    'QuickAction |Inventory | Inventory requested',
                                                    '',
                                                    '',
                                                    "Master")
                    Glpi().addRegistryCollectContent(computers_id, registry_id, key_name, reg_key_value)
                except Exception as e:
                    logging.getLogger().debug("Error getting key: %s" % reg_key)
                    pass
        time.sleep(25)
        # restart agent
        # xmppobject.restartAgent(message['from'])
    except Exception as e:
        print(str(e))
        traceback.print_exc(file=sys.stdout)


def getComputerByMac( mac):
    ret = Glpi().getMachineByMacAddress('imaging_module', mac)
    if type(ret) == list:
        if len(ret) != 0:
            return ret[0]
        else:
            return None
    return ret

def getMachineByUuidSetup( uuidsetupmachine):
    if uuidsetupmachine is None or uuidsetupmachine == "":
        logger.warning("Setup uuid machine missing in inventory xmpp")
        return {}
    machine_result=Glpi().getMachineByUuidSetup(uuidsetupmachine)
    if machine_result:
        logger.debug("machine for setup uuid machine %s" %machine_result)
    return machine_result

def XmppUpdateInventoried(jid, machine):
    """ search id glpi for machine
        search on uuid setup machine is exist.
        if not exit search on macadress """
    logger.debug("** function XmppUpdateInventoried")


    if machine['uuid_serial_machine'] is not None and \
        machine['uuid_serial_machine'] != "":
        # search on uuid setup

        setupuuid = getMachineByUuidSetup(machine['uuid_serial_machine'])
        if setupuuid:
            logger.debug("** search id glpi on uuid setup machine %s" % machine['uuid_serial_machine'])
            uuid = 'UUID' + str(setupuuid['id'])
            if machine['uuid_inventorymachine'] == uuid:
                logger.debug("correct uuid_inventorymachine " \
                    "in table machine id(%s) uuid_inventorymachine(%s)" %  (machine['id'],
                                                                            machine['uuid_inventorymachine']))
                return True
            XmppMasterDatabase().replace_Organization_ad_id_inventory(machine['id'],
                                                                              uuid)
            XmppMasterDatabase().updateMachineidinventory(uuid, machine['id'])
            logger.debug("** update uuid inventory (%s) for machine %s" % (uuid, machine['id']))
            return True
    # update on mac address
    try:
        result = XmppMasterDatabase().listMacAdressforMachine(machine['id'])
        results = result[0].split(",")
        logger.debug("listMacAdressforMachine   %s" % results)
        uuid = ''
        for t in results:
            logger.debug("Processing mac address %s" % t)
            computer = getComputerByMac(t)
            if computer is not None:
                logger.debug("computer find %s for mac adress %s" % (computer.id,t))
                uuid = 'UUID' + str(computer.id)
                if machine['uuid_inventorymachine'] != uuid :
                    XmppMasterDatabase().replace_Organization_ad_id_inventory(machine['uuid_inventorymachine'],
                                                                              uuid)
                    logger.debug("** Update in Organization_ad uuid %s to %s " % (machine['uuid_inventorymachine'],
                                                                                  uuid))
                    logger.debug("** Update uuid inventory %s to %s" % ( uuid, machine['jid']))
                    XmppMasterDatabase().updateMachineidinventory(uuid, machine['id'])
                else:
                    logger.debug("uuid inventory correct in base")
                return True

    except KeyError:
        logger.error("An error occurred on machine %s and we did not receive any inventory,"
                     "make sure fusioninventory is running correctly" % machine)
    except Exception:
        logger.error("** Update error on inventory %s\n%s" % (jid, traceback.format_exc()))
    return False
