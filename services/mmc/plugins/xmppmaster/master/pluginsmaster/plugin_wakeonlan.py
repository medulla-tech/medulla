# -*- coding: utf-8; -*-
import base64, json, os, sys
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
import traceback
from utils import name_random

# plugin run wake on lan on mac adress

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    print "call master plugin Master wakeonlan"

    try:
        listserverrelay = XmppMasterDatabase().listserverrelay()
        if 'macadress' in data:
            senddataplugin = {'action' : 'wakeonLan',
                            'sessionid': name_random(5, "wakeonLan"),
                            'data' : {'macaddress': data['macadress'] }}
            for serverrelay in listserverrelay:
                xmppobject.send_message(  mto = serverrelay[0],
                                    mbody = json.dumps(senddataplugin, encoding='latin1'),
                                    mtype = 'chat')
        elif 'UUID' in data:
            listadressmacs = Glpi().getMachineMac(data['UUID'])
            for macadress in listadressmacs:
                if macadress == '00:00:00:00:00:00':
                    continue
                senddataplugin = {'action' : 'wakeonLan',
                                  'sessionid': name_random(5, "wakeonLan"),
                                  'data' : {'macaddress': macadress }}
                for serverrelay in listserverrelay:
                    xmppobject.send_message( mto = serverrelay[0],
                                             mbody = json.dumps(senddataplugin, encoding='latin1'),
                                             mtype = 'chat')
        else:
            raise

    except:
        print "error plugin plugin_wakeonlan %s"%data
        traceback.print_exc(file=sys.stdout)
