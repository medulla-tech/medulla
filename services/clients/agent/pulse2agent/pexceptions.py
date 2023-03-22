# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

class SmartAgentError(Exception):
    def __init__(self, name):
        self.name = name


class SoftwareRequestError(SmartAgentError):
    def __repr__(self):
        return "Request to get %s failed" % self.name


class SoftwareCheckError(SmartAgentError):

    def __repr__(self):
        return "Unable to check installed software: %s" % self.name

class ConnectionError(SmartAgentError):
    def __repr__(self):
        return "Request to server %s failed" % self.name

class SoftwareInstallError(SmartAgentError):

    def __repr__(self):
        return "Unable to install software: %s" % self.name

class PackageDownloadError(SmartAgentError):

    def __repr__(self):
        return "Unable to download the package: %s" % self.name
