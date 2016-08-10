# -*- coding: utf-8 -*-
import json

from lib.utils import  simplecommandestr, simplecommande
import sys, os, platform
from  lib.utils import pulginprocess

#from  lib.utils import file_get_content, file_put_content, typelinux, servicelinuxinit, isprogramme, simplecommande, simplecommandestr, CreateWinUser


plugin={"VERSION": "1.0", "NAME" :"filetransfert"}

@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur, result):
    print "plugin filetransfert"
    print data
    #part = 0
    #result['data']['end'] = False
    #result['base64'] = True
    #result['data']['namefiledest'] = data['namefiledest']
    #f = open( data['namesource'], "rb")
    #try:
        #while True:
            #result['data']['part'] = 0
            #result['data']['data'] = f.read(1024)
            #if bytes == "":
                #break;
            #else:
                #objetxmpp.send_message( mto=message['from'],
                                        #mbody=base64.b64encode(json.dumps(result['data'])),
                                        #mtype='chat')
                #part = part + 1
    #except IOError:
        #dataerreur['data']['data'] =''
        #dataerreur['data']['msg'] = "ERROR : relayserver  must is linux"
        #dataerreur['ret'] = 255
        #dataerreur['data']['end'] = False
        #dataerreur['data']['namefiledest']=result['data']['namefiledest']
        #raise
    #finally:
        #result['data']['end'] = True
        #f.close()
