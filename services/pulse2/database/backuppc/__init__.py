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
BackupPC database handler
"""

# SqlAlchemy
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import create_session, mapper
from sqlalchemy.orm import sessionmaker; Session = sessionmaker()
from sqlalchemy.exc import DBAPIError


# PULSE2 modules
from pulse2.database import database_helper
from pulse2.database.database_helper import DatabaseHelper
from pulse2.database.backuppc.schema import Backup_profiles, Period_profiles, Backup_servers, Hosts

# Imported last
import logging

logger = logging.getLogger()


class BackuppcDatabase(DatabaseHelper):
    """
    Singleton Class to query the backuppc database.

    """
    is_activated = False
    session = None

    def db_check(self):
        self.my_name = "backuppc"
        self.configfile = "backuppc.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        self.logger = logging.getLogger()
        if self.is_activated:
            return None

        self.logger.info("BackupPC database is connecting")
        self.config = config
        self.db = create_engine(self.makeConnectionPath(), pool_recycle = self.config.dbpoolrecycle, pool_size = self.config.dbpoolsize)
        self.metadata = MetaData(self.db)
        if not self.initMappersCatchException():
            self.session = None
            return False
        self.metadata.create_all()
        self.is_activated = True
        self.logger.debug("BackupPC database connected (version:%s)"%(self.db_version))
        return True


    @property
    def db_version(self):
        return self.db.execute("select Number from version").scalar()

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the BackupPC database
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
    # BACKUP PROFILES FUNCTIONS
    # =====================================================================

    def _session(func):
        def __session(self, *args, **kw):
            if not self.session:
                self.session = Session(bind=self.db)
            result = func(self, self.session,*args, **kw)
            self.session.close()
            self.session = None
            return result
        return __session

    @_session
    def get_backup_profiles(self, session):
        ret = session.query(Backup_profiles).all()
        return [row.toDict() for row in ret]

    @_session
    def add_backup_profile(self, session, _profile):
        profile = Backup_profiles()
        profile.fromDict(_profile)
        session.add(profile)
        session.flush()
        return profile.toDict()

    @_session
    def delete_backup_profile(self, session, id):
        ret = session.query(Backup_profiles).get(int(id))
        session.delete(ret)
        session.flush()

    @_session
    def edit_backup_profile(self, session, id, override):
        ret = session.query(Backup_profiles).get(int(id))
        if ret:
            ret.fromDict(override)
            session.flush()
            return ret.toDict()
        else:
            logger.warning("Can't find backup profile with id = %d" % id)
            return False

    # =====================================================================
    # PERIOD PROFILES FUNCTIONS
    # =====================================================================

    @_session
    def get_period_profiles(self, session):
        ret = session.query(Period_profiles).all()
        return [row.toDict() for row in ret]

    @_session
    def add_period_profile(self, session, _profile):
        profile = Period_profiles()
        profile.fromDict(_profile)
        session.add(profile)
        session.flush()
        return profile.toDict()


    @_session
    def delete_period_profile(self, session, id):
        ret = session.query(Period_profiles).get(int(id))
        session.delete(ret)
        session.flush()

    @_session
    def edit_period_profile(self, session, id,override):
        ret = session.query(Period_profiles).get(int(id))
        if ret:
            ret.fromDict(override)
            session.flush()
            return ret.toDict()
        else:
            logger.warning("Can't find backup profile with id = %d" % id)
            return False

    # =====================================================================
    # HOSTS TABLE FUNCTIONS
    # =====================================================================

    @_session
    def get_all_hosts(self, session):
        ret = session.query(Hosts).all()
        return [row.toDict() for row in ret]

    @_session
    def get_host_backup_profile(self, session, uuid):
        host = session.query(Hosts).filter_by(uuid = uuid).one()
        if not host:
            logger.warning("Can't find configured host with uuid = %s" % uuid)
            return -1
        else:
            return host.backup_profile

    @_session
    def set_host_backup_profile(self, session, uuid, newprofile):
        host = session.query(Hosts).filter_by(uuid = uuid).one()
        if host:
            host.backup_profile = newprofile
            session.flush()
        return host != None

    @_session
    def get_host_period_profile(self, session, uuid):
        host = session.query(Hosts).filter_by(uuid = uuid).one()
        if not host:
            logger.warning("Can't find configured host with uuid = %s" % uuid)
            return -1
        else:
            return host.period_profile

    @_session
    def set_host_period_profile(self, session, uuid, newprofile):
        ret = session.query(Hosts).filter_by(uuid = uuid).one()
        if ret:
            ret.period_profile = newprofile
            session.flush()
        return ret != None

    @_session
    def get_hosts_by_backup_profile(self, session, profileid):
        ret = session.query(Hosts.uuid).filter_by(backup_profile = profileid).all()
        if ret:
            return [m[0] for m in ret]
        else:
            return []


    @_session
    def get_hosts_by_period_profile(self, session, profileid):
        ret = session.query(Hosts.uuid).filter_by(period_profile = profileid).all()
        if ret:
            return [m[0] for m in ret]
        else:
            return []

    # =====================================================================
    # HOSTS TABLE FUNCTIONS
    # =====================================================================

    @_session
    def add_host(self, session, uuid):
        host = Hosts(uuid = uuid)
        # Setting host fields
        host.backup_profile = 0
        host.period_profile = 0
        session.add(host)
        session.flush()
        return host.toDict()

    @_session
    def remove_host(self, session, uuid):
        try:
            ret = session.query(Hosts).filter_by(uuid = uuid.upper()).one()
            if ret:
                session.delete(ret)
                session.flush()
            return True
        except Exception, e:
            logger.error("Can't remove host where uuid=%s" % uuid)
            logger.error(str(e))

    @_session
    def host_exists(self, session, uuid):
        try:
            ret = session.query(Hosts).filter_by(uuid = uuid.upper()).all()
            return len(ret) == 1
        except Exception, e:
            logger.error("Database error: %s " % str(e))


    # =====================================================================
    # BACKUP SERVER FUNCTIONS
    # =====================================================================

    @_session
    def get_backupserver_by_entity(self, session, entity_uuid):
        try:
            ret = session.query(Backup_servers.backupserver_url).filter_by(entity_uuid = entity_uuid).one()
            if ret: return ret.backupserver_url
        except:
            ret = ''
        return ret

    # =====================================================================

    @_session
    def get_backupservers_list(self, session):
        ret = session.query(Backup_servers).all()
        return [row.toDict() for row in ret]


    @_session
    def add_backupserver(self, session, entityuuid, serverURL):
        server = Backup_servers(entity_uuid = entityuuid, backupserver_url = serverURL)
        session.add(server)
        session.flush()
        return server.toDict()

    @_session
    def remove_backupserver(self, session, entityuuid):
        ret = session.query(Backup_servers).filter_by(entity_uuid = entityuuid).first()
        if ret:
            session.delete(ret)
            session.flush()
            return True
        else:
            logger.warning("Can't find BackupServer associated to entity %s" % entityuuid)