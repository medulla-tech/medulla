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


from pulse2.cm._config import ConfigReader


class Config(object):
    __metaclass__ = ConfigReader

    class daemon(object):
        umask = 0077
        user = 0
        group = 0
        pidfile = "/var/run/pulse2-cm.pid"

    class main(object):
        serializer = "json"

    class server(object):

        port = 443
        ssl_key_file = None
        ssl_crt_file = None
        ssl_method = "SSLv3_METHOD"

        endpoints = ["packages", "inventory","vpn_install"]

    class inventory(object):
        enablessl = False
        host = "localhost"
        port = 9999

        inscription_lag = 12

    class mmc(object):
        enablessl = True
        host = "localhost"
        port = 7080
        user = "mmc"
        passwd = "s3cr3t"
        ldap_user = "root"
        ldap_passwd = "ldap"

    class vpn(object):
        scripts_path = "/var/lib/pulse2/clients/vpn"

    class logging(object):
        level = "DEBUG"
        filename = "/var/log/mmc/pulse2-cm.log"

    class loggers(object):
        keys = "root"

    class handlers(object):
        keys= "hand01"

    class formatters(object):
        keys = "form01"

    class logger_root(object):
        level = "NOTSET"
        handlers = "hand01"

    class handler_hand01(object):
        class_ = "handlers.TimedRotatingFileHandler"
        level = "INFO"
        formatter = "form01"
        args = ("/var/log/mmc/pulse2-cm.log", 'midnight', 1, 7)

    class formatter_form01(object):
        format = "%(asctime)s %(levelname)s %(message)s"

