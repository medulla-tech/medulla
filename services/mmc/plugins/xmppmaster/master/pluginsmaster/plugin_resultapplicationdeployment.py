 
# -*- coding: utf-8; -*-


def action( objetxmpp, action, sessionid, data, message, ret, dataobj):
    print "plugin_resultapplicationdeployment"
    print "%s from %s"%(data['msg'],message['from'])