# -*- coding: utf-8 -*-
import traceback
import sys
from pulse2.database.xmppmaster import XmppMasterDatabase

def action( objetxmpp, action, sessionid, data, message, ret, objsessiondata):
    print "plugin_resultguacamole : %s"%data
    try:
        XmppMasterDatabase().addlistguacamoleidforiventoryid(data['uuid'], data['connection'])
    except Exception, e:
        print "Error: %s" % str(e)
        traceback.print_exc(file=sys.stdout)
