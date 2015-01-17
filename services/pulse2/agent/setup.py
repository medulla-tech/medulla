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


    class Install(_install):
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

