# -*- coding: utf-8; -*-
#from utils import pulginmaster, pulginmastersessionaction
import base64
import json
import os
#import zlib
#from utils import affichedatajson
import utils

#import hashlib
#from lib.managepackage import managepackage
import pprint

def action( objetxmpp, action, sessionid, data, message, ret, dataobj):
    try:
        if 'typequery' in  data:
            if data['typequery'] == 'TED':
                print "efface session %s"%sessionid
                #passer deploiement a done dans base
                objetxmpp.session.clear(sessionid)
                
            elif  data['typequery'] == 'TE':
                # clear session
                objetxmpp.session.clear(sessionid)
                #passer deploiement a error dans base
            else:
                # mettre à jour session avec data
                objetxmpp.session.sessionsetdata(sessionid, data)
    except Exception as e:
        print "ERREUR DANS PLUGINS%s"%str(e)
