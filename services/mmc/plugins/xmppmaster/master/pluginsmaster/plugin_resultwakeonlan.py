# -*- coding: utf-8; -*-
import base64, json, os

#plugin_resultwakeonLan
def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    print "plugin_resultwakeonLan"
    try:
        print data
    except Exception as e:
        print "Error in plugin %s : %s"%(action, str(e))
