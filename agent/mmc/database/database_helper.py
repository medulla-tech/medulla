# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com/
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

"""
Define classes to help implementing the database access in all the
pulse2 modules.
"""
import functools
import logging

from mmc.support.mmctools import Singleton
from mmc.database.ddl import DDLContentManager, DBControl
from mmc.database.sqlalchemy_tests import checkSqlalchemy, MIN_VERSION, MAX_VERSION, CUR_VERSION
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.orm.util import _entity_descriptor

Session = sessionmaker()
logger = logging.getLogger()
NB_DB_CONN_TRY = 2


class DatabaseConnectionError(Exception):
    pass


class DatabaseHelper(Singleton):
    is_activated = False
    config = None
    session = None

    def db_check(self):
        required_version = DDLContentManager().get_version(self.my_name)
        if not checkSqlalchemy():
            logger.error("Sqlalchemy: current version is %s. Must be between %s and %s" % (CUR_VERSION, MIN_VERSION, MAX_VERSION))
            return False

        conn = self.connected()
        if conn:
            # Glpi is an external DB, its version is not managed by Pulse
            if self.my_name == 'Glpi':
                return True
            elif required_version == self.db_version:
                return True
            elif required_version > self.db_version:
                return self.db_update()
            elif required_version != -1 and conn != required_version:
                logger.error("%s database version error: v.%s needeed, v.%s found; please update your schema !" % (self.my_name, required_version, conn))
                return False
        else:
            logger.error("Can't connect to database (s=%s, p=%s, b=%s, l=%s, p=******). Please check %s." % (self.config.dbhost, self.config.dbport, self.config.dbbase, self.config.dbuser, self.configfile))
            return False
        return True

    def db_update(self):
        """Automatic database update"""

        db_control = DBControl(user=self.config.dbuser,
                               passwd=self.config.dbpasswd,
                               host=self.config.dbhost,
                               port=self.config.dbport,
                               module=self.config.dbname,
                               log=logger,
                               use_same_db=True)

        return db_control.process()

    def connected(self):
        try:
            if self.db is not None:
                if hasattr(self, "version"):
                    return self.version.select().execute().fetchone()[0]
                elif hasattr(self, "Version"):
                    return self.version.select().execute().fetchone()[0]
                else:
                    return True
            return False
        except:
            if self.db is not None and self.session is not None:
                return True
            return False

    def makeConnectionPath(self):
        """
        Build and return the db connection path according to the plugin
        configuration.

        @rtype: str
        """
        if self.config is None:
            raise Exception("Object must have a config attribute")
        if self.config.dbport:
            port = ":" + str(self.config.dbport)
        else:
            port = ""
        url = "%s://%s:%s@%s%s/%s" % (self.config.dbdriver, self.config.dbuser, self.config.dbpasswd, self.config.dbhost, port, self.config.dbname)
        if self.config.dbdriver == 'mysql':
            # See http://www.sqlalchemy.org/docs/05/reference/dialects/mysql.html#character-sets
            # charset=utf8 will convert all data to UTF-8, even if tables are
            # stored in Latin-1
            url += '?charset=utf8&use_unicode=0'
            if self.config.dbsslenable:
                url = url + "&ssl_ca=%s&ssl_key=%s&ssl_cert=%s" % (self.config.dbsslca, self.config.dbsslkey, self.config.dbsslcert)
        return url

    def enableLogging(self, level=None):
        """
        Enable log for sqlalchemy.engine module using the level configured by the db_debug option of the plugin configuration file.
        The SQL queries will be loggued.
        """
        if not level:
            if hasattr(self.config, "dbdebug"):
                level = self.config.dbdebug
            else:
                level = logging.INFO
        logging.getLogger("sqlalchemy.engine").setLevel(level)

    def disableLogging(self):
        """
        Disable log for sqlalchemy.engine module
        """
        logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

    def getDbConnection(self):
        ret = None
        for i in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except:
                logger.exception("Error on DB connection")
            if ret:
                break
        if not ret:
            raise DatabaseConnectionError("Database connection error")
        return ret

    def initMappersCatchException(self):
        try:
            self.initMappers()
        except NoSuchTableError, e:
            logger.warn('The table %s does not exists.' % str(e))
            return False
        except:
            logger.exception('Error when initializing mappers')
            return False
        return True

    @property
    def db_version(self):
        if hasattr(self, "version"):
            return self.version.select().execute().fetchone()[0]
        elif hasattr(self, "Version"):
            return self.version.select().execute().fetchone()[0]


    # Session decorator to create and close session automatically
    @classmethod
    def _session(self, func):
        @functools.wraps(func)
        def __session(self, *args, **kw):
            created = False
            if not self.session:
                self.session = Session(bind=self.db)
                created = True
            result = func(self, self.session, *args, **kw)
            if created:
                self.session.close()
                self.session = None
            return result
        return __session


    # listinfo decorator to handle offsets, limits and output serialization
    # for XMLRPC, can handle multiple entities queries, multiple columns
    # and mapped relationships
    @classmethod
    def _listinfo(self, func_):
        @functools.wraps(func_)
        def __listinfo(self, params, *args, **kw):
            query = func_(self, params, *args, **kw)

            # Testing if result is a Query statement
            if not isinstance(query, Query):
                logging.getLogger().error('@_listinfo methods must return a Query object, got %s', query.__class__.__name__)
                return {'count': 0, 'data': [], 'listinfo': 1}

            # Applying filters on primary entity
            # Exact filters
            if 'filters' in params and params['filters']:
                clauses = [_entity_descriptor(query._mapper_zero(), key) == value
                    for key, value in params['filters'].iteritems()]
                if clauses:
                    query = query.filter(*clauses)
            # Like filters
            if 'like_filters' in params and params['like_filters']:
                clauses = [_entity_descriptor(query._mapper_zero(), key).like('%' + value + '%')
                    for key, value in params['like_filters'].iteritems()]
                if clauses:
                    query = query.filter(*clauses)

            # Calculating count without limit and offset on primary entity id
            primary_id = _entity_descriptor(query._mapper_zero(), "id")
            count = query.with_entities(func.count(primary_id))
            # Scalar doesn't work if multiple entities are selected
            count = sum([c[0] for c in count.all()])

            # Applying limit and offset
            if 'max' in params and 'min' in params:
                query = query.limit(int(params['max']) - int(params['min'])).offset(int(params['min']))

            columns = query.column_descriptions

            data = []

            # Serializing query output
            for line in query:
                if isinstance(line, DBObj):
                    data.append(line.toDict())
                elif isinstance(line, tuple):
                    # Fetching all tuple items
                    line_ = {}
                    for i in xrange(len(line)):
                        item = line[i]
                        if isinstance(item, DBObj):
                            line_.update(item.toDict())
                        else:
                            if item.__class__.__name__ == 'Decimal':
                                item = int(item)
                            line_.update({columns[i]['name'].encode('ascii', 'ignore') : item})
                    data.append(line_)
                else:
                    if line.__class__.__name__ == 'Decimal':
                        line = int(line)
                    elif hasattr(line, '_sa_instance_state'):
                        # SA object, try to do a dict conversion
                        line = line.__dict__
                        del line['_sa_instance_state']
                    # Base types
                    data.append(line)

            # Ensure that session will be closed
            query.session.close()

            return {'count': count, 'data': data, 'listinfo': 1}

        return __listinfo


    @classmethod
    def _logquery(self, func_):
        """
        print a query, with values filled in
        for debugging purposes *only*
        for security, you should always separate queries from their values
        please also note that this function is quite slow
        """
        @functools.wraps(func_)
        def __logquery(self, *args, **kw):
            query = func_(self, *args, **kw)

            # ===========================================
            # Begin query logging
            # ===========================================
            if isinstance(query, Query):
                bind = query.session.get_bind(
                        query._mapper_zero_or_none()
                )
                statement = query.statement
            else:
                logging.getLogger().error('@_logquery methods must return a Query object, got %s', query.__class__.__name__)
                return query

            dialect = bind.dialect
            compiler = statement._compiler(dialect)
            class LiteralCompiler(compiler.__class__):
                def visit_bindparam(
                        self, bindparam, within_columns_clause=False,
                        literal_binds=False, **kwargs
                ):
                    return super(LiteralCompiler, self).render_literal_bindparam(
                            bindparam, within_columns_clause=within_columns_clause,
                            literal_binds=literal_binds, **kwargs
                    )

            compiler = LiteralCompiler(dialect, statement)
            query_str = compiler.process(statement)
            logging.getLogger().debug('Result query for %s:' % func_.__name__)
            logging.getLogger().debug(query_str)

            # ===========================================
            # End query logging
            # ===========================================

            return query

        return __logquery


class DBObject(object):
    to_be_exported = ['id', 'name', 'label']
    need_iteration = []
    i18n = []

    def getUUID(self):
        if hasattr(self, 'id'):
            return id2uuid(self.id)
        logging.getLogger().warn("try to get %s uuid!" % type(self))
        return False

    def to_h(self):
        return self.toH()

    def toH(self, level=0):
        ret = {}
        for i in dir(self):
            if i in self.i18n:
                pass

            if i in self.to_be_exported:
                ret[i] = getattr(self, i)
            if i in self.need_iteration and level < 1:
                # we don't want to enter in an infinite loop
                # and generally we don't need more levels
                attr = getattr(self, i)
                if type(attr) == list:
                    new_attr = []
                    for a in attr:
                        new_attr.append(a.toH(level + 1))
                    ret[i] = new_attr
                else:
                    ret[i] = attr.toH(level + 1)
        if hasattr(self, 'id'):
            ret['db_uuid'] = self.getUUID()
        return ret


# new Class to remplace current DBObject
class DBObj(object):
    # Function to convert mapped object to Dict
    # TODO : Do the same for relations [convert relations to subdicts]
    def toDict(self, relations=True):
        d = self.__dict__
        # Convert relations to dict, if 'relations'
        for k in d.keys():
            if isinstance(d[k], DBObj):
                if relations:
                    d[k] = d[k].toDict()
                else:
                    del d[k]
        # Delete Sqlachemy instance state
        if '_sa_instance_state' in d:
            del d['_sa_instance_state']
        return d

    def fromDict(self, d, relations=False):
        #TODO: Test if d is dict
        if '_sa_instance_state' in d:
            del d['_sa_instance_state']
        # Actually we don't support relations
        for key, value in d.iteritems():
            if key and type(value) not in [type({}), type([])]:
                setattr(self, key, value)

    def __str__(self):
        return str(self.toDict())


def id2uuid(id):
    return "UUID%d" % id


def uuid2id(uuid):
    return uuid.replace("UUID", "")
