# -*- coding: utf-8; -*-

import logging

plugin = { "VERSION" : "1.0", "NAME" : "evtfrommachine", "TYPE" : "master" }

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("Pulgin %s %version"%(plugin))
    try:
        logging.getLogger().debug("EVENT %s on Machine %s"%( data['event'], data['machine']))
    except Exception as e:
        logging.getLogger().error("Plugin %s %version\nerror %s"%(plugin,str(e)))

