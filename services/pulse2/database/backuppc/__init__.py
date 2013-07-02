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
from sqlalchemy import create_engine, MetaData, Table #, Column, Text
from sqlalchemy.orm import create_session, mapper
from sqlalchemy.exc import DBAPIError

# PULSE2 modules
from pulse2.database import database_helper
from pulse2.database.database_helper import DatabaseHelper

# Imported last
import logging

logger = logging.getLogger()

def dbOjb2dict(obj):
    if isinstance(obj,list):
        result = []
        for record in obj:
            dct = record.__dict__
            if '_sa_instance_state' in dct: del dct['_sa_instance_state']
            for k in dct:
                dct[k] = str(dct[k])
            result += [dct]
        return result
    else:
        dct = obj.__dict__
        if '_sa_instance_state' in dct: del dct['_sa_instance_state']
        for k in dct:
            dct[k] = str(dct[k])
        return dct

class BackuppcDatabase(DatabaseHelper):
    """
    Singleton Class to query the backuppc database.

    """
    is_activated = False

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
        self.session = create_session()
        self.is_activated = True
        self.logger.debug("BackupPC database connected (version:%s)"%(self.version.select().execute().fetchone()[0]))
        return True

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the BackupPC database
        """
        # version
        self.version = Table("version", self.metadata, autoload = True)
        # Backup servers
        self.backup_servers = Table("backup_servers", self.metadata, autoload = True)
        mapper(Backup_servers, self.backup_servers)
        # Hosts
        self.hosts = Table("hosts", self.metadata, autoload = True)
        mapper(Hosts, self.hosts)
        # Backup profiles
        self.backup_profiles = Table("backup_profiles", self.metadata, autoload = True)
        mapper(Backup_profiles, self.backup_profiles)
        # Period profiles
        self.period_profiles = Table("period_profiles", self.metadata, autoload = True)
        mapper(Period_profiles, self.period_profiles)



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

    def get_backup_profiles(self):
        session = create_session()
        ret = session.query(Backup_profiles).all()
        session.close()
        return dbOjb2dict(ret) or []


    def add_backup_profile(self, _profile):
        session = create_session()
        profile = Backup_profiles()
        # Setting profile fields
        profile.profilename = _profile['profilename']
        profile.sharenames = _profile['sharenames']
        profile.excludes = _profile['excludes']
        profile.encoding = _profile['encoding']
        #
        session.add(profile)
        session.flush()
        session.close()
        return dbOjb2dict(profile) or {}


    def delete_backup_profile(self,id):
        session = create_session()
        id = int(id)
        ret = session.query(Backup_profiles).filter(Backup_profiles.id == id).first()
        if ret:
            session.delete(ret)
            session.flush()
        else:
            logger.warning("Can't find backup profile with id = %d" % id)
        session.close()

    def edit_backup_profile(self,id,override):
        session = create_session()
        id = int(id)
        ret = session.query(Backup_profiles).filter(Backup_profiles.id == id).first()
        if ret:
            # Setting all overrided fields
            for k,v in override.iteritems():
                setattr(ret,k,v)
            session.flush()
        else:
            logger.warning("Can't find backup profile with id = %d" % id)
        session.close()
        return dbOjb2dict(ret) or {}


    # =====================================================================
    # PERIOD PROFILES FUNCTIONS
    # =====================================================================

    def get_period_profiles(self):
        session = create_session()
        ret = session.query(Period_profiles).all()
        session.close()
        return dbOjb2dict(ret) or []


    def add_period_profile(self, _profile):
        session = create_session()
        profile = Period_profiles()
        # Setting profile fields
        profile.profilename = _profile['profilename']
        profile.full = _profile['full']
        profile.incr = _profile['incr']
        profile.exclude_periods = _profile['exclude_periods']
        #
        session.add(profile)
        session.flush()
        session.close()
        return dbOjb2dict(profile) or {}


    def delete_period_profile(self,id):
        session = create_session()
        id = int(id)
        ret = session.query(Period_profiles).filter(Period_profiles.id == id).first()
        if ret:
            session.delete(ret)
            session.flush()
        else:
            logger.warning("Can't find period profile with id = %d" % id)
        session.close()

    def edit_period_profile(self,id,override):
        id = int(id)
        session = create_session()
        ret = session.query(Period_profiles).filter(Period_profiles.id == id).first()
        if ret:
            # Setting all overrided fields
            for k,v in override.iteritems():
                setattr(ret,k,v)
            session.flush()
        else:
            logger.warning("Can't find period profile with id = %d" % id)
        session.close()
        return dbOjb2dict(ret) or {}

    # =====================================================================
    # HOSTS TABLE FUNCTIONS
    # =====================================================================

    def get_host_backup_profile(self,uuid):
        session = create_session()
        host = session.query(Hosts).filter(Hosts.uuid == uuid).first()
        session.close()
        if not host:
            logger.warning("Can't find configured host with uuid = %s" % uuid)
            return -1
        else:
            return host.backup_profile


    def set_host_backup_profile(self,uuid,newprofile):
        session = create_session()
        ret = session.query(Hosts).filter(Hosts.uuid == uuid).first()
        if ret:
            ret.backup_profile = newprofile
            session.flush()
        session.close()
        return ret != None

    def get_host_period_profile(self,uuid):
        session = create_session()
        host = session.query(Hosts).filter(Hosts.uuid == uuid).first()
        session.close()
        if not host:
            logger.warning("Can't find configured host with uuid = %s" % uuid)
            return -1
        else:
            return host.period_profile

    def set_host_period_profile(self,uuid,newprofile):
        session = create_session()
        ret = session.query(Hosts).filter(Hosts.uuid == uuid).first()
        if ret:
            ret.period_profile = newprofile
            session.flush()
        session.close()
        return ret != None


    def get_hosts_by_backup_profile(self,profileid):
        session = create_session()
        ret = session.query(Hosts.uuid).filter(Hosts.backup_profile== profileid).all()
        session.close()
        if ret:
            for i in xrange(len(ret)):
                ret[i] = ret[i][0]
            return ret
        else:
            return []


    def get_hosts_by_period_profile(self,profileid):
        session = create_session()
        ret = session.query(Hosts.uuid).filter(Hosts.period_profile== profileid).all()
        session.close()
        if ret:
            for i in xrange(len(ret)):
                ret[i] = ret[i][0]
            return ret
        else:
            return []

    # =====================================================================
    # HOSTS TABLE FUNCTIONS
    # =====================================================================

    def add_host(self,uuid):
        session = create_session()
        host = Hosts()
        # Setting host fields
        host.uuid = uuid
        host.backup_profile = 0
        host.period_profile = 0
        #
        session.add(host)
        session.flush()
        session.close()
        return dbOjb2dict(host) or {}
    
    def remove_host(self,uuid):
        session = create_session()
        try:
            ret = session.query(Hosts).filter(Hosts.uuid == uuid.upper()).one()
            if ret:
                session.delete(ret)
                session.flush()
        except:
            logger.error("Can't remove host where uuid=%s" % uuid)
        session.close()
        
    def host_exists(self,uuid):
        session = create_session()
        try:
            ret = session.query(Hosts).filter(Hosts.uuid == uuid.upper()).one()
            exists = (ret != None)
            session.close()
            return ret
        except:
            logger.error("DB Error")
        

    # =====================================================================
    # BACKUP SERVER FUNCTIONS
    # =====================================================================

    def get_backupserver_by_entity(self,entity_uuid):
        session = create_session()
        try:
            ret = session.query(Backup_servers.backupserver_url).filter(Backup_servers.entity_uuid == entity_uuid).one()
            if ret: return ret.backupserver_url
        except:
            ret = ''
        session.close()
        return ret

    # =====================================================================

    def get_backupservers_list(self):
        session = create_session()
        ret = session.query(Backup_servers).all()
        session.close()
        return dbOjb2dict(ret) or []


    def add_backupserver(self,entityuuid,serverURL):
        session = create_session()
        server = Backup_servers()
        # Setting host fields
        server.entity_uuid = entityuuid
        server.backupserver_url = serverURL
        #
        session.add(server)
        session.flush()
        session.close()
        return dbOjb2dict(server) or {}

    def remove_backupserver(self,entityuuid):
        session = create_session()
        ret = session.query(Backup_servers).filter(Backup_servers.entity_uuid == entityuuid).first()
        if ret:
            session.delete(ret)
            session.flush()
        else:
            logger.warning("Can't find BackupServer associated to entity %s" % entityuuid)
        session.close()

##############################################################################################################
class Backup_servers(database_helper.DBObject):
    to_be_exported = ['entity_uuid', 'backupserver_url']

class Hosts(database_helper.DBObject):
    to_be_exported = ['uuid', 'backup_profile','period_profile']

class Backup_profiles(database_helper.DBObject):
    to_be_exported = ['id', 'profilename','sharenames','excludes','encoding']

class Period_profiles(database_helper.DBObject):
    to_be_exported = ['id', 'profilename','full','incr','exclude_periods']
