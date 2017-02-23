# -*- coding: utf-8 -*-
import zlib, base64
import traceback
import os,sys
import urllib2
import time
import json
from mmc.plugins.glpi.database import Glpi
from pulse2.database.xmppmaster import XmppMasterDatabase

def action( xmppobject, action, sessionid, data, message, ret, objsessiondata):
    HEADER = {"Pragma": "no-cache",
              "User-Agent": "Proxy:FusionInventory/Pulse2/GLPI",
              "Content-Type": "application/x-compress",
             }
    try:
        print os.environ
        print "plugin_resultinventory : %s"%data
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
            print "computers_id: %s" % computers_id
            nb_iter = int(reginventory['info']['max_key_index']) + 1
            for num in range(1,nb_iter):
                reg_key_num = 'reg_key_'+str(num)
                reg_key = reginventory[reg_key_num]['key'].strip('"')
                reg_key_value = reginventory[reg_key_num]['value'].strip('"')
                key_name = reg_key.split('\\')[-1]
                print "reg_key_num: %s" % reg_key_num
                print "reg_key: %s" % reg_key
                print "reg_key_value: %s" % reg_key_value
                print "key_name: %s" % key_name
                registry_id = Glpi().getRegistryCollect(reg_key)
                print "registry_id: %s" % registry_id
                Glpi().addRegistryCollectContent(computers_id, registry_id, key_name, reg_key_value)
        # restart agent
        xmppobject.restartAgent(message['from'])
    except Exception, e:
        print str(e)
        traceback.print_exc(file=sys.stdout)
