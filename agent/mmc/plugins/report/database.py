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
from time import time

from mmc.database.database_helper import DatabaseHelper, DBObj

from sqlalchemy import (create_engine, MetaData, Table, Integer, Column,
                        DateTime, and_)
from sqlalchemy.orm import create_session, mapper

from mmc.plugins.report.schema import ReportingData, Indicator


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
        self.is_activated = True
        self.logger.debug("Report database connected")
        return True

    def initMappers(self):
        """
        This Method is nomore need, all tables are mapped on schema.py
        """
        return


    @DatabaseHelper._session
    def get_indicator_by_name(self, session, name):
        return session.query(Indicator).filter_by(name = name).one()

    @DatabaseHelper._session
    def historize_indicator(self, session, name):
        indicator = self.get_indicator_by_name(name)
        # TODO: Test if history is 1 if not WARNING
        # Save the indicator values to Db
        for entry in indicator.getCurrentValue():
            data = ReportingData()
            # Import value and enity_id from entry
            data.fromDict(entry)
            #
            data.indicator_id = indicator.id
            data.timestamp = int(time())
            session.add(data)
        session.commit()

    @DatabaseHelper._session
    def historize_all(self, session):
        indicators = session.query(Indicator).filter_by(active = 1, keep_history = 1).all()
        for indicator in indicators:
            # Save the indicator values to Db
            try:
                values = indicator.getCurrentValue()
            except Exception, e:
                logging.getLogger().warning('Unable to get data for indicator : %s' % indicator.name )
                logging.getLogger().warning(str(e))
                continue
            #
            for entry in values:
                data = ReportingData()
                # Import value and enity_id from entry
                data.fromDict(entry)
                #
                data.indicator_id = indicator.id
                data.timestamp = int(time())
                session.add(data)
        session.commit()

    def feed_db(self):
        logging.getLogger().debug('Successfully feeded Report database')
        return True

    @DatabaseHelper._session
    def get_indicator_value_at_time(self, session, indicator_name, ts_min, ts_max, entities): #'2013-10-29', ['UUID1']
        return self.get_indicator_by_name(indicator_name).getValueAtTime(session, ts_min, ts_max , entities)

    @DatabaseHelper._session
    def get_indicator_current_value(self, session, name, entities = []):
        indicator = self.get_indicator_by_name(name)
        return indicator.getCurrentValue(entities)