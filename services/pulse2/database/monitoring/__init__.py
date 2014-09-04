# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
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
Monitoring database handler
"""

# SqlAlchemy
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
from sqlalchemy.exc import DBAPIError


# PULSE2 modules
from mmc.database.database_helper import DatabaseHelper
from pulse2.database.monitoring.schema import Monitoring_detection, Monitoring_options

# Imported last
import logging

# Convert IP to INT for database
import socket, struct

logger = logging.getLogger()


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))




class MonitoringDatabase(DatabaseHelper):
    """
    Singleton Class to query the backuppc database.

    """
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "monitoring"
        self.configfile = "monitoring.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Monitoring database is connecting")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        self.logger.debug("Monitoring database connected (version:%s)"%(self.db_version))
        return True


    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the Monitoring database
        """
        # No mapping is needed, all is done on schema file
        return


    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError, e:
                self.logger.error(e)
            except Exception, e:
                self.logger.error(e)
            if ret: break
        if not ret:
            raise "Database connection error"
        return ret

    # =====================================================================
    # MONITORING DISCOVERY FUNCTIONS
    # =====================================================================

    @DatabaseHelper._session
    def get_discover_host_os(self, session, _ip):
        host = session.query(Monitoring_detection).filter_by(ip = _ip).one()
        if not host:
            logger.warning("Can't find configured host with ip = %s" % _ip)
            return -1
        else:
            return host.os

    @DatabaseHelper._session
    def get_discover_host_all(self, session):
        host = session.query(Monitoring_detection).all()
        if not host:
            logger.warning("Can't find any host")
            return -1
        else:
	    return [row.toDict() for row in host]

    @DatabaseHelper._session
    def add_discover_host(self, session, _os, _ip):
        table = Monitoring_detection(ip = "192.168.2.3", os = "yzduzdbzudb")
	#ip = ip2int(_ip)
        #table.os = _os
	#table.ip = _ip
        session.add(table)
        session.flush()
	return table.toDict()

