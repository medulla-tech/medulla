# -*- coding: utf-8; -*-


def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    print "plugin_resultreverse_ssh_on"
    print "%s from %s"%(data['msg'],message['from'])
