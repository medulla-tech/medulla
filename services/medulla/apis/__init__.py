# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
this module just prvide a method to create an API url from a dict.
"""


def makeURL(config):
    credentials = ""
    if "proto" in config and "enablessl" not in config:
        uri = "%s://" % config["proto"]
    elif "protocol" in config and "enablessl" not in config:
        uri = "%s://" % config["protocol"]
    else:
        if "enablessl" in config and config["enablessl"]:
            uri = "https://"
        else:
            uri = "http://"
    if "username" in config and config["username"] != "":
        uri += "%s:%s@" % (config["username"], config["password"])
        credentials = "%s:%s" % (config["username"], config["password"])
    if "server" in config and "host" not in config:
        config["host"] = config["server"]
    uri += "%s:%d" % (config["host"], int(config["port"]))
    return (uri, credentials)
