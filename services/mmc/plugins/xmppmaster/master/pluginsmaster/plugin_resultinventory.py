# -*- coding: utf-8 -*-
import zlib
import base64
import traceback
import os
import sys
import urllib2
import time
import json
import logging
from mmc.plugins.glpi.database import Glpi
from pulse2.database.xmppmaster import XmppMasterDatabase
from utils import file_put_contents

plugin = {"VERSION": "1.2", "NAME": "resultinventory", "TYPE": "master"}


def action(xmppobject, action, sessionid, data, message, ret, objsessiondata):
    HEADER = {"Pragma": "no-cache",
              "User-Agent": "Proxy:FusionInventory/Pulse2/GLPI",
              "Content-Type": "application/x-compress",
              }
    try:
        logging.getLogger().debug("=====================================================")
        logging.getLogger().debug(plugin)
        logging.getLogger().debug("=====================================================")

        if not 'inventorylistage' in xmppobject.config.__dict__:
            xmppobject.config.__dict__['inventorylistage'] = False
        else:
            if isinstance(xmppobject.config.__dict__['inventorylistage'], basestring):
                if xmppobject.config.__dict__['inventorylistage'].lower() == "true" or\
                    xmppobject.config.__dict__['inventorylistage'].lower() == "1" or\
                        xmppobject.config.__dict__['inventorylistage'].lower() == "yes":
                    xmppobject.config.__dict__['inventorylistage'] = True
                else:
                    xmppobject.config.__dict__['inventorylistage'] = False

        # Directory inventaire.
        RecvInventory = os.path.abspath(  os.path.join( os.path.dirname( __file__), "..", "RecvInventory"))
        if not os.path.exists(RecvInventory):
            os.makedirs( RecvInventory, 0755 )

        try:
            url = xmppobject.config.inventory_url
        except:
            url = "http://localhost:9999/"

        inventory = zlib.decompress(base64.b64decode(data['inventory']))

        if xmppobject.config.inventorylistage:
            # copy fichier to
            namefile = os.path.join(RecvInventory, "%s_%s.xml"%(time.time(), message['from'].user))

            file_put_contents(namefile,  inventory)
        else:
            request = urllib2.Request(url, inventory, HEADER)
            response = urllib2.urlopen(request)
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
        if not xmppobject.config.inventorylistage:
            timedata = 6
        else:
            timedata = 20
        time.sleep(timedata)

        if not xmppobject.XmppUpdateInventoried(message['from']):
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
                except Exception, e:
                    logging.getLogger().debug("Error getting key: %s" % reg_key)
                    pass
        time.sleep(25)
        # restart agent
        # xmppobject.restartAgent(message['from'])
    except Exception, e:
        print str(e)
        traceback.print_exc(file=sys.stdout)
