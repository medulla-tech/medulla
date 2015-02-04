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


