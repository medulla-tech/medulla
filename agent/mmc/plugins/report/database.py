# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com
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
from time import time

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.exc import NoResultFound

from mmc.database.database_helper import DatabaseHelper
from mmc.plugins.report.schema import ReportingData, Indicator


logger = logging.getLogger()


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
        if self.is_activated:
            return None

        logger.info("Report database is connecting")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        # Uncomment this line to connect to mysql and parse tables
        self.is_activated = True
        logger.debug("Report database connected")
        return True

    def initMappers(self):
        """
        This Method is nomore need, all tables are mapped on schema.py
        """
        return

    @DatabaseHelper._session
    def get_indicator_by_name(self, session, name):
        try:
            return session.query(Indicator).filter_by(name=name).one()
        except NoResultFound:
            logger.error("Can't find indicator %s in the DB" % name)
            return False

    @DatabaseHelper._session
    def add_indicator(self, session, indicator_attr):
        try:
            indicator = session.query(Indicator).filter_by(name = indicator_attr['name']).first()
            if indicator:
                indicator.fromDict(indicator_attr)
            else:
                logger.info('Adding new indicator %s' % indicator_attr['name'])
                indicator = Indicator(**indicator_attr)
                session.add(indicator)
            session.commit()
        except:
            logger.exception("Failed to add indicator with values %s" % indicator_attr)
            return False
        return True

    @DatabaseHelper._session
    def historize_indicator(self, session, name):
        indicator = self.get_indicator_by_name(name)
        # TODO: Test if history is 1 if not WARNING
        # Save the indicator values to Db
        for entry in indicator.getCurrentValue():
            data = ReportingData()
            # Import value and enity_id from entry
            data.fromDict(entry)
            data.indicator_id = indicator.id
            data.timestamp = int(time())
            session.add(data)
        session.commit()

    @DatabaseHelper._session
    def historize_all(self, session):
        indicators = session.query(Indicator).filter_by(active=1, keep_history=1).all()
        for indicator in indicators:
            # Save the indicator values to Db
            try:
                values = indicator.getCurrentValue()
            except:
                logger.exception('Unable to get data for indicator : %s' % indicator.name)
                continue
            for entry in values:
                data = ReportingData()
                # Import value and enity_id from entry
                data.fromDict(entry)
                data.indicator_id = indicator.id
                data.timestamp = int(time())
                session.add(data)
        session.commit()

    @DatabaseHelper._session
    def get_indicator_value_at_time(self, session, indicator_name, ts_min, ts_max, entities):
        indicator = self.get_indicator_by_name(indicator_name)
        if indicator:
            return indicator.getValueAtTime(session, ts_min, ts_max, entities)

    @DatabaseHelper._session
    def get_indicator_datatype(self, session, indicator_name):
        indicator = self.get_indicator_by_name(indicator_name)
        if indicator:
            return indicator.data_type

    @DatabaseHelper._session
    def get_indicator_current_value(self, session, indicator_name, entities=[]):
        indicator = self.get_indicator_by_name(indicator_name)
        if indicator:
            return indicator.getCurrentValue(entities)
