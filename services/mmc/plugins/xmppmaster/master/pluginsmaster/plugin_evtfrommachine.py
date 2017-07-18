# -*- coding: utf-8; -*-

import logging

plugin = { "VERSION" : "1.0", "NAME" : "evtfrommachine", "TYPE" : "master" }


def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    logging.getLogger().debug(plugin)
    if data['event'] == "SHUTDOWN_EVENT":
        msg_changed_status = {
            "from" : data['machine'],
            "type" : 'unavailable'
            }
        xmppobject.changed_status(msg_changed_status)
