# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import os
import sys
import fileinput

from subprocess import call
from distutils.file_util import copy_file

VERSION = "0.1"
NAME = "Pulse2 Agent"


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
        """Checks if defaults file exists"""
        return os.path.exists(self.defaults_file)

    def get_defaults(self):
        """Parses a defaults file"""
        pattern = {}
        if self.exists:
            with open(self.defaults_file, "r") as f:
                for num, line in enumerate(f.readlines()):
                    if len(line.strip()) == 0:
                        # ignore empty lines
                        continue
                    if self.DELIMITER in line:
                        if line.count(self.DELIMITER) == 1:
                            name, value = [
                                s.strip() for s in line.split(self.DELIMITER)
                            ]
                            pattern[name] = value
                        else:
                            print(
                                "WARNING: Unknown format  (file: %s:%d)"
                                % (self.defaults_file, num)
                            )
                            print("  --> %s" % line)
                            print("INFO: Ignoring")
                    else:
                        print(
                            "WARNING: Unknown format  (file: %s:%d)"
                            % (self.defaults_file, num)
                        )
                        print("  --> %s" % line)
                        print("INFO: Ignoring")
        else:
            print("WARNING: File with defaults (%s) not exists!" % (self.defaults_file))

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
            for (old, new) in list(pattern.items()):
                search_exp = "@@%s@@" % old
                if search_exp in line:
                    line = line.replace(search_exp, new)
                    replaced_items += 1
            sys.stdout.write(line)

        return replaced_items == len(pattern)


class PostInstallPosixHandler(object):
    """Abstract class to generalize different startup systems"""

    SCRIPT_NAME = "pulse2-agent"
    current_directory = None

    system_management = None
    insert_service_cmd = None
    start_service_cmd = None

    # list of files to copy : [(source, destionation),]
    include_files = [
        (),
    ]

    def __init__(self, current_directory):
        self.current_directory = current_directory

        print("Running selected handler: %s" % self.__class__.__name__)

    def run(self):
        for method in (
            self.copy_files,
            self.post_copy_tasks,
            self.fill_defaults,
            self.start_service,
        ):
            succeed = method()
            if not succeed:
                print("ERROR: An error occurred during execute %s" % method.__name__)
                return False
        return True

    def copy_files(self):
        """Copy include files"""
        for (source, destination) in self.include_files:

            result = copy_file(source, destination)
            if result[1] != 1:
                print("WARNING: copy of file %s -> %s failed" % (source, destination))
                return False
        return True

    def post_copy_tasks(self):
        """Custom tasks to execute after the copy phase"""
        return True

    def fill_defaults(self):
        """Config file filled by pre-configured defaults file"""
        df = DefaultsFiller()
        if df.exists:
            all_replaced = df.fill()
            if all_replaced:
                print("INFO: Config file correctly updated")
                return True
            else:
                print("WARNING: Some occurrences weren't correctly updated")
                print("WARNING: Fix please your config file")
                print("WARNING: Start of service omitted")
        else:
            print("WARNING: File of defaults not exists")
            print("WARNING: Start of service omitted")

        return False

    def insert_service(self):
        """
        Add command to system

        @return: True if successfully added
        @rtype: bool
        """
        if self.insert_service_cmd is None:
            return True

        print("Install service %s ..." % self.SCRIPT_NAME)
        result = call(self.insert_service_cmd, shell=True)
        return result == 0

    def start_service(self):
        """
        Start command as service

        @return: True if successfully started
        @rtype: bool
        """
        if self.start_service_cmd is None:
            return True

        print("Starting service %s ..." % self.SCRIPT_NAME)
        result = call(self.start_service_cmd, shell=True)
        return result == 0


class PostInstallSystemVHandler(PostInstallPosixHandler):
    """SystemV (based on inittab) handler"""

    insert_service_cmd = (
        "/usr/sbin/update-rc.d %s defaults" % PostInstallPosixHandler.SCRIPT_NAME
    )
    start_service_cmd = "/etc/init.d/%s start" % PostInstallPosixHandler.SCRIPT_NAME

    include_files = [
        ("linux/pulse2-agent.init.lsb", "/etc/init.d/pulse2-agent"),
        ("linux/pulse2-agent.default", "/etc/default/pulse2-agent"),
        ("pulse2agent.ini", "/etc/pulse2agent.ini"),
    ]


class PostInstallSysCtlHandler(PostInstallPosixHandler):
    """Sysctl handler"""

    insert_service_cmd = (
        "/bin/chkconfig --add  %s" % PostInstallPosixHandler.SCRIPT_NAME
    )
    start_service_cmd = "/etc/init.d/%s start" % PostInstallPosixHandler.SCRIPT_NAME

    include_files = [
        ("linux/pulse2-agent.init", "/etc/init.d/pulse2-agent"),
        ("linux/pulse2-agent.default", "/etc/default/pulse2-agent"),
        ("pulse2agent.ini", "/etc/pulse2agent.ini"),
    ]


class PostInstallSystemDHandler(PostInstallPosixHandler):
    """Systemd handler"""

    insert_service_cmd = (
        "/bin/systemctl enable %s.service" % PostInstallPosixHandler.SCRIPT_NAME
    )
    start_service_cmd = (
        "/bin/systemctl start %s.service" % PostInstallPosixHandler.SCRIPT_NAME
    )

    include_files = [
        ("linux/pulse2-agent.service", "/lib/systemd/system/"),
        ("pulse2agent.ini", "/etc/pulse2agent.ini"),
    ]

    def post_copy_tasks(self):

        cmd_link = (
            "ln -s /lib/systemd/system/%s.service /etc/systemd/system/%s.service"
            % (self.SCRIPT_NAME, self.SCRIPT_NAME)
        )
        cmd_systemd_reload = " /bin/systemctl daemon-reload"
        for cmd in [cmd_link, cmd_systemd_reload]:
            result = call(cmd, shell=True)
            if result != 0:
                return False
        return True


class PostInstallOSXHandler(PostInstallPosixHandler):
    """Mac OS X handler"""

    insert_service_cmd = "/bin/launchd load com.pulse2.agent"

    include_files = [
        ("mac/com.pulse2.agent.plist", "/Library/LaunchDaemons"),
        ("pulse2agent.ini", "/etc/pulse2agent.ini"),
    ]


class SystemManagementResolver(object):
    """
    Selects a correct handler to insert and configure service to system.

    The choice is based on existence of service configuration tools.
    Important: Because sysctl exists on systemd too, the check of systemd
    must be executed before.
    """

    handlers = {
        "/usr/sbin/update-rc.d": PostInstallSystemVHandler,
        "/usr/bin/systemctl": PostInstallSystemDHandler,
        "/sbin/sysctl": PostInstallSysCtlHandler,
        "/bin/launchctl": PostInstallOSXHandler,
    }

    def resolve(self):
        """
        Resolves a correct handler.

        @return: handler
        @rtype: PostInstallPosixHandler
        """
        for path, handler in list(self.handlers.items()):
            if os.path.exists(path):
                return handler


if sys.platform in ("linux2", "darwin"):

    SCRIPT_NAME = "pulse2-agent"
    from distutils.core import setup
    from distutils.command.install import install as _install

    def post_install(current_directory):
        """
        Post-install phase to run several tasks.

        - configure phase (copy config and daemon files)
        - put the defaults into the config file
        - start service
        """
        handler = SystemManagementResolver().resolve()
        return handler(current_directory).run()

    class Install(_install):
        "Distutils command install class subclassed to run post-install phase"

        def run(self):
            _install.run(self)
            self.execute(
                post_install, (self.install_lib,), msg="Running post install task"
            )

    setup(
        name=NAME,
        version=VERSION,
        description=NAME,
        packages=["pulse2agent"],
        scripts=["pulse2-agent"],
        cmdclass={"install": Install},
    )


elif sys.platform == "win32":

    from cx_Freeze import setup, Executable

    executables = [
        Executable(
            "pulse2agent/config.py",
            base="Win32Service",
            packages=["pulse2agent"],
            targetName="service.exe",
        )
    ]
    include_modules = [
        "service",
    ]
    include_files = [
        "pulse2agent.ini",
    ]
    build_options = dict(
        includes=include_modules, include_files=include_files, include_msvcr=1
    )
    setup(
        name=NAME,
        version=VERSION,
        description=NAME,
        options=dict(build_exe=build_options),
        executables=executables,
    )
