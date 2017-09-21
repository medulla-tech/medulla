# -*- coding: utf-8; -*-
import json
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
from utils import name_random

# plugin run guacamole

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    print "call master plugin Master guacamole"

    try:
        relayserver = XmppMasterDatabase().getRelayServerForMachineUuid(data['uuid'])
        jidmachine = XmppMasterDatabase().getjidMachinefromuuid(data['uuid'])
        senddataplugin = {'action' : 'guacamole',
                          'sessionid': name_random(5, "guacamole"),
                          'data' : {'jidmachine': jidmachine, 'cux_id': data['cux_id'], 'cux_type': data['cux_type'], 'uuid': data['uuid'] }}
        xmppobject.send_message( mto = relayserver['jid'],
                                 mbody = json.dumps(senddataplugin, encoding='latin1'),
                                 mtype = 'chat')

    except:
        print "error plugin plugin_guacamole %s"%data
        traceback.print_exc(file=sys.stdout)
