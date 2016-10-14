# -*- coding: utf-8; -*-
import base64, json, os

#plugin_resultwakeonLan
def action( objetxmpp, action, sessionid, data, message, ret, dataobj):
    print "plugin_resultwakeonLan"
    try:
        print data
    except Exception as e:
        print "ERREUR DANS PLUGINS %s : %s"%(action, str(e))
 
