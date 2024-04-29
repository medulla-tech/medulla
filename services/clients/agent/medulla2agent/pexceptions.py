# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2014 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


class SmartAgentError(Exception):
    def __init__(self, name):
        self.name = name


class SoftwareRequestError(SmartAgentError):
    def __repr__(self):
        return f"Request to get {self.name} failed"


class SoftwareCheckError(SmartAgentError):
    def __repr__(self):
        return f"Unable to check installed software: {self.name}"


class ConnectionError(SmartAgentError):
    def __repr__(self):
        return f"Request to server {self.name} failed"


class SoftwareInstallError(SmartAgentError):
    def __repr__(self):
        return f"Unable to install software: {self.name}"


class PackageDownloadError(SmartAgentError):
    def __repr__(self):
        return f"Unable to download the package: {self.name}"
