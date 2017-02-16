# -*- coding: utf-8; -*-

import json
import logging
import traceback
import sys

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    try:
        if ret == 0:
            ###logging.getLogger().debug("deploiement session %s success"% sessionid)
            logging.getLogger().debug("Succes deploy on %s Package : %s Session : %s"%( data['jidmachine'],
                                                                                        data['descriptor']['info']['name'],
                                                                                        sessionid))
            #logging.getLogger().debug("%s"%json.dumps(data, indent=4, sort_keys=True))
        else:
            logging.getLogger().error("Error deploy on %s Package : %s Session : %s"%(  data['jidmachine'],
                                                                                        data['descriptor']['info']['name'],
                                                                                        sessionid))
            #logging.getLogger().error("%s"%json.dumps(data, indent=4, sort_keys=True))
    except:
        traceback.print_exc(file=sys.stdout)

