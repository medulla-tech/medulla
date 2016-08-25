# -*- coding: utf-8 -*-
#import base64
#import json
#import subprocess
import sys, os



plugin={"VERSION": "1.0", "NAME" :"installplugin","TYPE":"all"}

def action( objetxmpp, action, sessionid, data, message, dataerreur ):
    if action == 'installplugin':
        if len(data) != 0 :
            pl = sys.platform
            if pl.startswith('win'):
                data = data.replace("\n","\r\n");
            elif pl.startswith('linux'):
                pass
            else:
                pass
            namefile =  os.path.join(objetxmpp.config.pathplugins,data['pluginname'])
            try:
                fileplugin = open(namefile, "w")                                     
                fileplugin.write(str(data['datafile']))
                fileplugin.close()
            except :
                print "erreur ecriture fichier"
                return
            msg = "install plugin %s on %s"%(data['pluginname'],message['to'].user)
            objetxmpp.loginformation(msg)
