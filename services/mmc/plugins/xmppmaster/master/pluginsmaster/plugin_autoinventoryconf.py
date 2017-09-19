# -*- coding: utf-8 -*-
from mmc.plugins.glpi.database import Glpi
from mmc.plugins.xmppmaster.config import xmppMasterConfig
import hashlib
from pulse2.database.xmppmaster import XmppMasterDatabase
import logging
import traceback
import sys

# Plugin for configuring glpi database for holding the registry keys
# and for configuring the machine agent for inventory


def action( xmppobject ):
    logging.debug("Plugin Master inventoryconf")

    try:
        # read max_key_index parameter to find out the number of keys
        if hasattr(xmppobject.config, 'max_key_index'):
            logging.debug("Loading %s keys" % xmppobject.config.max_key_index)
            nb_iter = int(xmppobject.config.max_key_index) + 1
            for num in range(1,nb_iter):
                registry_key = getattr(xmppobject.config, 'reg_key_' + str(num))
                # Check that the keys are in glpi and insert them if not present
                if not Glpi().getRegistryCollect(registry_key):
                    Glpi().addRegistryCollect(registry_key)
    except Exception, e:
        logging.error("Error loading plugin: %s" % str(e))
        traceback.print_exc(file=sys.stdout)
