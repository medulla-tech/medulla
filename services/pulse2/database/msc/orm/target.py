# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
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

""" Class to map msc.target to SA
"""
import re
import sqlalchemy
import logging

re_file_prot = re.compile('^file://')
re_http_prot = re.compile('^http://')
re_https_prot = re.compile('^https://')


class Target(object):
    """ Mapping between msc.target and SA
    """
    def flush(self):
        """ Handle SQL flushing """
        session = sqlalchemy.create_session()
        session.add(self)
        session.flush()
        session.close()

    def getId(self):
        return self.id

    def getUUID(self):
        return self.target_uuid

    def getFQDN(self):
        return self.target_name

    def getShortName(self):
        try :
            return self.target_name.split(".")[0]
        except :
            logging.getLogger().warn("Unable to get shortname from '%s'" % self.target_name)
            return self.target_name

    def getIps(self):
        return self.target_ipaddr.split('||')

    def getMacs(self):
        return self.target_macaddr.split('||')

    def getBCast(self):
        return self.target_bcast.split('||')

    def getNetmasks(self):
        return self.target_network.split('||')


    def hasEnoughInfoToWOL(self):
        # to perform a WOL, we need two informations:
        # - at least one MAC address
        # - at least one IP network broadcast
        # FIXME: ATM the test is rather simple : count items len
        mac_len = reduce(lambda x,y: x+y, map(lambda x: len(x), self.getMacs()))
        bcast_len = reduce(lambda x,y: x+y, map(lambda x: len(x), self.getBCast()))
        result = (mac_len > 0 ) and (bcast_len > 0)
        logging.getLogger().debug("hasEnoughInfoToWOL(#%s): %s" % (self.id, result))
        return result

    def hasEnoughInfoToConnect(self):
        # to establish, we need one information :
        # - either at least one hostname
        # - or at least one IP address
        # FIXME: ATM the test is rather simple : count items len
        ips_len = reduce(lambda x,y: x+y, map(lambda x: len(x), self.getIps()))
        names_len = len(self.getFQDN())
        result = (ips_len > 0 ) or (names_len > 0)
        logging.getLogger().debug("hasEnoughInfoToConnect(#%s): %s" % (self.id, result))
        return result

    def hasFileMirror(self):
        return re_file_prot.match(self.mirrors)

    def hasHTTPMirror(self):
        mirrors = self.mirrors.split('||')
        mirror = mirrors[0] # TODO: handle when several mirrors are available
        return re_http_prot.match(mirror) or re_https_prot.match(mirror)


    def toH(self):
        return {
            'id': self.id,
            'target_name': self.target_name,
            'target_uuid': self.target_uuid,
            'target_ipaddr': self.target_ipaddr,
            'target_macaddr': self.target_macaddr,
            'target_bcast': self.target_bcast,
            'mirrors': self.mirrors,
            'id_group': self.id_group
        }
