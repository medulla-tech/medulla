# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Declare Report database
"""

import logging
import time

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm.exc import NoResultFound

from mmc.database.database_helper import DatabaseHelper
from mmc.plugins.report.schema import Indicator, ReportingIntData, ReportingTextData, ReportingFloatData


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
        self.db = create_engine(self.makeConnectionPath(),
                                pool_recycle=self.config.dbpoolrecycle,
                                pool_size=self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        # Uncomment this line to connect to mysql and parse tables
        self.is_activated = True
        logger.debug("Report database connected")
        if not self.db_check():
            return self.db_update()
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
    def disable_indicators_by_name(self, session, includes=[], excludes=[]):
        ## Mutable list includes used as default argument to a method or function
        #includes = includes or []
        ## Mutable list excludes used as default argument to a method or function
        #excludes = excludes or []
        try:
            query = session.query(Indicator)
            if includes:
                query = query.filter(Indicator.name.in_(includes))
            if excludes:
                query = query.filter(~Indicator.name.in_(excludes))
            query.update({'active':0, 'keep_history':0}, synchronize_session=False)
            session.commit()
            return True
        except Exception, e:
            logger.error('DB Error: %s', str(e))

    @DatabaseHelper._session
    def add_indicator(self, session, indicator_attr):
        try:
            indicator = session.query(Indicator).filter_by(name=indicator_attr['name']).first()
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
    def historize_indicator(self, session, name, timestamp):
        indicator = self.get_indicator_by_name(name)
        # TODO: Test if history is 1 if not WARNING
        # Save the indicator values to Db
        for entry in indicator.getCurrentValue():
            data = indicator.dataClass()
            # Import value and enity_id from entry
            data.fromDict(entry)
            data.indicator_id = indicator.id
            data.timestamp = timestamp
            session.add(data)
        session.commit()

    @DatabaseHelper._session
    def historize_all(self, session, timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        indicators = session.query(Indicator).filter_by(active=1, keep_history=1)
        for indicator in indicators:
            # Save the indicator values to Db
            try:
                values = indicator.getCurrentValue()
            except:
                logger.exception('Unable to get data for indicator : %s' % indicator.name)
                continue
            for entry in values:
                if not 'value' in entry:
                    continue
                if entry['value'] is None:
                    entry['value'] = 0
                data = indicator.dataClass()
                # Import value and enity_id from entry
                data.fromDict(entry)
                data.indicator_id = indicator.id
                data.timestamp = timestamp
                session.add(data)
        session.commit()


    @DatabaseHelper._session
    def historize_overwrite_last(self, session, timestamp):
        """
        Debug function to historize and overwrite last historization data
        """

        # Remove last 24 hours data
        for _class in [ReportingIntData, ReportingTextData, ReportingFloatData]:
            session.query(_class).filter(_class.timestamp>timestamp-86400).delete()

        # Doing an historization for
        self.historize_all(timestamp-80400)

    @DatabaseHelper._session
    def get_indicator_value_at_time(self, session, indicator_name, ts_min, ts_max, entities=[]):
        ## Mutable list entities used as default argument to a method or function
        #entities = entities or []
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
        # Mutable list entities used as default argument to a method or function
        #entities = entities or []
        indicator = self.get_indicator_by_name(indicator_name)
        if indicator:
            return indicator.getCurrentValue(entities)
