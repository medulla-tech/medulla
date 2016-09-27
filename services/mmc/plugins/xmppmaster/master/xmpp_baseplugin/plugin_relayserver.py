# -*- coding: utf-8 -*-
import json

from lib.utils import  simplecommandestr, simplecommande
import sys, os, platform
from  lib.utils import pulginprocess
from lxml import etree


plugin={"VERSION": "1.0", "NAME" : "relayserver", "TYPE" : "relayserver"}
# ce plugin install la configuration de guacamole sur server relais.
# When using guacamole-auth-noauth, you have to logout of Guacamole (or clear cookies, etc.)
# for changes to noauth-config.xml to take effect.
def xmlgeneration(nameconfig, protocol, hostname, port):
    """
        #<config name="myconfig" protocol="rdp">
            #<param name="hostname" value="rdp-server" />
            #<param name="port" value="3389" />
        #</config>
    """
    CONFIG =  etree.Element('config')
    #CONFIG.text = 
    CONFIG.set('name', nameconfig)
    CONFIG.set('protocol', protocol)
    HOSTNAME = etree.SubElement(CONFIG,'param')
    #QUERY.text = 'INVENTORY'
    HOSTNAME.set('name', 'hostname')
    HOSTNAME.set('value', hostname)
    PORT = etree.SubElement(CONFIG,'param')
    PORT.set('name', 'port')
    PORT.set('value', str(port))
    return etree.tostring(CONFIG, pretty_print=True)


@pulginprocess
def action( objetxmpp, action, sessionid, data, message, dataerreur,result):
    #try :
        #from  fichierdecomf import fileconf
    #except:
        #dataerreur['ret']=255
        #dataerreur['data']['msg'] = "ERROR : relayserver verify execution from relayserver"
        #raise 
    if sys.platform.startswith('linux'):
        # write config to /etc/guacamole/noauth-config.xml
        #print "%s"% json.dumps(data[0], indent=4, sort_keys=True)
        xml=""
        protocolewindows = {'rdp': 3389,'ssh':22}
        protocolelinux   = {'VNC': 5900, 'ssh':22}
        for donnees in data:
            if donnees['os']=="Linux":
                for prot,po in protocolelinux.iteritems():
                    xml = xml + xmlgeneration(donnees['hostname'], prot, donnees['xmppip'], po)
        try:
            with open("/etc/guacamole/noauth-config.xml", 'w') as file:
                file.write('<configs>\n')
                file.write(xml)
                file.write('</configs>\n')
        except IOError:
            dataerreur['data']['msg'] = "ERROR : write file /etc/guacamole/noauth-config.xml"   
            dataerreur['ret']=255
            raise
        result['data']['msg'] = "install configuration guacamole"
        result['data']['info'] = data
        result['base64'] = False
    else:
        dataerreur['data']['msg'] = "ERROR : relayserver plugin must be running on Linux"
        dataerreur['ret']=255
        raise
