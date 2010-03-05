# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
#
# $Id: mirror_api.py 689 2009-02-06 15:18:43Z oroussy $
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""
this module just prvide a method to create an API url from a dict.
"""


def makeURL(config):
    credentials = ''
    if 'proto' in config and not 'enablessl' in config:
        uri = "%s://" % config['proto']
    elif 'protocol' in config and not 'enablessl' in config:
        uri = "%s://" % config['protocol']
    else:
        if 'enablessl' in config and config['enablessl']:
            uri = 'https://'
        else:
            uri = 'http://'
    if 'username' in config and config['username'] != '':
        uri += '%s:%s@' % (config['username'], config['password'])
        credentials = '%s:%s' % (config['username'], config['password'])
    if 'server' in config and not 'host' in config:
        config['host'] = config['server']
    uri += '%s:%d' % (config['host'], int(config['port']))
    return (uri, credentials)
