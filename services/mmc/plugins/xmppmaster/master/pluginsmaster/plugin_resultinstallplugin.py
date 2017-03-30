# -*- coding: utf-8; -*-


def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    try:
       print "plugin resultinstallplugin from %s  ret [%s]"%(message['from'], ret)
    except Exception as e:
        print "Error in plugin resultinstallplugin %s"%str(e)
