# -*- coding: utf-8 -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# file : xmppmaster/master/pluginsmaster/plugin_loadpluginlistversion.py
import base64
import json
import sys, os
import logging
import platform
from utils import file_get_contents, \
                      getRandomName, \
                      data_struct_message, \
                      add_method
import traceback
from sleekxmpp import jid
import ConfigParser
from ConfigParser import  NoOptionError, NoSectionError
import types

from pulse2.database.xmppmaster import XmppMasterDatabase
logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25

# this plugin calling to starting agent

plugin = {"VERSION" : "1.1", "NAME" : "loadpluginlistversion", "TYPE" : "master", "LOAD" : "START" }

def action( objectxmpp, action, sessionid, data, msg, dataerreur):
    logger.debug("=====================================================")
    logger.debug("call %s from %s"%(plugin, msg['from']))
    logger.debug("=====================================================")
    #lit fichiers de configuration pour le plugin si pas charge.
    
    compteurcallplugin = getattr(objectxmpp, "num_call%s"%action)

    if compteurcallplugin == 0:
        read_conf_load_plugin_list_version(objectxmpp)
        objectxmpp.schedule('updatelistplugin',
                            900,
                            objectxmpp.loadPluginList,
                            repeat=True)
    logger.debug("%s"%hasattr(objectxmpp, "loadPluginList"))
    objectxmpp.loadPluginList()

def read_conf_load_plugin_list_version(objectxmpp):
    """
        lit la configuration du plugin
        le repertoire ou doit se trouver le fichier de configuration est dans la variable objectxmpp.config.pathdirconffile
    """
    objectxmpp.config_loadpluginlistversion = True

    namefichierconf = plugin['NAME'] + ".ini"
    pathfileconf = os.path.join( objectxmpp.config.pathdirconffile, namefichierconf )
    if not os.path.isfile(pathfileconf):
        logger.error("plugin %s\nConfiguration file  missing\n  %s" \
            "\neg conf:\n[parameters]\ndirpluginlist = /var/lib/pulse2/xmpp_baseplugin/"%(plugin['NAME'], pathfileconf))

        logger.warning("default value for dirplugins is /var/lib/pulse2/xmpp_baseplugin/")
        objectxmpp.dirpluginlist = "/var/lib/pulse2/xmpp_baseplugin/"
    else:
        Config = ConfigParser.ConfigParser()
        Config.read(pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")
        objectxmpp.dirpluginlist = "/var/lib/pulse2/xmpp_baseplugin/"
        if Config.has_option("parameters", "dirpluginlist"):
            objectxmpp.dirpluginlist = Config.get('parameters', 'dirpluginlist')
    # loadPluginList function definie dynamiquement
    objectxmpp.file_deploy_plugin = []
    objectxmpp.loadPluginList = types.MethodType(loadPluginList, objectxmpp)
    ##objectxmpp.restartmachineasynchrone = types.MethodType(restartmachineasynchrone, objectxmpp)
    #objectxmpp.restartAgent = types.MethodType(restartAgent, objectxmpp)
    objectxmpp.remoteinstallPlugin = types.MethodType(remoteinstallPlugin, objectxmpp)
    objectxmpp.deployPlugin = types.MethodType(deployPlugin, objectxmpp)
    objectxmpp.plugin_loadpluginlistversion = types.MethodType(plugin_loadpluginlistversion, objectxmpp)

def loadPluginList(self):
    """ charges les informations des plugins 'nom plugins et version' pour
        faire la comparaison avec les plugin sur les machines.
    """
    logger.debug("Load and Verify base plugin")
    self.plugindata = {}
    self.plugintype = {}
    for element in [x for x in os.listdir(self.dirpluginlist) if x[-3:] == ".py" and x[:7] == "plugin_"]:
        element_name = os.path.join(self.dirpluginlist, element)
        # verify syntax error for plugin python
        # we do not deploy a plugin with syntax error.
        if os.system("python -m py_compile \"%s\"" % element_name) == 0:
            f = open(element_name, 'r')
            lignes = f.readlines()
            f.close()
            for ligne in lignes:
                if 'VERSION' in ligne and 'NAME' in ligne:
                    l = ligne.split("=")
                    plugin = eval(l[1])
                    self.plugindata[plugin['NAME']] = plugin['VERSION']
                    try:
                        self.plugintype[plugin['NAME']] = plugin['TYPE']
                    except:
                        self.plugintype[plugin['NAME']] = "machine"
                    break
        else:
            logger.error("As long as the ERROR SYNTAX is not fixed, the plugin [%s] is ignored." % os.path.join(
                self.dirpluginlist, element))

def remoteinstallPlugin(self):
    """
        This function installs the plugins to agent M and RS
    """
    restart_machine = set()
    for indexplugin in range(0, len(self.file_deploy_plugin)):
        plugmachine = self.file_deploy_plugin.pop(0)
        if XmppMasterDatabase().getPresencejid(plugmachine['dest']):
            if plugmachine['type'] == 'deployPlugin':
                logger.debug("install plugin normal %s to %s" %
                                (plugmachine['plugin'], plugmachine['dest']))
                self.deployPlugin(plugmachine['dest'], plugmachine['plugin'])
                restart_machine.add(plugmachine['dest'])
            elif plugmachine['type'] == 'deploySchedulingPlugin':
                # It is the updating code for the scheduling plugins.
                pass
    for jidmachine in restart_machine:  # Itération pour chaque élément
        # call one function by message to processing asynchronous tasks and can add a tempo on restart action.
        self.event('restartmachineasynchrone', jidmachine)

def deployPlugin(self, jid, plugin):
        content = ''
        fichierdata = {}
        namefile = os.path.join(self.dirpluginlist, "plugin_%s.py" % plugin)
        if os.path.isfile(namefile):
            logger.debug("File plugin found %s" % namefile)
        else:
            logger.error("File plugin found %s" % namefile)
            return
        try:
            fileplugin = open(namefile, "rb")
            content = fileplugin.read()
            fileplugin.close()
        except:
            logger.error("File read error\n%s"%(traceback.format_exc()))
            return
        fichierdata['action'] = 'installplugin'
        fichierdata['data'] = {}
        dd = {}
        dd['datafile'] = content
        dd['pluginname'] = "plugin_%s.py" % plugin
        fichierdata['data'] = base64.b64encode(json.dumps(dd))
        fichierdata['sessionid'] = "sans"
        fichierdata['base64'] = True
        try:
            self.send_message(mto=jid,
                              mbody=json.dumps(fichierdata),
                              mtype='chat')
        except:
            logger.error("\n%s"%(traceback.format_exc()))

def plugin_loadpluginlistversion(self, msg, data):
    #logger.info(json.dumps(data['plugin'], indent = 4))
    #function de rappel dans boucle de message.
    #cette function est definie dans l'instance mucbot, si on veut quel soit utiliser dans un autre plugin.
    # Show plugins information logs
    restartAgent = False
    for k, v in self.plugindata.iteritems():
        deploy = False
        try:
            # Check version
            if data['plugin'][k] != v:
                deploy = True
        except:
            deploy = True
        if data['agenttype'] != "all":
            if data['agenttype'] == "relayserver" and self.plugintype[k] == 'machine':
                deploy = False
            if data['agenttype'] == "machine" and self.plugintype[k] == 'relayserver':
                deploy = False
        if deploy:
            try:
                logger.info("update %s version %s to version %s on Agent " % (k,
                                                                              data['plugin'][k],
                                                                              v))
            except KeyError:
                logger.info("install %s version %s to version on Agent " % (k,v))
            self.file_deploy_plugin.append(
                {'dest': msg['from'], 'plugin': k, 'type': 'deployPlugin'})
            #return True
    self.remoteinstallPlugin()
