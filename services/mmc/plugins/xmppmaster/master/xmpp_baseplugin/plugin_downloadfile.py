# -*- coding: utf-8; -*-
import json
import base64
import zlib
import hashlib
from lib.utils import  simplecommandestr, simplecommande, md5
import sys, os, platform
from  lib.utils import pulginprocess
from lib.managesession import sessiondatainfo, session
#from  lib.utils import file_get_content, file_put_content, typelinux, servicelinuxinit, isprogramme, simplecommande, simplecommandestr, CreateWinUser


plugin={"VERSION": "1.1", "NAME" :"downloadfile","TYPE":"all"}
@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur, result):
    try:
        if not objetxmpp.session.isexist(sessionid):
            objetxmpp.event("pluginaction", { 'action': action,
                                         'sessionid': sessionid,
                                         'status': 'start', 
                                         'to' : message['from'],
                                         'form' : message['to'] ,
                                         'file' : data['namesource']})
            datasession={
                            'fichier' : data['namesource'], 
                            'pointeurfichier' : 0 ,
                            'part' : 0
                            }
            objetxmpp.session.createsessiondatainfo(sessionid, datasession, 10)
        else:
            objetxmpp.session.reactualisesession(sessionid)

        sessiondata = objetxmpp.session.sessionfromsessiondata(sessionid)
        pointeur = sessiondata.getdatasession()['pointeurfichier']
        namefile = sessiondata.getdatasession()['fichier']
        result['part'] =  sessiondata.getdatasession()['part']
        try:
            f = open( namefile, "rb")
            f.seek(pointeur, 0)
            buffer = f.read(25000)
            result['trame']= hashlib.md5(buffer).hexdigest()
            pointeur = f.tell()
        except IOError:
            objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'error',
                            'msgerror' : "IOError ERROR on file %s"%namefile,
                            'size' : sessiondata.getdatasession()['pointeurfichier'],
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' : namefile})
            dataerreur['data']['msg'] = "IOError ERROR on file %s"%namefile
            dataerreur['ret'] = 255
            dataerreur['end'] = False
            raise
        finally:
            f.close()
        result['end'] = False
        if len(buffer) == 0 or buffer == "":
            result['end'] = True
            result['data'] = ""
            result['md5'] = md5(namefile)
            objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'finished', 
                            'success': True,
                            'size' : sessiondata.getdatasession()['pointeurfichier'],
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' : namefile})
            objetxmpp.session.clear(sessionid)
            return
        else:
            aaa = zlib.compress(buffer)
            result['data'] = base64.b64encode(aaa)
            objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'process',
                            'size' : pointeur,
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' : namefile})

        sessiondata.datasession['pointeurfichier'] = pointeur
        sessiondata.datasession['part'] = result['part'] + 1
        objetxmpp.session.affiche()

    except Exception as e:
        objetxmpp.event("pluginaction", { 'action': action,
                            'sessionid': sessionid,
                            'status': 'error',
                            'msgerror' : str(e),
                            'size' : sessiondata.getdatasession()['pointeurfichier'],
                            'to' : message['from'],
                            'form' : message['to'] ,
                            'file' : namefile})
        dataerreur['data']['msg'] = str(e)
        dataerreur['ret'] = 255
        dataerreur['end'] = False
        raise
