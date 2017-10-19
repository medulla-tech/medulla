# -*- coding: utf-8; -*-
import base64, json, os, sys
from pulse2.database.xmppmaster import XmppMasterDatabase
from mmc.plugins.glpi.database import Glpi
import traceback
from utils import name_random

# plugin run wake on lan on mac adress

def action( xmppobject, action, sessionid, data, message, ret, dataobj):
    print "call master plugin Master wakeonlan"
    
    
    
    sessionid = name_random(5, "wakeonlan")
    
    try:
        listserverrelay = XmppMasterDatabase().listserverrelay()
        if 'macadress' in data:
            senddataplugin = {'action' : 'wakeonlan',
                            'sessionid': sessionid,
                            'data' : {'macaddress': data['macadress'] }}
            for serverrelay in listserverrelay:
                xmppobject.send_message(  mto = serverrelay[0],
                                    mbody = json.dumps(senddataplugin, encoding='latin1'),
                                    mtype = 'chat')
                xmppobject.xmpplog("ARS %s : WOL for macadress %s"%(serverrelay[0], data['macadress']),
                                        type = 'deploy',
                                        sessionname = sessionid,
                                        priority =-1,
                                        action = "",
                                        who = "",
                                        how = "",
                                        why = xmppobject.boundjid.bare,
                                        module = "Wol | Start | Creation",
                                        date = None ,
                                        fromuser = xmppobject.boundjid.bare,
                                        touser = "")
        elif 'UUID' in data:
            listadressmacs = Glpi().getMachineMac(data['UUID'])
            for macadress in listadressmacs:
                if macadress == '00:00:00:00:00:00':
                    continue
                senddataplugin = {'action' : 'wakeonlan',
                                  'sessionid': sessionid,
                                  'data' : {'macaddress': macadress }}
                for serverrelay in listserverrelay:
                    xmppobject.send_message( mto = serverrelay[0],
                                             mbody = json.dumps(senddataplugin, encoding='latin1'),
                                             mtype = 'chat')
                    xmppobject.xmpplog("ARS %s : WOL for macadress %s"%(serverrelay[0], macadress ),
                                        type = 'deploy',
                                        sessionname = sessionid,
                                        priority =-1,
                                        action = "",
                                        who = "",
                                        how = "",
                                        why = xmppobject.boundjid.bare,
                                        module = "Wol | Start | Creation",
                                        date = None ,
                                        fromuser = xmppobject.boundjid.bare,
                                        touser = "")
        else:
            raise

    except:
        print "error plugin plugin_wakeonlan %s"%data
        traceback.print_exc(file=sys.stdout)
