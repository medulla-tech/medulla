# SPDX-FileCopyrightText: 2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module to link entities to users depending on their profile.
"""

import os.path
import imp

from mmc.plugins.base.provisioning import ProvisionerConfig, ProvisionerI
from pulse2.database.inventory import Inventory
from mmc.support.mmctools import getConfigFile


class InventoryProvisionerConfig(ProvisionerConfig):
    def readConf(self):
        ProvisionerConfig.readConf(self)
        if self.has_option(self.section, "profile_attr"):
            self.profileAttr = self.get(self.section, "profile_attr")
            PROFILEENTITY = "profile_entity_"
            for option in self.options(self.section):
                if option.startswith(PROFILEENTITY):
                    self.profilesEntity[option.replace(PROFILEENTITY, "").lower()] = (
                        self.get(self.section, option)
                    )

    def setDefault(self):
        ProvisionerConfig.setDefault(self)
        self.profileAttr = None
        self.profilesEntity = {}


class InventoryProvisioner(ProvisionerI):
    """
    This provisionner updates user / entities mapping in the inventory
    database.
    """

    def __init__(self, conffile=None, name="inventory"):
        if not conffile:
            conffile = getConfigFile(name)
        ProvisionerI.__init__(self, conffile, name, InventoryProvisionerConfig)

    def validate(self):
        Inventory()
        return True

    def doProvisioning(self, authtoken):
        userentry = authtoken.getInfos()[1]
        uid = authtoken.getLogin()
        if self.config.profileAttr and self.config.profilesEntity:
            try:
                profile = userentry[self.config.profileAttr][0].lower()
            except KeyError:
                self.logger.info(
                    "No profile information for user '%s' in attribute %s"
                    % (uid, self.config.profileAttr)
                )
                profile = ""
            profile = profile.strip()
            try:
                entities = self.config.profilesEntity[profile].split()
            except KeyError:
                if "default" in self.config.profilesEntity:
                    entities = self.config.profilesEntity["default"].split()
                    self.logger.info("Set the default profile to user.")
                    profile = "default"
                else:
                    self.logger.info(
                        "No entity defined in configuration file for profile '%s'"
                        % profile
                    )
                    self.logger.info("Setting user's entity to empty")
                    entities = []
            if profile and entities:
                tmp = []
                for entity in entities:
                    if entity.startswith("%") and entity.endswith("%"):
                        attr = entity.strip("%")
                        if attr in userentry:
                            tmp.extend(userentry[attr])
                        else:
                            self.logger.info(
                                "The user '%s' doesn't have an attribute '%s'"
                                % (uid, attr)
                            )
                    elif entity.startswith("plugin:"):
                        plugin = entity.replace("plugin:", "")
                        searchpath = os.path.join(
                            os.path.dirname(__file__), "provisioning_plugins"
                        )
                        try:
                            f, p, d = imp.find_module(plugin, [searchpath])
                            mod = imp.load_module(plugin, f, p, d)
                            klass = mod.PluginEntities
                            found = klass().get(authtoken)
                            if found:
                                self.logger.info(
                                    "Plugin '%s' found these entities: %s"
                                    % (plugin, found)
                                )
                            else:
                                self.logger.info(
                                    "Plugin '%s' found no matching entity" % plugin
                                )
                            tmp.extend(found)
                        except ImportError:
                            self.logger.error(
                                "The plugin '%s' can't be imported" % plugin
                            )
                        except Exception as e:
                            self.logger.error(
                                "Error while using the plugin '%s'" % plugin
                            )
                            self.logger.exception(e)
                    else:
                        tmp.append(entity)
                entities = tmp[:]
                self.logger.info(
                    "Setting user '%s' entities corresponding to user profile '%s': %s"
                    % (uid, profile, str(entities))
                )
            Inventory().setUserEntities(uid, entities)
