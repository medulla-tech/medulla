# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
The module define the config option needed by the package server and all
it's API modules.
"""

from mmc.site import mmcconfdir

# Misc
import configparser
import re
import sys
import pulse2.utils
import logging
import os
from pulse2.xmlrpc import isTwistedEnoughForLoginPass
from pulse2.utils import isUUID, subnetForIpMask

if sys.platform != "win32":
    import pwd
    import grp
    from pulse2.utils import Pulse2ConfigParser


class P2PServerCP(pulse2.utils.Singleton):
    """
    Class to hold configuration directives
    """

    cacert = mmcconfdir + "/pulse2/package-server/keys/cacert.pem"
    localcert = mmcconfdir + "/pulse2/package-server/keys/privkey.pem"

    # default values

    # [main] section
    bind = ""
    port = 9990
    public_ip = bind
    enablessl = True
    verifypeer = False
    username = ""
    password = ""
    tmp_input_dir = "/var/lib/pulse2/package-server-tmpdir"

    pxe_password = ""
    pxe_keymap = "C"

    if sys.platform != "win32":
        daemon_group = 0
        daemon_user = pwd.getpwnam("root")[2]
        umask = int("0022", 8)
        pidfile = "/var/run/pulse2-package-server.pid"
    if sys.platform == "win32":
        use_iocp_reactor = False

    package_detect_loop = 60
    package_detect_activate = False

    SMART_DETECT_NONE = 0
    SMART_DETECT_LAST = 1
    SMART_DETECT_LOOP = 2
    SMART_DETECT_SIZE = 3

    detectSmartMethod = ["none", "last", "loop", "size"]

    def packageDetectSmartMethod(self):
        return ", ".join(
            [self.detectSmartMethod[x] for x in self.package_detect_smart_method]
        )

    package_detect_smart = False
    package_detect_smart_method = []
    package_detect_smart_time = 60

    package_detect_tmp_activate = False

    real_package_deletion = True

    package_mirror_loop = 5
    package_mirror_activate = False
    package_mirror_target = ""
    package_mirror_status_file = "/var/data/mmc/status"
    package_mirror_command = "/usr/bin/rsync"
    package_mirror_command_options = ["-ar", "--delete"]
    package_mirror_level0_command_options = ["-d", "--delete"]
    package_mirror_command_options_ssh_options = None
    package_global_mirror_activate = True
    package_global_mirror_loop = 3600
    package_global_mirror_command_options = ["-ar", "--delete"]

    mm_assign_algo = "default"
    up_assign_algo = "default"

    # / [main] section

    parser = None
    mirrors = []
    package_api_get = []
    package_api_put = []
    proto = "http"

    mirror_api = {}
    user_package_api = {}
    scheduler_api = {}
    imaging_api = {}
    cp = None

    mmc_agent = {}
    config_file = ""

    def pre_setup(self, config_file):
        self.config_file = config_file
        if sys.platform != "win32":
            self.cp = Pulse2ConfigParser()
        else:
            self.cp = configparser.ConfigParser()
        self.cp.read(config_file)
        self.cp.read(config_file + ".local")

        if self.cp.has_option("handler_hand01", "args"):
            self.logdir = os.path.dirname(
                re.compile("['|\"]").split(self.cp.get("handler_hand01", "args"))[1]
            )

    def setup(self, config_file):
        self.config_file = config_file
        if self.cp is None:
            # Load configuration file
            if sys.platform != "win32":
                self.cp = Pulse2ConfigParser()
            else:
                self.cp = configparser.ConfigParser()
            self.cp.read(config_file)
            self.cp.read(config_file + ".local")

        if self.cp.has_option("main", "bind"):  # TODO remove in a future version
            logging.getLogger().warning(
                "'bind' is obsolete, please replace it in your config file by 'host'"
            )
            self.bind = self.cp.get("main", "bind")
        elif self.cp.has_option("main", "host"):
            self.bind = self.cp.get("main", "host")
        if self.cp.has_option("main", "port"):
            self.port = self.cp.getint("main", "port")
        if self.cp.has_option("main", "public_ip"):
            self.public_ip = self.cp.get("main", "public_ip")
        else:
            self.public_ip = self.bind
        if self.cp.has_option("main", "public_mask"):
            self.public_mask = self.cp.get("main", "public_mask")
        else:
            self.public_mask = "255.255.255.0"

        if sys.platform != "win32":
            if self.cp.has_section("daemon"):
                if self.cp.has_option("daemon", "pidfile"):
                    self.pid_path = self.cp.get("daemon", "pidfile")
                if self.cp.has_option("daemon", "user"):
                    self.daemon_user = pwd.getpwnam(self.cp.get("daemon", "user"))[2]
                if self.cp.has_option("daemon", "group"):
                    self.daemon_group = grp.getgrnam(self.cp.get("daemon", "group"))[2]
                if self.cp.has_option("daemon", "umask"):
                    self.umask = int(self.cp.get("daemon", "umask"), 8)

        if sys.platform == "win32":
            if self.cp.has_option("main", "use_iocp_reactor"):
                self.use_iocp_reactor = self.cp.getboolean("main", "use_iocp_reactor")

        if self.cp.has_option("ssl", "username"):
            self.username = self.cp.get("ssl", "username")
            if sys.platform != "win32":
                self.password = self.cp.getpassword("ssl", "password")
            else:
                self.password = self.cp.get("ssl", "password")
            if not isTwistedEnoughForLoginPass():
                if self.username:
                    logging.getLogger().warn(
                        "your version of twisted is not high enough to use login (ssl/username)"
                    )
                    self.username = ""
                if self.password != "":
                    logging.getLogger().warning(
                        "your version of twisted is not high enough to use password (ssl/password)"
                    )
                    self.password = ""

        if self.cp.has_option("ssl", "enablessl"):
            self.enablessl = self.cp.getboolean("ssl", "enablessl")
        if self.enablessl:
            self.proto = "https"
            if self.cp.has_option("ssl", "certfile"):
                self.cacert = self.cp.get("ssl", "certfile")
            if self.cp.has_option("ssl", "cacert"):
                self.cacert = self.cp.get("ssl", "cacert")
            if self.cp.has_option("ssl", "privkey"):
                self.localcert = self.cp.get("ssl", "privkey")
            if self.cp.has_option("ssl", "localcert"):
                self.localcert = self.cp.get("ssl", "localcert")
            if self.cp.has_option("ssl", "verifypeer"):
                self.verifypeer = self.cp.getboolean("ssl", "verifypeer")
            if not os.path.isfile(self.localcert):
                raise Exception('can\'t read SSL key "%s"' % (self.localcert))
                return False
            if not os.path.isfile(self.cacert):
                raise Exception('can\'t read SSL certificate "%s"' % (self.cacert))
                return False
            if (
                self.verifypeer
            ):  # we need twisted.internet.ssl.Certificate to activate certs
                import twisted.internet.ssl

                if not hasattr(twisted.internet.ssl, "Certificate"):
                    raise Exception(
                        "I need at least Python Twisted 2.5 to handle peer checking"
                    )
                    return False

        if self.cp.has_section("mirror_api"):
            self.mirror_api["mount_point"] = "/rpc"
            if self.cp.has_option("mirror_api", "mount_point"):
                self.mirror_api["mount_point"] = self.cp.get(
                    "mirror_api", "mount_point"
                )

        if self.cp.has_section("user_packageapi_api"):
            self.user_package_api["mount_point"] = "/upaa"
            if self.cp.has_option("user_packageapi_api", "mount_point"):
                self.user_package_api["mount_point"] = self.cp.get(
                    "user_packageapi_api", "mount_point"
                )

        if self.cp.has_section("scheduler_api"):
            self.scheduler_api["mount_point"] = "/scheduler_api"
            self.scheduler_api["schedulers"] = "scheduler_01"
            if self.cp.has_option("scheduler_api", "mount_point"):
                self.scheduler_api["mount_point"] = self.cp.get(
                    "scheduler_api", "mount_point"
                )
            if self.cp.has_option("scheduler_api", "schedulers"):
                self.scheduler_api["schedulers"] = self.cp.get(
                    "scheduler_api", "schedulers"
                )

        if self.cp.has_option("main", "tmp_input_dir"):
            self.tmp_input_dir = self.cp.get("main", "tmp_input_dir")

        for section in self.cp.sections():
            if re.compile("^mirror:[0-9]+$").match(section):
                mount_point = self.cp.get(section, "mount_point")
                src = self.cp.get(section, "src")
                mirror = {"mount_point": mount_point, "src": src}
                if self.cp.has_option(section, "mirror"):
                    mirror["mirror"] = self.cp.get(section, "mirror")
                self.mirrors.append(mirror)
            if re.compile("^package_api_get:[0-9]+$").match(section):
                mount_point = self.cp.get(section, "mount_point")
                src = self.cp.get(section, "src")
                self.package_api_get.append({"mount_point": mount_point, "src": src})
            if re.compile("^package_api_put:[0-9]+$").match(section):
                mount_point = self.cp.get(section, "mount_point")
                src = self.cp.get(section, "src")
                pap_tmp_input_dir = self.tmp_input_dir
                if self.cp.has_option(section, "tmp_input_dir"):
                    self.package_detect_activate = True
                    self.package_detect_tmp_activate = True
                    pap_tmp_input_dir = self.cp.get(section, "tmp_input_dir")

                self.package_api_put.append(
                    {
                        "mount_point": mount_point,
                        "src": src,
                        "tmp_input_dir": pap_tmp_input_dir,
                    }
                )

        # [mmc_agent] section parsing
        self.mmc_agent = {}
        if self.cp.has_section("mmc_agent"):
            self.mmc_agent = {
                "host": "127.0.0.1",
                "port": 7080,
                "username": "mmc",
                "password": "s3cr3t",
                "enablessl": True,
                "verifypeer": False,
                "cacert": mmcconfdir + "/pulse2/package-server/keys/cacert.pem",
                "localcert": mmcconfdir + "/pulse2/package-server/keys/privkey.pem",
            }
            if self.cp.has_option("mmc_agent", "host"):
                self.mmc_agent["host"] = self.cp.get("mmc_agent", "host")
            if self.cp.has_option("mmc_agent", "port"):
                self.mmc_agent["port"] = self.cp.getint("mmc_agent", "port")
            if self.cp.has_option("mmc_agent", "enablessl"):
                self.mmc_agent["enablessl"] = self.cp.getboolean(
                    "mmc_agent", "enablessl"
                )
            if self.cp.has_option("mmc_agent", "verifypeer"):
                self.mmc_agent["verifypeer"] = self.cp.getboolean(
                    "mmc_agent", "verifypeer"
                )
            if self.cp.has_option("mmc_agent", "cacert"):
                self.mmc_agent["cacert"] = self.cp.get("mmc_agent", "cacert")
            if self.cp.has_option("mmc_agent", "localcert"):
                self.mmc_agent["localcert"] = self.cp.get("mmc_agent", "localcert")
            if self.mmc_agent["enablessl"]:
                if not os.path.isfile(self.mmc_agent["localcert"]):
                    raise Exception(
                        'can\'t read SSL key "%s"' % (self.mmc_agent["localcert"])
                    )
                    return False
                if not os.path.isfile(self.mmc_agent["cacert"]):
                    raise Exception(
                        'can\'t read SSL certificate "%s"' % (self.mmc_agent["cacert"])
                    )
                    return False
                # we need twisted.internet.ssl.Certificate to activate certs
                if self.mmc_agent["verifypeer"]:
                    import twisted.internet.ssl

                    if not hasattr(twisted.internet.ssl, "Certificate"):
                        raise Exception(
                            "I need at least Python Twisted 2.5 to handle peer checking"
                        )
                        return False

        # [imaging_api] section parsing
        if self.cp.has_section("imaging_api") and self.cp.has_option(
            "imaging_api", "uuid"
        ):
            # mount point
            imaging_mp = "/imaging_api"
            # base folder
            base_folder = "/var/lib/pulse2/imaging"
            # will contain the bootloader material (revoboot + splashscreen),
            # served by tftp
            bootloader_folder = "bootloader"
            # CDROM bootloader
            cdrom_bootloader = "cdrom_boot"
            # Boot splash screen
            bootsplash_file = "bootsplash.png"
            # will contain the boot menus, served by tftp
            bootmenus_folder = "bootmenus"
            # will contain diskless stuff (kernel, initramfs, additional
            # tools), served by tftp
            diskless_folder = "davos"
            # Options passed to Davos at boot
            davos_options = ""
            # will contain tools, served by tftp
            tools_folder = "tools"
            # diskless kernel
            diskless_kernel = "vmlinuz"
            # diskless initrd
            diskless_initrd = "initrd.img"
            # diskless initrd for CD-ROM
            diskless_initrdcd = "initrdcd"
            # will contain computer-related materials
            computers_folder = "computers"
            # will contain inventories
            inventories_folder = "inventories"
            # will contain masters, served by tftp
            masters_folder = "masters"
            # will contain postinstall binaries
            postinst_folder = "postinst"
            # will contain archived computer imaging data
            archives_folder = "archives"
            # will contain generated ISO images
            isos_folder = "/var/lib/pulse2/imaging/isos"
            # tool used to generate ISO file
            isogen_tool = "/usr/bin/genisoimage"
            # will contain our UUID/MAC Addr cache
            uuid_cache_file = os.path.join(base_folder, "uuid-cache.txt")
            # our UUID/MAC Addr cache lifetime
            uuid_cache_lifetime = 300
            # RPC replay file
            rpc_replay_file = os.path.join(base_folder, "rpc-replay.pck")
            # RPC replay loop timer in seconds
            rpc_loop_timer = 60
            # RPC to replay at each loop
            rpc_count = 10
            # Interval in seconds between two RPCs
            rpc_interval = 2
            # Package Server UUID
            uuid = ""
            # listening on this port to communicate with PXE
            pxe_port = 1001
            # inventory host
            inventory_host = "127.0.0.1"
            # inventory port
            inventory_port = 9999
            # inventory SSL enable
            inventory_enablessl = False
            # on glpi, PXE register by minimal inventory
            glpi_mode = False
            # identification on PXE console

            if self.cp.has_option("imaging_api", "mount_point"):
                imaging_mp = self.cp.get("imaging_api", "mount_point")
            if self.cp.has_option("imaging_api", "base_folder"):
                base_folder = self.cp.get("imaging_api", "base_folder")
            if self.cp.has_option("imaging_api", "bootloader_folder"):
                bootloader_folder = self.cp.get("imaging_api", "bootloader_folder")
            if self.cp.has_option("imaging_api", "cdrom_bootloader"):
                cdrom_bootloader = self.cp.get("imaging_api", "cdrom_bootloader")
            if self.cp.has_option("imaging_api", "bootsplash_file"):
                bootsplash_file = self.cp.get("imaging_api", "bootlsplash_file")
            if self.cp.has_option("imaging_api", "bootmenus_folder"):
                bootmenus_folder = self.cp.get("imaging_api", "bootmenus_folder")
            if self.cp.has_option("imaging_api", "diskless_folder"):
                diskless_folder = self.cp.get("imaging_api", "diskless_folder")
            if self.cp.has_option("imaging_api", "davos_options"):
                davos_options = self.cp.get("imaging_api", "davos_options")
            if self.cp.has_option("imaging_api", "tools_folder"):
                tools_folder = self.cp.get("imaging_api", "tools_folder")
            if self.cp.has_option("imaging_api", "diskless_kernel"):
                diskless_kernel = self.cp.get("imaging_api", "diskless_kernel")
            if self.cp.has_option("imaging_api", "diskless_initrd"):
                diskless_initrd = self.cp.get("imaging_api", "diskless_initrd")
            if self.cp.has_option("imaging_api", "diskless_initrdcd"):
                diskless_initrdcd = self.cp.get("imaging_api", "diskless_initrdcd")
            if self.cp.has_option("imaging_api", "computers_folder"):
                computers_folder = self.cp.get("imaging_api", "computers_folder")
            if self.cp.has_option("imaging_api", "inventories_folder"):
                inventories_folder = self.cp.get("imaging_api", "inventories_folder")

            if self.cp.has_option("imaging_api", "pxe_mask"):
                pxe_mask = self.cp.get("imaging_api", "pxe_mask")
            else:
                pxe_mask = self.public_mask

            if self.cp.has_option("imaging_api", "pxe_tftp_ip"):
                pxe_tftp_ip = self.cp.get("imaging_api", "pxe_tftp_ip")
            else:
                pxe_tftp_ip = self.public_ip

            if self.cp.has_option("imaging_api", "pxe_subnet"):
                pxe_subnet = self.cp.get("imaging_api", "pxe_subnet")
            else:
                a, b = subnetForIpMask(pxe_tftp_ip, pxe_mask)
                pxe_subnet = b

            if self.cp.has_option("imaging_api", "pxe_gateway"):
                pxe_gateway = self.cp.get("imaging_api", "pxe_gateway")
            else:
                pxe_gateway = self.public_ip
            pxe_debug = ""
            if self.cp.has_option("imaging_api", "pxe_debug"):
                if self.cp.getboolean("imaging_api", "pxe_debug"):
                    pxe_debug = "debug"

            pxe_xml = ""
            if self.cp.has_option("imaging_api", "pxe_xml"):
                if self.cp.getboolean("imaging_api", "pxe_xml"):
                    pxe_xml = "xml"

            if self.cp.has_option("imaging_api", "latence"):
                pxe_latence = self.cp.getfloat("imaging_api", "latence")
            else:
                pxe_latence = 0.9

            if self.cp.has_option("imaging_api", "pxe_time"):
                pxe_time = self.cp.get("imaging_api", "pxe_time")
            else:
                pxe_time = "2"

            if self.cp.has_option("imaging_api", "masters_folder"):
                masters_folder = self.cp.get("imaging_api", "masters_folder")
            if self.cp.has_option("imaging_api", "postinst_folder"):
                postinst_folder = self.cp.get("imaging_api", "postinst_folder")
            if self.cp.has_option("imaging_api", "archives_folder"):
                archives_folder = self.cp.get("imaging_api", "archives_folder")
            if self.cp.has_option("imaging_api", "isos_folder"):
                isos_folder = self.cp.get("imaging_api", "isos_folder")
            if self.cp.has_option("imaging_api", "isogen_tool"):
                isogen_tool = self.cp.get("imaging_api", "isogen_tool")
            if self.cp.has_option("imaging_api", "uuid_cache_file"):
                uuid_cache_file = os.path.join(
                    base_folder, self.cp.get("imaging_api", "uuid_cache_file")
                )
            if self.cp.has_option("imaging_api", "uuid_cache_lifetime"):
                uuid_cache_lifetime = self.cp.getint(
                    "imaging_api", "uuid_cache_lifetime"
                )
            if self.cp.has_option("imaging_api", "rpc_replay_file"):
                rpc_replay_file = os.path.join(
                    base_folder, self.cp.get("imaging_api", "rpc_replay_file")
                )
            if self.cp.has_option("imaging_api", "rpc_loop_timer"):
                rpc_loop_timer = self.cp.getint("imaging_api", "rpc_loop_timer")
            if self.cp.has_option("imaging_api", "rpc_count"):
                rpc_count = self.cp.getint("imaging_api", "rpc_count")
            if self.cp.has_option("imaging_api", "rpc_interval"):
                rpc_interval = self.cp.getint("imaging_api", "rpc_interval")
            if self.cp.has_option("imaging_api", "uuid"):
                uuid = self.cp.get("imaging_api", "uuid")
            if self.cp.has_option("imaging_api", "glpi_mode"):
                glpi_mode = self.cp.get("imaging_api", "glpi_mode")
            if self.cp.has_option("imaging_api", "pxe_port"):
                pxe_port = self.cp.get("imaging_api", "pxe_port")
            if self.cp.has_option("imaging_api", "inventory_host"):
                inventory_host = self.cp.get("imaging_api", "inventory_host")
            if self.cp.has_option("imaging_api", "inventory_port"):
                inventory_port = self.cp.get("imaging_api", "inventory_port")
            if self.cp.has_option("imaging_api", "inventory_enablessl"):
                inventory_enablessl = self.cp.get("imaging_api", "inventory_enablessl")
            if not isUUID(uuid):
                raise TypeError(
                    "'%s' is not an valid UUID : in my config file, section [imaging_api], set a correct uuid."
                    % uuid
                )

            self.imaging_api = {
                "mount_point": imaging_mp,
                "base_folder": base_folder,
                "bootloader_folder": bootloader_folder,
                "bootsplash_file": bootsplash_file,
                "bootmenus_folder": bootmenus_folder,
                "cdrom_bootloader": cdrom_bootloader,
                "diskless_folder": diskless_folder,
                "davos_options": davos_options,
                "tools_folder": tools_folder,
                "diskless_kernel": diskless_kernel,
                "diskless_initrd": diskless_initrd,
                "diskless_initrdcd": diskless_initrdcd,
                "computers_folder": computers_folder,
                "inventories_folder": inventories_folder,
                "pxe_mask": pxe_mask,
                "pxe_tftp_ip": pxe_tftp_ip,
                "pxe_subnet": pxe_subnet,
                "pxe_gateway": pxe_gateway,
                "pxe_debug": pxe_debug,
                "pxe_xml": pxe_xml,
                "pxe_latence": pxe_latence,
                "pxe_time": pxe_time,
                "masters_folder": masters_folder,
                "postinst_folder": postinst_folder,
                "archives_folder": archives_folder,
                "isos_folder": isos_folder,
                "isogen_tool": isogen_tool,
                "pxe_port": pxe_port,
                "inventory_host": inventory_host,
                "inventory_port": inventory_port,
                "inventory_enablessl": inventory_enablessl,
                "glpi_mode": glpi_mode,
                "uuid": uuid,
                "uuid_cache_file": uuid_cache_file,
                "uuid_cache_lifetime": uuid_cache_lifetime,
                "rpc_replay_file": rpc_replay_file,
                "rpc_loop_timer": rpc_loop_timer,
                "rpc_count": rpc_count,
                "rpc_interval": rpc_interval,
            }

        if self.cp.has_option("main", "package_detect_activate"):
            # WARN this must overide the previously defined activate if it is
            # in the config file
            self.package_detect_activate = self.cp.getboolean(
                "main", "package_detect_activate"
            )
            if self.package_detect_activate and self.cp.has_option(
                "main", "package_detect_loop"
            ):
                self.package_detect_loop = self.cp.getint("main", "package_detect_loop")

            if self.cp.has_option("main", "package_detect_smart_method"):
                package_detect_smart_method = self.cp.get(
                    "main", "package_detect_smart_method"
                )
                if package_detect_smart_method != "none":
                    package_detect_smart_method = package_detect_smart_method.split(",")
                    self.package_detect_smart = True
                    if "last_time_modification" in package_detect_smart_method:
                        self.package_detect_smart_method.append(self.SMART_DETECT_LAST)
                    if "check_in_loop" in package_detect_smart_method:
                        self.package_detect_smart_method.append(self.SMART_DETECT_LOOP)
                    if "check_size" in package_detect_smart_method:
                        self.package_detect_smart_method.append(self.SMART_DETECT_SIZE)
                    else:
                        logging.getLogger().info(
                            "dont know the package_detect_smart_method '%s'"
                        )
                    if self.cp.has_option("main", "package_detect_smart_time"):
                        self.package_detect_smart_time = self.cp.getint(
                            "main", "package_detect_smart_time"
                        )
                else:
                    self.package_detect_smart = False

        if self.cp.has_option("main", "package_mirror_target"):
            self.package_mirror_target = self.cp.get(
                "main", "package_mirror_target"
            ).split(" ")
            if (
                (
                    isinstance(self.package_mirror_target, str)
                    and self.package_mirror_target != ""
                )
                or (
                    isinstance(self.package_mirror_target, list)
                    and len(self.package_mirror_target) == 1
                    and self.package_mirror_target[0] != ""
                )
                or (
                    isinstance(self.package_mirror_target, list)
                    and len(self.package_mirror_target) != 1
                )
            ):
                self.package_mirror_activate = True

                if self.cp.has_option("main", "package_mirror_status_file"):
                    self.package_mirror_status_file = self.cp.get(
                        "main", "package_mirror_status_file"
                    )
                if self.cp.has_option("main", "package_mirror_loop"):
                    self.package_mirror_loop = self.cp.getint(
                        "main", "package_mirror_loop"
                    )

                if self.cp.has_option("main", "package_mirror_command"):
                    self.package_mirror_command = self.cp.get(
                        "main", "package_mirror_command"
                    )
                if self.cp.has_option("main", "package_mirror_command_options"):
                    self.package_mirror_command_options = self.cp.get(
                        "main", "package_mirror_command_options"
                    ).split(" ")
                if self.cp.has_option(
                    "main", "package_mirror_command_options_ssh_options"
                ):
                    self.package_mirror_command_options_ssh_options = self.cp.get(
                        "main", "package_mirror_command_options_ssh_options"
                    ).split(" ")
                if self.cp.has_option("main", "package_mirror_level0_command_options"):
                    self.package_mirror_level0_command_options = self.cp.get(
                        "main", "package_mirror_level0_command_options"
                    ).split(" ")

            if self.cp.has_option("main", "package_global_mirror_activate"):
                self.package_global_mirror_activate = self.cp.getboolean(
                    "main", "package_global_mirror_activate"
                )
                if self.cp.has_option("main", "package_global_mirror_loop"):
                    self.package_global_mirror_loop = self.cp.getint(
                        "main", "package_global_mirror_loop"
                    )
                if self.cp.has_option("main", "package_global_mirror_command_options"):
                    self.package_global_mirror_command_options = self.cp.get(
                        "main", "package_global_mirror_command_options"
                    ).split(" ")

        if self.cp.has_option("main", "real_package_deletion"):
            self.real_package_deletion = self.cp.getboolean(
                "main", "real_package_deletion"
            )
        if self.cp.has_option("main", "mm_assign_algo"):
            self.mm_assign_algo = self.cp.get("main", "mm_assign_algo")
        if self.cp.has_option("main", "up_assign_algo"):
            self.up_assign_algo = self.cp.get("main", "up_assign_algo")


def config_addons(conf):
    if len(conf.mirrors) > 0:
        #        for mirror_params in conf.mirrors:
        list([add_access(x, conf) for x in conf.mirrors])
    if len(conf.package_api_get) > 0:
        #        for mirror_params in conf.package_api_get:
        list([add_server(x, conf) for x in conf.package_api_get])
    return conf


def add_access(mirror_params, conf):
    mirror_params["port"] = conf.port
    mirror_params["server"] = conf.public_ip
    mirror_params["file_access_path"] = "%s_files" % (mirror_params["mount_point"])
    mirror_params["file_access_uri"] = conf.public_ip
    mirror_params["file_access_port"] = conf.port
    return mirror_params


def add_server(mirror_params, conf):
    mirror_params["port"] = conf.port
    mirror_params["server"] = conf.public_ip
    return mirror_params
