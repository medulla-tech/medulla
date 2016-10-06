# -*- coding: utf-8; -*-
import base64, json, os, sys
from pulse2.database.xmppmaster import XmppMasterDatabase
import traceback
from utils import name_random
#plugin_masterwakeonLan
def action( objetxmpp, action, sessionid, data, message, ret, dataobj):
    print "kkkkkkkkkkkkkkk"
    #try:
    print data
    #except Exception as e:
        #print "ERREUR DANS PLUGINS %s : %s"%(action, str(e))
    try:
            listserverrelais = XmppMasterDatabase().listserverrelay()
            senddataplugin = {'action' : 'wakeonLan',
                            'sessionid': name_random(5, "wakeonLan"),
                            'data' : {'macaddress': data['macadress'] }}
            for serverrelais in listserverrelais:
                objetxmpp.send_message(  mto = serverrelais[0],
                                    mbody = json.dumps(senddataplugin, encoding='latin1'),
                                    mtype = 'chat')
    except:
        traceback.print_exc(file=sys.stdout)


