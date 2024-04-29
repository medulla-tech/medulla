# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import json
import os
import logging
import traceback
import types
import configparser
import hashlib
from mmc.plugins.xmppmaster.master.lib.utils import file_get_contents, name_random
from medulla.database.xmppmaster import XmppMasterDatabase
from manage_grafana import manage_grafana

logger = logging.getLogger()
DEBUGPULSEPLUGIN = 25

# this plugin is called at agent start

plugin = {"VERSION": "1.1", "NAME": "loadmonitoringconfig", "TYPE": "master"}


def action(objectxmpp, action, sessionid, data, msg, dataerreur):
    logger.debug("=====================================================")
    logger.debug("call %s from %s" % (plugin, msg["from"]))
    logger.debug("=====================================================")

    callcounter = getattr(objectxmpp, "num_call%s" % action)
    if callcounter == 0:
        read_conf_load_plugin_monitoring_version_config(objectxmpp)


def read_conf_load_plugin_monitoring_version_config(objectxmpp):
    """
    reads the plugin config
    """
    conffilename = plugin["NAME"] + ".ini"
    pathfileconf = os.path.join(objectxmpp.config.pathdirconffile, conffilename)

    defautconf = "/var/lib/medulla/xmpp_monitoring/confagent/monitoring_config.ini"
    if not os.path.isfile(pathfileconf):
        logger.error(
            "plugin %s\nConfiguration file missing\n  %s\neg conf:"
            "\n[parameters]\nmonitoring_agent_config_file = %s"
            % (plugin["NAME"], pathfileconf, defautconf)
        )
        logger.warning(
            "Default value for monitoring_agent_config_file is %s" % defautconf
        )
        objectxmpp.monitoring_agent_config_file = defautconf
    else:
        Config = configparser.ConfigParser()
        Config.read(pathfileconf)
        if os.path.exists(pathfileconf + ".local"):
            Config.read(pathfileconf + ".local")
        objectxmpp.monitoring_agent_config_file = defautconf
        if Config.has_option("parameters", "monitoring_agent_config_file"):
            objectxmpp.monitoring_agent_config_file = Config.get(
                "parameters", "monitoring_agent_config_file"
            )
    logger.debug(
        "Monitoring agent config file is %s" % objectxmpp.monitoring_agent_config_file
    )

    ## function defined dynamically
    objectxmpp.plugin_loadmonitoringconfig = types.MethodType(
        plugin_loadmonitoringconfig, objectxmpp
    )
    objectxmpp.monitoring_agent_config_file_md5 = ""
    objectxmpp.monitoring_agent_config_file_content = ""
    if objectxmpp.monitoring_agent_config_file != "" and os.path.exists(
        objectxmpp.monitoring_agent_config_file
    ):
        content = file_get_contents(objectxmpp.monitoring_agent_config_file)

        logger.debug(
            "monitoring_agent_config_file %s "
            % (objectxmpp.monitoring_agent_config_file)
        )
        logger.debug("content %s " % (content))

        objectxmpp.monitoring_agent_config_file_md5 = hashlib.md5(content).hexdigest()
        objectxmpp.monitoring_agent_config_file_content = base64.b64encode(content)
        logger.debug(
            "monitoring_agent_config_file_content %s "
            % (objectxmpp.monitoring_agent_config_file_content)
        )
        logger.debug(
            "md5 file %s is %s"
            % (
                objectxmpp.monitoring_agent_config_file,
                objectxmpp.monitoring_agent_config_file_md5,
            )
        )


def plugin_loadmonitoringconfig(self, msg, data):
    """
    This function is used load the configuration of the plugin. We also update
    it if needed.

    Args:
        msg: informations from where and to who goes the messages.
        data: XMPP messages sent to the plugin

    """
    try:
        if data["agenttype"] in ["relayserver"]:
            logger.warning("ARS monitoring_agent_config_file does not exist")
            return

        initialisation_graph(self, msg, data)

        if self.monitoring_agent_config_file_md5 == "":
            logger.warning(
                "file %s not defined or non-existent md5"
                % self.monitoring_agent_config_file
            )
            return

        if "md5_conf_monitoring" not in data:
            logger.warning("md5_conf_monitoring missing from agent %s " % (msg["from"]))
            return

        logger.debug(
            "monitoring_agent_config_file_md5 %s "
            % (self.monitoring_agent_config_file_md5)
        )
        logger.debug(
            "self.monitoring_agent_config_file_content %s "
            % (self.monitoring_agent_config_file_content)
        )
        logger.debug("data['md5_conf_monitoring'] %s " % (data["md5_conf_monitoring"]))
        if "md5_conf_monitoring" in data:
            if (
                data["md5_conf_monitoring"] != self.monitoring_agent_config_file_md5
                and self.monitoring_agent_config_file_content != ""
            ):
                # Insall config file, create configuration message and send
                fichierdata = {
                    "action": "installconfmonitoring",
                    "base64": False,
                    "sessionid": name_random(5, pref="confmonitoring"),
                    "data": {
                        "pluginname": "monitoring_config_file",
                        "content": self.monitoring_agent_config_file_content,
                    },
                }

                logger.debug(
                    "The new configuration is %s :"
                    % (json.dumps(fichierdata, indent=4))
                )
                try:
                    self.send_message(
                        mto=msg["from"], mbody=json.dumps(fichierdata), mtype="chat"
                    )
                except Exception as e:
                    logger.debug(
                        "Error creating configuration message for "
                        "plugin %s: %s" % (plugin["NAME"], str(e))
                    )
                    logger.error("\n%s" % (traceback.format_exc()))
    except Exception as e:
        logger.debug("Plugin %s : %s" % (plugin["NAME"], str(e)))
        logger.error("\n%s" % (traceback.format_exc()))


def initialisation_graph(objectxmpp, msg, data):
    try:
        hostname = str(msg["from"]).split(".", 1)[0]
    except Exception:
        logger.error(
            "Could not get hostname from jid %s\n%s"
            % (msg["from"], traceback.format_exc())
        )
        return
    # on recupere la liste des template
    listtemplate = XmppMasterDatabase().getMonitoring_panels_template(status=True)
    # pour chaque panel on applique les parametres.
    for graphe_init in listtemplate:
        try:
            if manage_grafana(hostname).grafanaGetPanelIdFromTitle(
                graphe_init["name_graphe"]
            ):
                logger.debug("graphe %s for machine %s always exist")
                continue
            parameters = {}
            try:
                parameters = json.loads(graphe_init["parameters"])
            except Exception:
                logger.error(
                    "voir parameters in format "
                    "string json.\n%s" % traceback.format_exc()
                )
            parameters["@_hostname_@"] = hostname
            parameters["@_type_graphe_@"] = graphe_init["type_graphe"]
            parameters["@_name_graphe_@"] = graphe_init["name_graphe"]
            logger.warning("parameters  %s" % parameters)
            for keyreplace in parameters:
                graphe_init["template_json"] = graphe_init["template_json"].replace(
                    keyreplace, parameters[keyreplace]
                )

            manage_grafana(hostname).grafanaEditPanel(graphe_init["template_json"])

        except Exception:
            logger.error(
                "Could not configure %s panel"
                " for %s\n%s"
                % (graphe_init["name_graphe"], hostname, traceback.format_exc())
            )
