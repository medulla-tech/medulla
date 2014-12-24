# -*- test-case-name: pulse2.msc.client.tests._config -*-
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

""" Declaration of config defaults """

from _config import ConfigReader

class Config(object):
    __metaclass__ = ConfigReader

    class main(object):
        serializer = "json"
        check_period = 10

    class server(type):
        host = "pulse2-server"
        port = 443
        keyfile = None
        crtfile = None
        timeout = 60
        enablessl = False

    class vpn(object):
        enabled = True
        host = "vpnhost"
        port = 443 
        command = "/opt/vpnclient"
        command_args = ["start",]
        certs_dir = "/etc/openvpn"

    class inventory(object):
        windows_reg_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        windows_software_required = ["Mandriva OpenSSH Agent",
                                     "FusionInventory Agent",
                                     "TightVNC",
                                     ]
        debian_software_required = ["pulse2-agents-installer",
                                    "fusioninventory-agent",
                                    ]
        debian_server_software_required = ["pulse2-agents-installer-nordp"
                                           "fusioninventory-agent",
                                           ]
        redhat_software_required = ["pulse2-agents-installer",
                                    "fusioninventory-agent",
                                    ]
        redhat_server_software_required = ["pulse2-agents-installer-nordp"
                                           "fusioninventory-agent",
                                           ]
        osx_required = ["org.pulse2-agents-installer",
                        ]
        
    class paths(object):
        package_tmp_dir_win = "C:\\Temp"
        package_tmp_dir_posix = "/tmp"


