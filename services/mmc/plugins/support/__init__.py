# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2014 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

""" Product manager plugin base """

import logging

from pulse2.version import getVersion, getRevision # pyflakes.ignore
from mmc.support.mmctools import SingletonN
from mmc.core.tasks import TaskManager

from mmc.plugins.dashboard.manager import DashboardManager
from mmc.plugins.support.config import SupportConfig
from mmc.plugins.support.panel import RemoteSupportPanel, LicensePanel
from mmc.plugins.support.process import TunnelBuilder
from mmc.plugins.support.jsonquery import Query

APIVERSION = "0:1:0"
NAME = "support"

def getApiVersion(): return APIVERSION


def activate():
    config = SupportConfig(NAME)
    if config.disabled:
        logging.getLogger().warning("Plugin Support: disabled by configuration.")
        return False

    DM = DashboardManager()
    DM.register_panel(RemoteSupportPanel("remotesupport"))
    DM.register_panel(license_panel)

    TaskManager().addTask("support.get_license_info",
                          (LicenseChecker().get_license_info,),
                          cron_expression=config.cron_search_for_updates
                          )

    LicenseChecker().get_license_info()

    return True

class LicenseChecker(object):
    """
    Periodical checks to license server.

    This checks are triggered by cron and returned and parsed data
    updates the license widget on dashboard.
    """
    __metaclass__ = SingletonN


    def get_license_info(self, offline=False):
        """
        Checks the license info on license server.

        @param offline: temp file check only
        @type offline: bool

        @return: True when successfull query and data parse
        @rtype: Deferred
        """

        logging.getLogger().info("Plugin Support: checking the license info on %s/%s/pulse/country=%s" % (
            config.license_server_url,
            config.install_uuid,
            config.country)
        )

        query = Query(config.license_server_url,
                      config.install_uuid,
                      config.license_tmp_file,
                      config.country
                      )

        d = query.get(offline)
        d.addCallback(self.data_extract)
        d.addErrback(self.eb_get_info)
        d.addCallback(self.update_panel)

        return d


    def data_extract(self, response):
        """
        Custom corrections to display the license info.

        @param data: decoded data returned from license server
        @type data: list

        @return: transformed data
        @rtype: dict
        """
        # -------------------
        # format of response:
        # -------------------
        #  [{"name": "Support - Niveau 1/2",
        #         "country": "FR",
        #          "data": {"hours": "De 7h \u00e0 18h, les jours ouvr\u00e9s.",
        #                   "phone": "+33 12 13 14 15 23",
        #                   "email": "support-fr@mandriva.com",
        #                   "links": [
        #                            {
        #                             "url": "http://hot-line.com",
        #                             "text": "Hot-line Form",
        #                             },
        #                            {
        #                             "url": "http://example.com",
        #                             "text": "Acheter une license"
        #                             },
        #                            ]
        #                   }
        #         },
        #        {"name": "Unterstützung - Ebene 1/2",
        #         "country": "DE",
        #         "data": {"hours": "Von 8 bis 18",
        #                  "phone": "+31 452 144 254",
        #                  "email": "support-de@mandriva.com"
        #                   }
        #         }]
        #
        # -----------------------
        # will be transformed to:
        # -----------------------
        #  {"name": "Support - Niveau 1/2",
        #   "country": "FR",
        #   "hours": "De 7h \u00e0 18h, les jours ouvr\u00e9s.",
        #   "phone": "+33 12 13 14 15 23",
        #   "email": "support-fr@mandriva.com"
        #   }

        if not isinstance(response, list):
            logging.getLogger().warning("No license data; widget will not be updated.")
            return None

        data = None
        for pack in response:
            if "country" in pack:
                if pack["country"] == config.country:
                    data = pack
                    break

        if not data:
            logging.getLogger().warning("No license data for country '%s'; widget will not be updated." % config.country)
            return None

        if not "data" in data:
            logging.getLogger().warning("No license data")
            return None

        for key in ["phone", "email", "hours", "links"]:
            if key in data["data"]:
                data[key] = data["data"][key]

        if "phone" in data:
            data["phone_uri"] = "tel:%s" % data["phone"].replace(".", "")\
                                       .replace("-", "").replace(" ", "")

        if "email" in data:
            data["email_uri"] = "mailto:%s?subject=%s" % (data["email"], config.install_uuid)


        del data["data"]

        return self.normalize(data)

    def normalize(self, data):
        """
        Converts all elements with unicode escape characters to unicode chars.

        Includes also nested lists containing another dicts.

        @param data: extracted response from the license server
        @type data: dict

        @return: converted data
        @rtype: dict
        """
        for key, value in data.items():
            if isinstance(value, unicode):
                data[key] = value.decode("unicode-escape")
            elif isinstance(value, list):
                lst = []
                for sub_data in value:
                    lst.append(self.normalize(sub_data))
                data[key] = lst
            else:
                data[key] = value
        return data


    def eb_get_info(self, failure):
        """ Common errorback for querying and parsing """
        logging.getLogger().warning("License check failed: %s" % failure)
        return False


    def update_panel(self, data):
        """
        Updates the license widget for dashboard.

        @param data: parsed data ready for widget display
        @type data: dict
        """
        if not data:
            return False
        license_panel.data_handler(data)
        return True



config = SupportConfig(NAME)
builder = TunnelBuilder(config)

license_panel = LicensePanel("license")


def open():
    return builder.open()

def close():
    return builder.close()

def established():
    return builder.established

def get_port():
    return builder.port

def get_subscription_info():
    try:
        from mmc.plugins.pulse2.inventory import getSubscriptionInfo
        return getSubscriptionInfo()
    except ImportError:
        return False






