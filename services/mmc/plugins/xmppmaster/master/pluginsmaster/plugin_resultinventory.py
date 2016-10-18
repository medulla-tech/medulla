# -*- coding: utf-8 -*-
import zlib, base64
import traceback
import os,sys
import urllib2
import time
def action( objetxmpp, action, sessionid, data, message, ret, objsessiondata):
    HEADER = {"Pragma": "no-cache",
              "User-Agent": "Proxy:FusionInventory/Pulse2/GLPI",
              "Content-Type": "application/x-compress",
             }
    try:
        print os.environ
        print "plugin_resultinventory"
        print message['from']
        url = "http://localhost:9999/"
        inventory = zlib.decompress(base64.b64decode(data['inventory']))
        request = urllib2.Request(url, inventory, HEADER)
        response = urllib2.urlopen(request)
        time.sleep(5)
        objetxmpp.restartagent(message['from'])
    except Exception, e:
        print str(e)
        traceback.print_exc(file=sys.stdout)
