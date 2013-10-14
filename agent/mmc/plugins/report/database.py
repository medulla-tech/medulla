# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2012 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Declare Report database
"""

import logging
from datetime import timedelta

from mmc.database.database_helper import DatabaseHelper, DBObject

from sqlalchemy import (create_engine, MetaData, Table, Integer, Column,
                        DateTime, and_)
from sqlalchemy.orm import create_session, mapper

class ReportDatabase(DatabaseHelper):
    """
    Singleton Class to query the report database.
    """
    is_activated = False

    def db_check(self):
        self.my_name = "report"
        self.configfile = "report.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("Report database is connecting")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        # Uncomment this line to connect to mysql and parse tables
        #self.metadata.create_all()
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("Report database connected")
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the Report database
        """
        # DiscSpace
        self.disc_space = Table("DiscSpace", self.metadata,
                                Column('id', Integer, primary_key = True),
                                Column('timestamp', DateTime),
                                Column('used', Integer),
                                Column('free', Integer),
                                mysql_engine='InnoDB'
                                )
        mapper(DiscSpace, self.disc_space)

        self.ram_usage = Table("RamUsage", self.metadata,
                                Column('id', Integer, primary_key = True),
                                Column('timestamp', DateTime),
                                Column('used', Integer),
                                Column('free', Integer),
                                mysql_engine='InnoDB'
                                )
        mapper(RamUsage, self.ram_usage)

    def feed_db(self):
        logging.getLogger().debug('Successfully feeded Report database')
        return True

    #################
    ## Report Methods
    #################

    def getDiscSpace(self, from_timestamp, to_timestamp, splitter):
        delta = to_timestamp - from_timestamp
        if delta.days < splitter:
            step = 1
        else:
            step = delta.days / splitter

        session = create_session()
        query = session.query(DiscSpace)
        query = query.filter(and_(
            DiscSpace.timestamp >= from_timestamp,
            DiscSpace.timestamp <= to_timestamp + timedelta(1),
        ))
        session.close()

        l = [(x.timestamp, x.used, x.free) for x in query.all()]

        res = {'titles': ['Used', 'Free']}
        for x in xrange(0, len(l), step):
            res[l[x][0].strftime('%s')] = [l[x][1], l[x][2]]

        return res

    def getRamUsage(self, from_timestamp, to_timestamp, splitter):
        delta = to_timestamp - from_timestamp
        if delta.days < splitter:
            step = 1
        else:
            step = delta.days / splitter

        session = create_session()
        query = session.query(RamUsage)
        query = query.filter(and_(
            RamUsage.timestamp >= from_timestamp,
            RamUsage.timestamp <= to_timestamp + timedelta(1),
        ))
        session.close()

        l = [(x.timestamp, x.used, x.free) for x in query.all()]

        res = {'titles': ['Used', 'Free']}
        for x in xrange(0, len(l), step):
            res[l[x][0].strftime('%s')] = [l[x][1], l[x][2]]

        return res

class DiscSpace(DBObject):
    pass
class RamUsage(DBObject):
    pass
