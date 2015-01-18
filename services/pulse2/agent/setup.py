# -*- coding: utf-8; -*-
#
# (c) 2014 Mandriva, http://www.mandriva.com/
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

import os
import sys
import fileinput

class DefaultsFiller(object):
    """
    Replaces declared occurences in a templated file.
    Based on a pattern of defaults.

    Format of pattern defaults file:
    PARAM1 = value1
    PARAM2 = value2
    ...

    Format of templated config file with parametters to fill:
    [section]
    param1 = @@PARAM1@@
    param2 = @@PARAM2@@
    """
    config_file = "/etc/pulse2agent.ini"
    defaults_file = "pulse2agent.defaults"

    DELIMITER = "="

    def __init__(self, config_file=None, defaults_file=None):
        """
        @param config_file: path to config file
        @type config file: str

        @param defaults_file: path to defaults file
        @type defaults file: str
        """
        if config_file:
            self.config_file = config_file
        if defaults_file:
            self.defaults_file = defaults_file



    @property
    def exists(self):
        """Checks if defaults file exists """
        return os.path.exists(self.defaults_file)


    def get_defaults(self):
        """Parses a defaults file """
        pattern = {}
        if self.exists:
            with open(self.defaults_file, "r") as f:
                for num, line in enumerate(f.readlines()):
                    if len(line.strip()) == 0:
                        # ignore empty lines
                        continue
                    if self.DELIMITER in line:
                        if line.count(self.DELIMITER) == 1:
                            name, value = [s.strip() for s in line.split(self.DELIMITER)]
                            pattern[name] = value
                        else:
                            print "WARNING: Unknown format  (file: %s:%d)" % (self.defaults_file, num)
                            print "  --> %s" % line
                            print "INFO: Ignoring"
                    else:
                        print "WARNING: Unknown format  (file: %s:%d)" % (self.defaults_file, num)
                        print "  --> %s" % line
                        print "INFO: Ignoring"
        else:
            print "WARNING: File with defaults (%s) not exists!" % (self.defaults_file)

        return pattern


    def fill(self):
        """
        Puts new values into a config file based on defaults.

        @return: True if all occurences replaced
        @rtype: bool
        """
       # pattern = {"PULSE2_CM_SERVER": "192.168.127.10",
       #            "PULSE2_CM_PORT": "8443",
       #            "VPNCMD_PATH": "/opt/vpnclient/vpncmd",
       #            "PULSE2_CM_LOG_PATH": "/var/log/pulse2agent.log",
       #            }
        pattern = self.get_defaults()
        return self.replace(pattern)

    def replace(self, pattern):
        """
        Replaces all occurences based on pattern.

        @param pattern: key as template expression, value as new string
        @type pattern: dict

        @return: True if all occurences replaced
        @rtype: bool
        """
        replaced_items = 0
        for line in fileinput.input(self.config_file, inplace=1):
            for (old, new) in pattern.iteritems():
                search_exp = "@@%s@@" % old
                if search_exp in line:
                    line = line.replace(search_exp, new)
                    replaced_items += 1
            sys.stdout.write(line)

        return replaced_items == len(pattern)



if sys.platform == "win32":
    from cx_Freeze import setup, Executable
    executables = [Executable("pulse2agent/config.py",
                              base="Win32Service",
                              packages = ["pulse2agent"],
                              targetName="service.exe")
                   ]
    include_modules = ["service",]
    include_files = ["pulse2agent.ini",]
    build_options = dict(includes = include_modules,
                         include_files = include_files,
                         include_msvcr = 1
                         )
    setup(name='Pulse2 Agent',
          version = '0.1',
          description = 'Pulse2 Agent',
          options = dict(build_exe = build_options),
          executables = executables)

elif sys.platform == "linux2":

    SCRIPT_NAME = "pulse2-agent"
    from subprocess import call
    from distutils.core import setup
    from distutils.command.install import install as _install
    from distutils.file_util import copy_file

    def post_install(cur_dir):
        """
        Post-install phase to run several tasks.

        - configure phase (copy config and daemon files)
        - put the defaults into the config file
        - start service
        """
        if os.path.exists('/usr/sbin/update-rc.d'):
            result = copy_file("linux/pulse2-agent.init",
                               "/etc/init.d/pulse2-agent")
            if result[1] == 1:
                print "ok init"
            result = copy_file("linux/pulse2-agent.default",
                               "/etc/default/pulse2-agent")
            if result[1] == 1:
                print "ok default"

            result = copy_file("pulse2agent.ini",
                               "/etc/pulse2agent.ini")
            if result[1] == 1:
                print "ok conf"

            result = call("/usr/sbin/update-rc.d %s defaults" % SCRIPT_NAME,
                          shell=True
                          )
            if result == 0:
                print "rc.d ok"
        else:
            print "Cannot install.. sysctl based system ?"

        df = DefaultsFiller()
        if df.exists :
            all_replaced = df.fill()
            if all_replaced:
                result = call("/etc/init.d/%s start" % SCRIPT_NAME,
                              shell=True
                              )
                if result == 0:
                    print "start of service ok"
            else:
                print "Corrupted defaults file, fix please your config file"
                print "Start of service omitted"
        else:
            print "File of defaults not exists"
            print "Start of service omitted"


    class Install(_install):
        "Distutils command install class subclassed to run post-install phase"

        def run(self):
            _install.run(self)
            self.execute(post_install,
                         (self.install_lib,),
                         msg="Running post install task"
                         )

    setup(name='Pulse2 Agent',
          version = '0.1',
          description = 'Pulse2 Agent',
          packages = ["pulse2agent"],
          scripts = ["pulse2-agent"],
          cmdclass={'install': Install},
          )

