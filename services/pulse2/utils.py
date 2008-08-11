# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: config.py 57 2008-07-17 13:36:26Z oroussy $
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

from ConfigParser import * # to build Pulse2ConfigParser on top of ConfigParser()

class Singleton(object):
    """
        Duplicate from the Singleton() class from the MMC Project,
        to remove unwanted dependancies
    """
    def __new__(type):
        if not '_the_instance' in type.__dict__:
            type._the_instance = object.__new__(type)
        return type._the_instance

class Pulse2ConfigParser(ConfigParser):
    """
        Duplicate from the MMCConfigParser() class from the MMC Project,
        to remove unwanted dependancies
    """

    def __init__(self):
        ConfigParser.__init__(self)

    def getpassword(self, section, option):
        """
        Like get, but interpret the value as a obfuscated password if a
        password scheme is specified.

        For example: passwd = {base64}bWFuL2RyaXZhMjAwOA==
        """
        value = self.get(section, option)
        m = re.search('^{(\w+)}(.+)$', value)
        if m:
            scheme = m.group(1)
            obfuscated = m.group(2)
            ret = obfuscated.decode(scheme)
        else:
            ret = value
        return ret


