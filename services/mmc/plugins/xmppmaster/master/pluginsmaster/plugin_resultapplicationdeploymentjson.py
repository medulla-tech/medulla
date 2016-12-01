# -*- coding: utf-8; -*-

import json
import logging
import traceback


def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    try:
        if ret == 0:
            logging.getLogger().debug("deploiement session %s success"% sessionid)
        else:
            logging.getLogger().debug("deploiement session %s error"% sessionid)
            
        print json.dumps(data, indent=4, sort_keys=True)

        #logging.getLogger().debug("deploiement packages :  %s\n%s"%( data['descriptor']['info']['name'],data['descriptor']['info']['description']))
        ## logging.getLogger().debug("environ: \n %s"%( data['environ'))
        ##logging.getLogger().debug("environ: \n %s"%(data['environ'))
        #logging.getLogger().debug("sequence %s "% json.dumps(data['descriptor']['sequence'], indent=4, sort_keys=False))
        #logging.getLogger().debug("deploiement packages %s"% json.dumps(data, indent=4, sort_keys=False) )
    except:
        traceback.print_exc(file=sys.stdout)
