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
Pulse 2 launcher configuration class
"""

# Misc
import ConfigParser
import re           # fo re.compil
import pwd          # for getpwnam
import grp          # for getgrpnam
import string       # for atoi
import logging      # logging stuff
import os
import stat         # for owner checking

# Others Pulse2 Stuff
import pulse2.utils
from pulse2.xmlrpc import isTwistedEnoughForLoginPass

log = logging.getLogger()

class LauncherConfig(pulse2.utils.Singleton):
    """
    Singleton Class to hold configuration directives

    """
    name = None
    cp = None

    # launchers section
    halt_command = "/bin/shutdown.exe -f -s 1 || shutdown -h now"
    inventory_command = '''export P2SRV=`echo $SSH_CONNECTION | cut -f1 -d\ `; export P2PORT=9999; export http_proxy=""; export ftp_proxy=""; ( [ -x /cygdrive/c/Program\ Files/FusionInventory-Agent/uninstFI.exe ] && /cygdrive/c/Program\ Files/FusionInventory-Agent/perl/bin/perl "C:\Program Files\FusionInventory-Agent\perl\\bin\\fusioninventory-agent" /server=http://$P2SRV:$P2PORT ) || ( [ -x /cygdrive/c/Program\ Files\ \(x86\)/FusionInventory-Agent/uninstFI.exe ] && /cygdrive/c/Program\ Files\ \(x86\)/FusionInventory-Agent/perl/bin/perl "C:\Program Files (x86)\FusionInventory-Agent\perl\\bin\\fusioninventory-agent" /server=http://$P2SRV:$P2PORT ) || ( [ -x /cygdrive/c/Program\ Files/FusionInventory-Agent/fusioninventory-agent.bat ] && /cygdrive/c/Program\ Files/FusionInventory-Agent/fusioninventory-agent.bat /server=http://$P2SRV:$P2PORT ) || ( [ -x /cygdrive/c/Program\ Files\ \(x86\)/FusionInventory-Agent/fusioninventory-agent.bat ] && /cygdrive/c/Program\ Files\ \(x86\)/FusionInventory-Agent/fusioninventory-agent.bat /server=http://$P2SRV:$P2PORT ) || ( [ -x /cygdrive/c/Program\ Files/OCS\ Inventory\ Agent/OCSInventory.exe ] && /cygdrive/c/Program\ Files/OCS\ Inventory\ Agent/OCSInventory.exe /np /server:$P2SRV /pnum:$P2PORT ) || ( [ -x /cygdrive/c/Program\ Files\ \(x86\)/OCS\ Inventory\ Agent/OCSInventory.exe ] && /cygdrive/c/Program\ Files\ \(x86\)/OCS\ Inventory\ Agent/OCSInventory.exe /np /server:$P2SRV /pnum:$P2PORT ) || ( [ -x /usr/bin/ocsinventory-agent ] && /usr/bin/ocsinventory-agent --server=http://$P2SRV:$P2PORT ) || ( [ -x /usr/sbin/ocsinventory-agent ] && /usr/sbin/ocsinventory-agent --server=http://$P2SRV:$P2PORT ) || ( [ -x /usr/local/sbin/ocs_mac_agent.php ] && /usr/local/sbin/ocs_mac_agent.php ) || ( [ -x /usr/local/bin/fusioninventory-agent ] && /usr/local/bin/fusioninventory-agent --server=http://$P2SRV:$P2PORT ) || ( [ -x /usr/bin/fusioninventory-agent ] && /usr/bin/fusioninventory-agent --server=http://$P2SRV:$P2PORT )'''
    launcher_path = "/usr/sbin/pulse2-launcher"
    max_command_age = 86400
    max_ping_time = 4
    max_probe_time = 20
    ping_path = "/usr/sbin/pulse2-ping"
    reboot_command = "/bin/shutdown.exe -f -r 1 || shutdown -r now"
    source_path = "/var/lib/pulse2/packages"
    target_path = "/tmp"
    temp_folder_prefix = "MDVPLS"

    # [daemon] section
    daemon_group = 0
    pid_path = "/var/run/pulse2"
    umask = 0077
    daemon_user = 0

    # wrapper stuff
    wrapper_max_exec_time = 21600
    wrapper_max_log_size = 512000
    wrapper_path = "/usr/sbin/pulse2-output-wrapper"

    # ssh stuff
    scp_path_default = scp_path = "/usr/bin/scp"
    ssh_agent_path_default = ssh_agent_path = "/usr/bin/ssh-agent"
    ssh_agent_sock = None
    ssh_agent_pid = None
    ssh_defaultkey = 'default'
    ssh_forward_key = 'let'
    ssh_keys = {
        'default': '/root/.ssh/id_rsa'
    }
    ssh_options = [ \
        'LogLevel=ERROR',
        'UserKnownHostsFile=/dev/null',
        'StrictHostKeyChecking=no',
        'Batchmode=yes',
        'PasswordAuthentication=no',
        'ServerAliveInterval=10',
        'CheckHostIP=no',
        'ConnectTimeout=10'
    ]
    ssh_path_default = ssh_path = "/usr/bin/ssh"

    # wget stuff
    wget_path_default = wget_path = '/usr/bin/wget'
    wget_options = ''
    wget_check_certs = False
    wget_resume = True

    # rsync stuff
    rsync_path_default = rsync_path = '/usr/bin/rsync'
    rsync_resume = True
    rsync_set_executable = 'yes'
    rsync_set_access = 'private'

    # WOL stuff
    wol_bcast = '255.255.255.255'
    wol_path = '/usr/sbin/pulse2-wol'
    wol_port = '40000'

    # SSH Proxy stuff
    tcp_sproxy_path = '/usr/sbin/pulse2-tcp-sproxy'
    tcp_sproxy_host = None
    tcp_sproxy_check = True
    tcp_sproxy_port_range_start = 8100
    tcp_sproxy_port_range_end = 8200
    tcp_sproxy_establish_delay = 60
    tcp_sproxy_connect_delay = 120
    tcp_sproxy_session_lenght = 3600

    # Create or not a web_proxy (to use with noVNC)
    create_web_proxy = False

    # Smart Cleaner Stuff
    is_smart_cleaner_available = True
    smart_cleaner_path = "/usr/bin/pulse2-smart-cleaner.sh"
    smart_cleaner_options = []

    # scheduler stuff
    first_scheduler = None
    schedulers = {
    }

    # [launcher_xxx] section
    launchers = {
    }

    ## initialize additionnal vars ##

    # base idea: rsync is NOT available
    is_rsync_available = False
    is_rsync_limited = True

    def setoption(self, section, key, attrib, type = 'str'):
        if type == 'str':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.get(section, key))
                log.debug("launcher %s: section %s, option %s set to '%s'" % (self.name, section, key, getattr(self, attrib)))
            else:
                log.debug("launcher %s: section %s, option %s not set, using default value '%s'" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'bool':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getboolean(section, key))
                log.debug("launcher %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                log.debug("launcher %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'int':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getint(section, key))
                log.debug("launcher %s: section %s, option %s set to %s" % (self.name, section, key, getattr(self, attrib)))
            else:
                log.debug("launcher %s: section %s, option %s not set, using default value %s" % (self.name, section, key, getattr(self, attrib)))
        elif type == 'pass':
            if self.cp.has_option(section, key):
                setattr(self, attrib, self.cp.getpassword(section, key))
                log.debug("launcher %s: section %s, option %s set using given value" % (self.name, section, key))
            else:
                log.debug("launcher %s: section %s, option %s not set, using default value" % (self.name, section, key))

    def presetup(self, config_file):
        """
            used to pre-parse conf file to gather enough data to setuid() soon
        """
        self.cp = pulse2.utils.Pulse2ConfigParser()
        self.cp.read(config_file)
        self.cp.read(config_file + '.local')

        if self.cp.has_option("daemon", "user"):
            self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
        if self.cp.has_option("daemon", "group"):
            self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
        if self.cp.has_option("daemon", "umask"):
            self.umask = string.atoi(self.cp.get("daemon", "umask"), 8)
        if self.cp.has_option("handler_hand01", "args"):
            self.logdir = os.path.dirname(re.compile("['|\"]").split(self.cp.get("handler_hand01", "args"))[1])

    def setup(self, config_file, name = None):
        # Load configuration file
        if not self.cp: # self.cp is set if presetup() was already called
            self.presetup(config_file)

        self.name = name

        # Parse "launchers" section
        self.setoption('launchers', 'inventory_command', 'inventory_command')
        self.setoption('launchers', 'launcher_path', 'launcher_path')
        self.setoption('launchers', 'max_command_age', 'max_command_age', 'int')
        self.setoption('launchers', 'max_ping_time', 'max_ping_time', 'int')
        self.setoption('launchers', 'max_probe_time', 'max_probe_time', 'int')
        self.setoption('launchers', 'ping_path', 'ping_path')
        self.setoption('launchers', 'source_path', 'source_path')
        self.setoption('launchers', 'reboot_command', 'reboot_command')
        self.setoption('launchers', 'halt_command', 'halt_command')
        self.setoption('launchers', 'target_path', 'target_path')
        self.setoption('launchers', 'temp_folder_prefix', 'temp_folder_prefix')

        # Parse "wrapper" section
        self.setoption('wrapper', 'max_log_size', 'wrapper_max_log_size', 'int')
        self.setoption('wrapper', 'max_exec_time', 'wrapper_max_exec_time', 'int')
        self.setoption('wrapper', 'path', 'wrapper_path')

        # Parse "wget" section
        self.setoption('wget', 'wget_path', 'wget_path')
        if self.cp.has_section("wget"):
            if self.cp.has_option("wget", "wget_options"):
                self.wget_options = self.cp.get("wget", "wget_options").split(' ')
        self.setoption('wget', 'check_certs', 'wget_check_certs', 'bool')
        self.setoption('wget', 'resume', 'wget_resume', 'bool')

        # Parse a part of "ssh" section
        self.setoption('ssh', 'ssh_path', 'ssh_path')
        self.setoption('ssh', 'scp_path', 'scp_path')
        self.setoption('ssh', 'ssh_agent_path', 'ssh_agent_path')

        # Parse "rsync" section
        self.setoption('rsync', 'rsync_path', 'rsync_path')
        self.setoption('rsync', 'resume', 'rsync_resume', 'bool')
        self.setoption('rsync', 'set_executable', 'rsync_set_executable')
        if not self.rsync_set_executable in ('yes', 'no', 'keep'):
            self.logger.warning("set_executable can have '%s' for value (yes|no|keep)"%(self.rsync_set_executable))
            self.rsync_set_executable = 'yes'
        self.setoption('rsync', 'set_access', 'rsync_set_access')
        if not self.rsync_set_access in ('private', 'restricted', 'public'):
            self.logger.warning("set_access can have '%s' for value (private|restricted|public)"%(self.rsync_set_access))
            self.rsync_set_access = 'private'

        # +----------------+------------------+---------------------+------------------+
        # | set_executable |                  |                     |                  |
        # +--------------\ |       yes        |         no          |        keep      |
        # | set_access    \|                  |                     |                  |
        # +----------------+------------------+---------------------+------------------+
        # | private        | u=rwx,g=,o=  (1) | u=rw,g=,o=          | u=rwX,g=,o=      |
        # +----------------+------------------+---------------------+------------------+
        # | restricted     | u=rwx,g=rx,o=    | u=rw,g=r,o=         | u=rwX,g=rX,o=    |
        # +----------------+------------------+---------------------+------------------+
        # | public         | u=rwx,g=rwx,o=rx | u=rw,g=rw,o=r       | u=rwX,g=rwX,o=rX |
        # +----------------+------------------+---------------------+------------------+
        # (1) : default value
        exe = 'X'
        if self.rsync_set_executable == 'yes':
            exe = 'x'
        elif self.rsync_set_executable == 'no':
            exe = ''

        other = ',o='
        group = ',g='
        if self.rsync_set_access == 'public':
            other += "r%s"%(exe)
            group += "rw%s"%(exe)
        elif self.rsync_set_access == 'restricted':
            group += "r%s"%(exe)
        self.rsync_set_chmod = 'u=rw%s%s%s'%(exe, group, other)

        log.debug("config metavalue 'rsync_set_chmod' = %s"%(self.rsync_set_chmod))

        # [daemon] section parsing (parsing ofr user, group, and umask is done above in presetup)
        if self.cp.has_section("daemon"):
            if self.cp.has_option('daemon', 'pid_path'):
                log.warning("'pid_path' is deprecated, please replace it in your config file by 'pidfile'")
                self.setoption('daemon', 'pid_path', 'pid_path')
            else:
                self.setoption('daemon', 'pidfile', 'pid_path')

        # Parse "wol" section
        self.setoption('wol', 'wol_bcast', 'wol_bcast')
        self.setoption('wol', 'wol_path', 'wol_path')
        self.setoption('wol', 'wol_port', 'wol_port')

        # Parse "tcp_sproxy" section
        self.setoption('tcp_sproxy', 'tcp_sproxy_path', 'tcp_sproxy_path')
        self.setoption('tcp_sproxy', 'tcp_sproxy_host', 'tcp_sproxy_host')
        self.setoption('tcp_sproxy', 'tcp_sproxy_check', 'tcp_sproxy_check', 'bool')
        self.setoption('tcp_sproxy', 'tcp_sproxy_establish_delay', 'tcp_sproxy_establish_delay', 'int')
        self.setoption('tcp_sproxy', 'tcp_sproxy_connect_delay', 'tcp_sproxy_connect_delay', 'int')
        self.setoption('tcp_sproxy', 'tcp_sproxy_session_lenght', 'tcp_sproxy_session_lenght', 'int')
        self.setoption('tcp_sproxy', 'create_web_proxy', 'create_web_proxy', 'bool')
        if self.cp.has_section("tcp_sproxy"):
            if self.cp.has_option("tcp_sproxy", "tcp_sproxy_port_range"):
                range = map(lambda x: int(x), self.cp.get("tcp_sproxy", "tcp_sproxy_port_range").split('-'))
                if len(range) != 2:
                    log.info("'tcp_sproxy_port_range' not formated as expected, using default value, please check your config file ")
                else:
                    (self.tcp_sproxy_port_range_start, self.tcp_sproxy_port_range_end) = range
        log.info("launcher %s: section %s, option %s set to %d-%d" % (self.name, 'tcp_sproxy', 'tcp_sproxy_port_range', self.tcp_sproxy_port_range_start, self.tcp_sproxy_port_range_end))

        # Parse "smart_cleaner" section
        self.setoption('smart_cleaner', 'smart_cleaner_path', 'smart_cleaner_path')
        if self.smart_cleaner_path == '':
            LauncherConfig().is_smart_cleaner_available = False
        if self.cp.has_section("smart_cleaner"):
            if self.cp.has_option("smart_cleaner", "smart_cleaner_options"):
                self.smart_cleaner_options = self.cp.get("smart_cleaner", "smart_cleaner_options").split(' ')

        # Parse "scheduler_XXXX" sections
        for section in self.cp.sections():
            if re.compile('^scheduler_[0-9]+$').match(section):
                try:
                    username = self.getvaluedefaulted(section, 'username', 'username')
                    password = self.getvaluedefaulted(section, 'password', "password", 'pass')
                    if not isTwistedEnoughForLoginPass():
                        if username != '':
                            if username != 'username':
                                log.warning("your version of twisted is not high enough to use login (%s/username)"%(section))
                            username = ''
                        if password != '':
                            if password != 'password':
                                log.warning("your version of twisted is not high enough to use password (%s/password)"%(section))
                            password = ''

                    awake_incertitude_factor = self.getvaluedefaulted(section, 'awake_incertitude_factor', .2, 'float')
                    if awake_incertitude_factor > .5:
                        log.warning("in %s, awake_incertitude_factor greater than .5, setting it to .5" % (section))
                        awake_incertitude_factor = .5
                    if awake_incertitude_factor < 0:
                        log.warning("in %s, awake_incertitude_factor lower than 0, setting it to 0" % (section))
                        awake_incertitude_factor = 0
                    awake_time = self.getvaluedefaulted(section, 'awake_time', 600, 'int')
                    if awake_time < 60:
                        log.warning("in %s, awake_time lower than 60, setting it to 60" % (section))
                        awake_time = 60

                    self.schedulers[section] = {
                        'host' : self.getvaluedefaulted(section, 'host', '127.0.0.1'),
                        'port' : self.getvaluedefaulted(section, 'port', "8000"),
                        'username' : username,
                        'password' : password,
                        'enablessl' : self.getvaluedefaulted(section, 'enablessl', True, 'bool'),
                        'awake_time' : awake_time,
                        'awake_incertitude_factor' : awake_incertitude_factor,
                        'defer_results' : self.getvaluedefaulted(section, 'defer_results', False, 'bool')
                    }
                    if self.first_scheduler == None:
                        self.first_scheduler = section
                except ConfigParser.NoOptionError, error:
                    log.warn("launcher %s: section %s do not seems to be correct (%s), please fix the configuration file" % (self.name, section, error))

        # Parse "launcher_XXXX" sections
        for section in self.cp.sections():
            if re.compile('^launcher_[0-9]+$').match(section):
                try:
                    username = self.getvaluedefaulted(section, 'username', 'username')
                    password = self.getvaluedefaulted(section, 'password', "password", 'pass')
                    if not isTwistedEnoughForLoginPass():
                        if username != '':
                            if username != 'username':
                                log.warning("your version of twisted is not high enough to use login (%s/username)"%(section))
                            username = ''
                        if password != '':
                            if password != 'password':
                                log.warning("your version of twisted is not high enough to use password (%s/password)"%(section))
                            password = ''

                    self.launchers[section] = {
                            'bind': self.getvaluedefaulted(section, 'bind', '127.0.0.1'),
                            'port': self.cp.get(section, 'port'),
                            'username': username,
                            'password': password,
                            'enablessl': self.getvaluedefaulted(section, 'enablessl', True, 'bool'),
                            'slots': self.getvaluedefaulted(section, 'slots', 300, 'int'),
                            'scheduler': self.getvaluedefaulted(section, 'scheduler', self.first_scheduler),
                            'logconffile' : self.getvaluedefaulted(section, 'logconffile', None),
                        }
                    if self.launchers[section]['enablessl']:
                        if self.cp.has_option(section, 'verifypeer'):
                            self.launchers[section]['verifypeer'] = self.cp.getboolean(section, 'verifypeer')
                        else:
                            self.launchers[section]['verifypeer'] = False
                        if self.cp.has_option(section, 'cacert'):
                            self.launchers[section]['cacert'] = self.cp.get(section, 'cacert')
                        else:
                            self.launchers[section]['cacert'] = self.cp.get(section, 'certfile')
                        if self.cp.has_option(section, 'localcert'):
                            self.launchers[section]['localcert'] = self.cp.get(section, 'localcert')
                        else:
                            self.launchers[section]['localcert'] = self.cp.get(section, 'privkey')
                        if not os.path.exists(self.launchers[section]['cacert']):
                            raise Exception("Configuration error: path %s does not exists" % self.launchers[section]['cacert'])
                            return False
                        if not os.path.exists(self.launchers[section]['localcert']):
                            raise Exception("Configuration error: path %s does not exists" % self.launchers[section]['localcert'])
                            return False
                        if self.launchers[section]['verifypeer']: # we need twisted.internet.ssl.Certificate to activate certs
                            import twisted.internet.ssl
                            if not hasattr(twisted.internet.ssl, "Certificate"):
                                raise Exception('Configuration error in section "%s": I need at least Python Twisted 2.5 to handle peer checking' % (section))
                                return False

                        maxslots = (os.sysconf('SC_OPEN_MAX') - 50) / 2 # "should work in most case" formulae
                        if self.launchers[section]['slots'] > maxslots:
                            log.warn("launcher %s: section %s, slots capped to %s instead of %s regarding the max FD (%s)" % (self.name, section, maxslots, self.launchers[section]['slots'], os.sysconf('SC_OPEN_MAX')))
                            self.launchers[section]['slots'] = maxslots

                except ConfigParser.NoOptionError, e:
                    log.warn("launcher %s: section %s do not seems to be correct (%s), please fix the configuration file" % (self.name, section, e))

        # check for a few binaries availability
        if self.conf_or_default('rsync'):
            rsync_version = os.popen("%s --version"%(self.rsync_path), 'r').read().split('\n')[0].split(' ')[3].split('.')
            if len(rsync_version) != 3:
                log.warn("launcher %s: can't find RSYNC (looking for rsync version), disabling all rsync-related stuff" % (self.name))
                self.is_rsync_available = False
            else:
                if rsync_version[0] < 2 or rsync_version[0] == 2 and rsync_version[1] < 6: # version < 2.6.0 => dont work
                    self.is_rsync_available = False
                elif rsync_version[0] == 2 and rsync_version[1] == 6 and rsync_version[2] < 7: # version between 2.6.0 and 2.6.7 => work but limited
                    self.is_rsync_available = True
                    self.is_rsync_limited = True
                else:
                    self.is_rsync_available = True
                    self.is_rsync_limited = False

        for p in ("scp", "ssh", "ssh_agent"):
            self.conf_or_default(p)

    def conf_or_default(self, type):
        label = type.upper().replace("_", " ")
        conf = getattr(self, "%s_path"%(type))
        default = getattr(self, "%s_path_default"%(type))

        if not os.access(conf, os.X_OK):
            if not os.access(default, os.X_OK):
                log.warn("launcher %s: can't find %s (looking for %s nor the default value %s), disabling all %s-related stuff" % (self.name, label, conf, default, type))
                setattr(self, "is_%s_available"%(type.replace("_", "")), False)
            else:
                log.warn("launcher %s: can't find %s (looking for %s) but by using the default value" % (self.name, label, conf))
                setattr(self, "is_%s_available"%(type.replace("_", "")), True)
                setattr(self, "%s_path"%(type), default)
        else:
            setattr(self, "is_%s_available"%(type.replace("_", "")), True)
        return getattr(self, "is_%s_available"%(type.replace("_", "")))

    def setup_post_permission(self):
        # Parse "ssh" sections
        self.setoption('ssh', 'default_key', 'ssh_defaultkey')
        self.setoption('ssh', 'forward_key', 'ssh_forward_key')

        self.setoption('ssh', 'ssh_options', 'ssh_options')
        if not type(self.ssh_options) == type([]):
            self.ssh_options = self.ssh_options.split(' ')

        has_sshkey = False
        if self.cp.has_section('ssh'):
            for option in self.cp.options('ssh'):
                if re.compile('^sshkey_[0-9A-Za-z]+$').match(option):
                    keyname = re.compile('^sshkey_([0-9A-Za-z]+)$').match(option).group(1)
                    keyfile = self.cp.get('ssh', option)
                    self.ssh_keys[keyname] = keyfile
                    if checkKeyPerm(keyfile):
                        log.info("launcher %s: added ssh key '%s' to keyring as key '%s'" % (self.name, keyfile, keyname))
                        has_sshkey = True
                    else:
                        del self.ssh_keys[keyname]
                        log.warn("launcher %s: didn't added ssh key '%s' to keyring as key '%s'" % (self.name, keyfile, keyname))
        if not checkKeyPerm(self.ssh_keys['default']):
            keyfile = self.ssh_keys['default']
            if has_sshkey:
                del self.ssh_keys['default']
                if self.ssh_defaultkey == 'default':
                    self.ssh_defaultkey = self.ssh_keys.keys()[0]
                    log.warning("launcher %s: the default ssh key '%s' is not valid, set '%s' as default (you should specify it with ssh_defaultkey)" % (self.name, keyfile, self.ssh_defaultkey))
            else:
                del self.ssh_keys['default']
                log.error("launcher %s: the default ssh key '%s' is not valid" % (self.name, keyfile))

    def getvaluedefaulted(self, section, option, default, type = 'str'):
        """ parse value using the given type """
        if self.cp.has_option(section, option):
            if type == 'str':
                return self.cp.get(section, option)
            elif type == 'bool':
                return self.cp.getboolean(section, option)
            elif type == 'int':
                return self.cp.getint(section, option)
            elif type == 'pass':
                return self.cp.getpassword(section, option)
            elif type == 'float':
                return self.cp.getfloat(section, option)
        else:
            return default

    def check(self):
        """
        Raise an error if the configuration is bad
        """
        paths = [self.launcher_path, self.ping_path, self.wrapper_path, self.wol_path]
        sshkeys = self.ssh_keys.values()
        if len(sshkeys) == 0:
            log.error("Configuration error: no ssh key has been defined")
            raise Exception("Configuration error: no ssh key has been defined")
        paths.extend(sshkeys)
        for path in paths:
            if not os.path.exists(path):
                log.error("Configuration error: path %s does not exists" % path)
                raise Exception("Configuration error: path %s does not exists" % path)

def checkKeyPerm(keyfile):
    try:
        if not os.path.exists(keyfile):
            log.warn("launcher %s: the ssh key file %s does not exists" % (LauncherConfig().name, keyfile))
            return False
        stats = os.stat(keyfile)
    except:
        log.warn("launcher %s: something goes wrong while performing stat() on %s !" % (LauncherConfig().name, keyfile))
        return False

    if stats.st_uid != os.getuid():
        log.debug("launcher %s: ssh key '%s' owner is %s, my uid is %s, dropping the key from the keyring" % (LauncherConfig().name, keyfile, stats.st_uid, os.getuid()))
        return False

    if stats.st_uid != os.geteuid():
        log.debug("launcher %s: ssh key '%s' owner is %s, my euid is %s, dropping the key from the keyring" % (LauncherConfig().name, keyfile, stats.st_uid, os.geteuid()))
        return False

    if stat.S_IMODE(os.stat(keyfile).st_mode) & ~(stat.S_IRUSR | stat.S_IWUSR): # check if perm are at most rw-------
        log.debug("launcher %s: ssh key '%s' perms are not *exactly* rw-------, dropping the key from the keyring" % (LauncherConfig().name, keyfile))
        return False

    return True

