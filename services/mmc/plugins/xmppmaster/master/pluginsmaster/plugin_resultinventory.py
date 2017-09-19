# -*- coding: utf-8 -*-
import zlib, base64
import traceback
import os,sys
import urllib2
import time
import json
import logging
from mmc.plugins.glpi.database import Glpi
from pulse2.database.xmppmaster import XmppMasterDatabase



def action( xmppobject, action, sessionid, data, message, ret, objsessiondata):
    HEADER = {"Pragma": "no-cache",
              "User-Agent": "Proxy:FusionInventory/Pulse2/GLPI",
              "Content-Type": "application/x-compress",
             }
    try:
        logging.getLogger().debug("plugin_resultinventory")
        print os.environ
        print message['from']
        # send inventory to inventory server
        try:
            url = xmppobject.config.inventory_url
        except:
            url = "http://localhost:9999/"
        inventory = zlib.decompress(base64.b64decode(data['inventory']))
        request = urllib2.Request(url, inventory, HEADER)
        response = urllib2.urlopen(request)
        time.sleep(5)
        # save registry inventory
        try:
            reginventory = json.loads(base64.b64decode(data['reginventory']))
        except:
            reginventory = False
        if reginventory:
            computers_id = XmppMasterDatabase().getUuidFromJid(message['from'])
            logging.getLogger().debug("Computers ID: %s" % computers_id)
            nb_iter = int(reginventory['info']['max_key_index']) + 1
            for num in range(1,nb_iter):
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
                    Glpi().addRegistryCollectContent(computers_id, registry_id, key_name, reg_key_value)
                except Exception, e:
                    logging.getLogger().debug("Error getting key: %s" % reg_key)
                    pass
        # restart agent
        xmppobject.restartAgent(message['from'])
    except Exception, e:
        print str(e)
        traceback.print_exc(file=sys.stdout)
