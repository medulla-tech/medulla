#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

from mmc.plugins.glpi.database import Glpi
import logging
import traceback
import sys


plugin = {"VERSION": "1.1", "NAME": "autoinventoryconf", "TYPE": "master"}
# Plugin for configuring glpi database for holding the registry keys
# and for configuring the machine agent for inventory


def action(xmppobject):
    logging.getLogger().debug(plugin)
    try:
        # read max_key_index parameter to find out the number of keys
        if hasattr(xmppobject.config, "max_key_index"):
            logging.getLogger().debug(
                "Loading %s keys" % xmppobject.config.max_key_index
            )
            nb_iter = int(xmppobject.config.max_key_index) + 1
            for num in range(1, nb_iter):
                registry_key = getattr(xmppobject.config, "reg_key_" + str(num)).split(
                    "|"
                )[0]
                try:
                    registry_key_name = getattr(
                        xmppobject.config, "reg_key_" + str(num)
                    ).split("|")[1]
                except IndexError:
                    registry_key_name = getattr(
                        xmppobject.config, "reg_key_" + str(num)
                    ).split("\\")[-1]
                # Check that the keys are in glpi and insert them if not present
                if not Glpi().getRegistryCollect(registry_key):
                    Glpi().addRegistryCollect(registry_key, registry_key_name)
        pass
    except Exception as e:
        logging.getLogger().error("Error loading plugin: %s" % str(e))
        traceback.print_exc(file=sys.stdout)
        pass
