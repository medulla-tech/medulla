# -*- coding: utf-8; -*-

import logging

plugin = { "VERSION" : "1.0", "NAME" : "resultenddeploy", "TYPE" : "master" }

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug("Pulgin %s %version %s"%(plugin['NAME'], plugin['VERSION']))
    
