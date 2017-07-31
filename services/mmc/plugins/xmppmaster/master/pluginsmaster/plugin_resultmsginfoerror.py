# -*- coding: utf-8; -*-

DEBUGPULSEPLUGIN = 25
plugin = { "VERSION" : "1.0", "NAME" : "resultmsginfoerror", "TYPE" : "master" }

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    if 'msg' in data:
        print "Error plugin : %s"%data['msg']
    pass
