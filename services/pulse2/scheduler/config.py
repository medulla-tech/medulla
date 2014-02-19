# -*- coding: utf-8; -*-
#
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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

"""
Parse the scheduler configuration file
"""

# Misc
import re           # for re.compil
import pwd          # for getpwnam
import grp          # for getgrpnam
import string       # for atoi
import logging      # logging stuff
import os.path      # for file checking

from mmc.site import mmcconfdir

# Others Pulse2 Stuff
import pulse2.utils
from pulse2.utils import SingletonN
from pulse2.network import PreferredNetworkParser
from pulse2.xmlrpc import isTwistedEnoughForLoginPass
from pulse2.database.msc.config import MscDatabaseConfig

log = logging.getLogger()

class SchedulerDatabaseConfig(MscDatabaseConfig):
    dbname = "msc"
    dbsection = "database"

    def __setup_fallback(self, mscconffile):
        log.info("Reading configuration file (database config): %s" % mscconffile)
        self.dbsection = "msc"
        MscDatabaseConfig.setup(self, mscconffile)

    def setup(self, conffile):
        mscconffile = pulse2.utils.getConfigFile("msc")
        if os.path.exists(conffile):
            try:
                log.info("Trying to read configuration file (database config): %s" % conffile)
                MscDatabaseConfig.setup(self, conffile)
            except Exception, e:
                log.warn("Configuration file: %s does not contain any database config : %s" % (conffile, e))
                self.__setup_fallback(mscconffile)
            if not self.cp.has_section("database"):
                log.warn("Configuration file: %s does not contain any database config" % conffile)
                self.__setup_fallback(mscconffile)
        elif os.path.exists(mscconffile):
            self.__setup_fallback(mscconffile)
        else:
            raise Exception("can find any config file")

class SchedulerConfig(object):
    __metaclass__ = SingletonN
    """
    Singleton Class to hold configuration directives

    """
    name = None
    cp = None

    # [scheduler] section default values
    announce_check = dict()
    awake_time = 5
    cacert = mmcconfdir + "/pulse2/scheduler/keys/cacert.pem"
    client_check = None
    dbencoding = 'utf-8'
    enablessl = True
    emitting_period = .1
    proxy_buffer_period = .1
    proxy_buffer_start_delay = 4
    initial_wait = 2
    localcert = mmcconfdir + "/pulse2/scheduler/keys/privkey.pem"
    host = "127.0.0.1"
    max_command_time = 3600
    max_threads = 20
    non_fatal_steps = []
    max_upload_time = 21600
    max_wol_time = 300
    mode = 'async'
    password = 'password'
    port = 8000
    resolv_order = ['fqdn', 'shortname', 'netbios', 'ip', 'first']
    preferred_network = [(None, None)]
    netbios_path = "/usr/bin/nmblookup"
    scheduler_path = '/usr/sbin/pulse2-scheduler'
    scheduler_proxy_path = '/usr/sbin/pulse2-scheduler-proxy'
    scheduler_proxy_socket_path = '/var/run/pulse2/scheduler-proxy.sock'
    scheduler_proxy_buffer_tmp = '/tmp/pulse2-scheduler-proxy.buff.tmp'
    server_check = None
    username = 'username'
    verifypeer = False
    cache_size = 300
    cache_timeout = 500
    imaging = False
    max_to_overtimed = 1000

    # [daemon] section
    daemon_group = 0
    pid_path = "/var/run/pulse2"
    umask = 0077
    daemon_user = 0
    setrlimit = ''

    mmc_agent = {}

    # [launcher_xxx] section
    launchers = {
    }

    launchers_uri = {}
    launchers_networks = {}
    def setoption(self, section, key, attrib, type = 'str'):
        if type == 'str':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.get(section, key))
                log.debug("scheduler %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
            else:
                log.debug("scheduler %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'bool':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getboolean(section, key))
                log.debug("scheduler %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                log.debug("scheduler %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        if type == 'int':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getint(section, key))
                log.debug("scheduler %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                log.debug("scheduler %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'pass':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getpassword(section, key))
                log.debug("scheduler %s: section %s, option %s set using given value" % (self.name, section, key))
            else:
                log.debug("scheduler %s: section %s, option %s not set, using default value" % (self.name, section, key))

    def presetup(self, config_file):
        """
            used to pre-parse conf file to gather enough data to setuid() soon
        """
        self.cp = pulse2.utils.Pulse2ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option("daemon", "user"):
            self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
        if self.cp.has_option("daemon", "group"):
            self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
        if self.cp.has_option("daemon", "umask"):
            self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)
        if self.cp.has_option("handler_hand01", "args"):
            self.logdir = os.path.dirname(re.compile("['|\"]").split(self.cp.get("handler_hand01", "args"))[1])
        if self.cp.has_option("daemon", "setrlimit"):
            self.setrlimit = self.cp.get("daemon", "setrlimit")

    def setup(self, config_file):
        # Load configuration file
        if not self.cp: # self.cp is set if presetup() was already called
            self.presetup(config_file)

        # [scheduler] section parsing
        self.name = self.cp.get("scheduler", "id")

        self.setoption("scheduler", "awake_time", "awake_time", 'int')
        self.setoption("scheduler", "initial_wait", "initial_wait", 'int')
        self.setoption("scheduler", "emitting_period", "emitting_period", 'float')
        self.setoption("scheduler", "proxy_buffer_period", "proxy_buffer_period", 'float')
        self.setoption("scheduler", "proxy_buffer_start_delay", "proxy_buffer_start_delay", 'int')

        # cache settings
        self.setoption("scheduler", "cache_size", "cache_size", 'int')
        self.setoption("scheduler", "cache_timeout", "cache_timeout", 'int')

        self.setoption("scheduler", "max_command_time", "max_command_time", 'int')
        self.setoption("scheduler", "max_upload_time", "max_upload_time", 'int')
        self.setoption("scheduler", "max_wol_time", "max_wol_time", 'int')
        self.setoption("scheduler", "dbencoding", "dbencoding")
        self.setoption("scheduler", "enablessl", "enablessl", 'bool')
        self.setoption("scheduler", "max_threads", "max_threads", 'int')

        self.setoption("scheduler", "imaging", "imaging", 'bool')
        self.setoption("scheduler", "max_to_overtimed", "max_to_overtimed", 'int')

        if self.cp.has_option("scheduler", "non_fatal_steps"):
            self.non_fatal_steps = self.cp.get("scheduler", "non_fatal_steps").split(' ')
            log.debug("scheduler %s: section %s, option %s set to '%s'" % (self.name, "scheduler", "non_fatal_steps", self.non_fatal_steps))
        else:
            log.debug("scheduler %s: section %s, option %s not set, using default value '%s'" % (self.name, "scheduler", "non_fatal_steps", self.non_fatal_steps))


        if self.enablessl:
            if self.cp.has_option("scheduler", "privkey"):
                self.localcert = self.cp.get("scheduler", "privkey")
            if self.cp.has_option("scheduler", "localcert"):
                self.localcert = self.cp.get("scheduler", "localcert")
            if self.cp.has_option("scheduler", "certfile"):
                self.cacert = self.cp.get("scheduler", "certfile")
            if self.cp.has_option("scheduler", "cacert"):
                self.cacert = self.cp.get("scheduler", "cacert")
            if self.cp.has_option("scheduler", "verifypeer"):
                self.verifypeer = self.cp.getboolean("scheduler", "verifypeer")
            if not os.path.isfile(self.localcert):
                raise Exception('scheduler "%s": can\'t read SSL key "%s"' % (self.name, self.localcert))
                return False
            if not os.path.isfile(self.cacert):
                raise Exception('scheduler "%s": can\'t read SSL certificate "%s"' % (self.name, self.cacert))
                return False
            if self.verifypeer: # we need twisted.internet.ssl.Certificate to activate certs
                import twisted.internet.ssl
                if not hasattr(twisted.internet.ssl, "Certificate"):
                    raise Exception('scheduler "%s": I need at least Python Twisted 2.5 to handle peer checking' % (self.name))
                    return False

        if self.cp.has_option("scheduler", "listen"): # TODO remove in a future version
            log.warning("'listen' is obsolete, please replace it in your config file by 'host'")
            self.setoption("scheduler", "listen", "host")
        else:
            self.setoption("scheduler", "host", "host")
        self.setoption("scheduler", "port", "port")
        self.port = int(self.port)
        self.setoption("scheduler", "username", "username")
        self.setoption("scheduler", "password", "password", 'pass')
        if not isTwistedEnoughForLoginPass():
            if self.username != '':
                if self.username != 'username':
                    log.warning("your version of twisted is not high enough to use login (scheduler/username)")
                self.username = ''
            if self.password != '':
                if self.password != 'password':
                    log.warning("your version of twisted is not high enough to use password (scheduler/password)")
                self.password = ''

        self.setoption("scheduler", "mode", "mode")
        self.setoption("scheduler", "resolv_order", "resolv_order")
        if not type(self.resolv_order) == type([]):
            self.resolv_order = self.resolv_order.split(' ')

        pnp = PreferredNetworkParser(None, None)
        if self.cp.has_option("scheduler", "preferred_network"):
            self.preferred_network = pnp.parse(self.cp.get("scheduler", "preferred_network"))
        else :
            self.preferred_network = pnp.get_default()


        self.setoption("scheduler", "netbios_path", "netbios_path")
        self.setoption("scheduler", "scheduler_path", "scheduler_path")
        self.setoption("scheduler", "scheduler_proxy_path", "scheduler_proxy_path")

        if self.cp.has_option("scheduler", "scheduler_proxy_socket_path"):
            self.scheduler_proxy_socket_path = self.cp.get("scheduler", "scheduler_proxy_socket_path")
        if self.cp.has_option("scheduler", "scheduler_proxy_buffer_tmp"):
            self.scheduler_proxy_buffer_tmp = self.cp.get("scheduler", "scheduler_proxy_buffer_tmp")


        if self.cp.has_option("scheduler", "client_check"):
            self.client_check = {}
            for token in self.cp.get("scheduler", "client_check").split(','):
                (key, val) = token.split('=')
                self.client_check[key] = val
            log.info("scheduler %s: section %s, option %s set using given value" % (self.name, 'client_check', self.client_check))
        if self.cp.has_option("scheduler", "server_check"):
            self.server_check = {}
            for token in self.cp.get("scheduler", "server_check").split(','):
                (key, val) = token.split('=')
                self.server_check[key] = val
            log.info("scheduler %s: section %s, option %s set using given value" % (self.name, 'server_check', self.server_check))
        if self.cp.has_option("scheduler", "announce_check"):
            self.announce_check = {}
            for token in self.cp.get("scheduler", "announce_check").split(','):
                (key, val) = token.split('=')
                self.announce_check[key] = val
            log.info("scheduler %s: section %s, option %s set using given value" % (self.name, 'server_check', self.server_check))

        # [daemon] section parsing (parsing ofr user, group, and umask is done above in presetup)
        if self.cp.has_section("daemon"):
            if self.cp.has_option('daemon', 'pid_path'):
                log.warning("'pid_path' is deprecated, please replace it in your config file by 'pidfile'")
                self.setoption('daemon', 'pid_path', 'pid_path')
            else:
                self.setoption('daemon', 'pidfile', 'pid_path')

        # [mmc_agent] section parsing
        self.mmc_agent = {}
        if self.cp.has_section("mmc_agent"):
            self.mmc_agent = {
                'host' : "127.0.0.1",
                'port' : 7080,
                'username' : 'mmc',
                'password' : 's3cr3t',
                'enablessl' : True,
                'verifypeer' : False,
                'cacert' : mmcconfdir + "/pulse2/scheduler/keys/cacert.pem",
                'localcert' : mmcconfdir + "/pulse2/scheduler/keys/privkey.pem"}
            if self.cp.has_option('mmc_agent', 'host'):
                self.mmc_agent['host'] = self.cp.get('mmc_agent', 'host')
            if self.cp.has_option('mmc_agent', 'port'):
                self.mmc_agent['port'] = self.cp.getint('mmc_agent', 'port')
            if self.cp.has_option('mmc_agent', 'enablessl'):
                self.mmc_agent['enablessl'] = self.cp.getboolean('mmc_agent', 'enablessl')
            if self.cp.has_option('mmc_agent', 'verifypeer'):
                self.mmc_agent['verifypeer'] = self.cp.getboolean('mmc_agent', 'verifypeer')
            if self.cp.has_option('mmc_agent', 'cacert'):
                self.mmc_agent['cacert'] = self.cp.get('mmc_agent', 'cacert')
            if self.cp.has_option('mmc_agent', 'localcert'):
                self.mmc_agent['localcert'] = self.cp.get('mmc_agent', 'localcert')
            if self.mmc_agent['enablessl']:
                if not os.path.isfile(self.mmc_agent['localcert']):
                    raise Exception('can\'t read SSL key "%s"' % (self.mmc_agent['localcert']))
                    return False
                if not os.path.isfile(self.mmc_agent['cacert']):
                    raise Exception('can\'t read SSL certificate "%s"' % (self.mmc_agent['cacert']))
                    return False
                if self.mmc_agent['verifypeer']:  # we need twisted.internet.ssl.Certificate to activate certs
                    import twisted.internet.ssl
                    if not hasattr(twisted.internet.ssl, "Certificate"):
                        raise Exception('I need at least Python Twisted 2.5 to handle peer checking')
                        return False

        # [launcher_xxx] section parsing
        for section in self.cp.sections():
            if re.compile("^launcher_[0-9]+$").match(section):
                username = self.cp.get(section, "username")
                password = self.cp.getpassword(section, "password")
                if not isTwistedEnoughForLoginPass():
                    if username != '':
                        log.warning("your version of twisted is not high enough to use login (%s/username)"%(section))
                        username = ''
                    if password != '':
                        log.warning("your version of twisted is not high enough to use password (%s/password)"%(section))
                        password = ''

                if self.cp.has_option(section, "slots"):
                    slots = self.cp.getint(section, "slots")
                else:
                    slots = 20

                self.launchers[section] = {
                        'enablessl': self.cp.getboolean(section, "enablessl"),
                        'host': self.cp.get(section, "host"),
                        'username': username,
                        'password': password,
                        'port': self.cp.get(section, "port"),
                        'slots': slots,
                    }
                if self.launchers[section]["enablessl"]:
                    uri = "https://"
                else:
                    uri = 'http://'
                if self.launchers[section]['username'] != '':
                    uri += '%s:%s@' % (self.launchers[section]['username'], self.launchers[section]['password'])
                uri += '%s:%d' % (self.launchers[section]['host'], int(self.launchers[section]['port']))
                self.launchers_uri.update({section: uri})

                pnp = PreferredNetworkParser(None, None)
                if self.cp.has_option(section, "preferred_network"):
                    _networks = pnp.parse(self.cp.get(section, "preferred_network"))
                else :
                    _networks = pnp.get_default()
                self.launchers_networks.update({section: _networks})




