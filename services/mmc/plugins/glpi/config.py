#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id: database.py 168 2008-07-09 09:53:32Z oroussy $
#
# This file is part of MMC.
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from mmc.support.config import PluginConfig

from ConfigParser import NoOptionError
import logging

class GlpiConfig(PluginConfig):
    dbpoolrecycle = 60
    dbpoolsize = 5
    dbport = None
    dbsslenable = False

    check_db_enable = False
    check_db_interval = 300

    filter_on = None

    # state section
    orange = 10
    red = 35

    # computer_list section
    # complete list: ['cn', 'description', 'os', 'type', 'user', 'inventorynumber', 'state', 'entity', 'location', 'model', 'manufacturer']
    summary = ['cn', 'description', 'os', 'type', 'user', 'owner', 'entity', 'location']
    ordered = False

    # antivirus section
    av_false_positive = []

    # manufacturer section
    manufacturerWarrantyUrl = {}
    webservices = {
        'purge_machine': 0
    }

    def readConf(self):
        self.dbdriver = self.get("main", "dbdriver")
        self.dbhost = self.get("main", "dbhost")
        self.dbname = self.get("main", "dbname")
        self.dbuser = self.get("main", "dbuser")
        self.dbpasswd = self.getpassword("main", "dbpasswd")

        if self.has_option("main", "dbsslenable"):
            self.dbsslenable = self.getboolean("main", "dbsslenable")
            if self.dbsslenable:
                self.dbsslca = self.get("main", "dbsslca")
                self.dbsslcert = self.get("main", "dbsslcert")
                self.dbsslkey = self.get("main", "dbsslkey")

        if self.has_option("main", "check_db_enable"):
            self.check_db_enable = self.getboolean("main", "check_db_enable")
        if self.has_option("main", "check_db_interval"):
            self.check_db_interval = self.getint("main", "check_db_interval")

        self.disable = self.getint("main", "disable")
        self.displayLocalisationBar = self.getboolean("main", "localisation")
        try:
            self.glpi_computer_uri = self.get("main", "glpi_computer_uri")
        except:
            self.glpi_computer_uri = "" # http://localhost/glpi/front/computer.form.php?id="
        try:
            self.activeProfiles = self.get('main', 'active_profiles').split(' ')
        except NoOptionError:
            # put the GLPI default values for actives profiles
            self.activeProfiles = ['Super-Admin', 'Admin', 'Supervisor', 'Technician']
        for option in ["dbport", "dbpoolrecycle", "dbpoolsize"]:
            try:
                self.__dict__[option] = self.getint("main", option)
            except NoOptionError:
                pass

        if self.has_option("main", "filter_on"):
            self.filter_on = self._parse_filter_on(self.get("main", "filter_on"))

        if self.has_option("state", "orange"):
            self.orange = self.getint("state", "orange")
        if self.has_option("state", "red"):
            self.red = self.getint("state", "red")

        if self.has_option("computer_list", "summary"):
            self.summary = self.get("computer_list", "summary").split(' ')

        if self.has_option("antivirus", "av_false_positive"):
            self.av_false_positive = self.get("antivirus", "av_false_positive").split('||')

        if self.has_option("computer_list", "ordered"):
            self.ordered = self.getint("computer_list", "ordered")

        if self.has_option("webservices", "purge_machine"):
            self.webservices['purge_machine'] = self.getint("webservices", "purge_machine")

        if self.has_option("webservices", "glpi_base_url"):
            self.webservices['glpi_base_url'] = self.get("webservices", "glpi_base_url")

        if self.has_option("webservices", "glpi_username"):
            self.webservices['glpi_username'] = self.get("webservices", "glpi_username")

        if self.has_option("webservices", "glpi_password"):
            self.webservices['glpi_password'] = self.get("webservices", "glpi_password")

        # associate manufacturer's names to their warranty url
        # manufacturer must have same key in 'manufacturer' and 'manufacturer_warranty_url' sections
        # for adding its warranty url
        self.manufacturerWarranty = {}
        if 'manufacturers' in self.sections():
            logging.getLogger().debug('[GLPI] Get manufacturers and their warranty infos')
            for manufacturer_key in self.options('manufacturers'):
                if self.has_section('manufacturer_' + manufacturer_key) and self.has_option('manufacturer_' + manufacturer_key, 'url'):
                    try:
                        type = self.get('manufacturer_' + manufacturer_key, 'type')
                    except NoOptionError:
                        type = "get"
                    try:
                        params = self.get('manufacturer_' + manufacturer_key, 'params')
                    except NoOptionError:
                        params = ""
                    self.manufacturerWarranty[manufacturer_key] = {'names': self.get('manufacturers', manufacturer_key).split('||'),
                                                                   'type': type,
                                                                   'url': self.get('manufacturer_' + manufacturer_key, 'url'),
                                                                   'params': params}
            logging.getLogger().debug(self.manufacturerWarranty)

    def _parse_filter_on(self, value):
        """
        Parsing of customized filters.

        Returned value will be parsed as a dictionnary with list of values
        for each filter.

        @param value: raw string
        @type value: str

        @return: dictionnary of filters
        @rtype: dict
        """
        try:
            couples = [f.split("=") for f in value.split(" ")]

            filters = dict([(key, values.split("|")) for (key, values) in couples])
            logging.getLogger().debug("will filter machines on %s" % (str(filters)))
            return filters

        except Exception, e:
            logging.getLogger().warn("Parsing on filter_on failed: %s" % str(e))
            return None



class GlpiQueryManagerConfig(PluginConfig):
    activate = False

    def readConf(self):
        PluginConfig.readConf(self)
        if self.has_section('querymanager'):
            self.activate = self.getboolean("querymanager", "activate")

