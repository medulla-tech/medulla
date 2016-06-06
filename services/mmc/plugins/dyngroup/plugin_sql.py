#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
#
# $Id$
#
# This file is part of MMC.
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
Mapping between SA and SQL ?
"""

from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import create_session, mapper

class SqlPlugin:
    """
    Class to query the dyngroup SQL db
    """
    def __init__(self, conf):
        self.config = conf
        self.db = create_engine(self.makeConnectionPath())
        self.metadata = MetaData(self.db)
        self.initMappers()
        self.metadata.create_all()
        self.session = create_session()

    def makeConnectionPath(self):
        """
        Build and return the db connection path according to the plugin configuration

        @rtype: str
        """
        if self.config.dbport:
            port = ":" + str(self.config.dbport)
        else:
            port = ""
        return "%s://%s:%s@%s%s/%s" % (self.config.dbdriver, self.config.dbuser, self.config.dbpasswd, self.config.dbhost, port, self.config.dbname)

    def initMappers(self):
        """
        Initialize all SQLalchemy mappers needed for the dyngroups database
        """
        self.sqlDatumSave = Table("SqlDatumSave", self.metadata, autoload = True)
        mapper(SqlDatumSave, self.sqlDatumSave)

    def hasValue(self, key, user = None):
        datum = self.session.query(SqlDatumSave).filter(self.sqlDatumSave.c.k == key).first()
        if datum != None:
            if user == None or datum.user == None or user == datum.user:
                return True
            else:
                raise Exception("user don't have good rigths")
        return False

    def delete(self, key, user = None):
        datum = self.session.query(SqlDatumSave).filter(self.sqlDatumSave.c.k == key).first()
        if datum != None:
            if user == None or datum.user == None or user == datum.user:
                self.session.delete(datum)
                self.session.flush()
                return key
            else:
                raise Exception("user don't have good rigths")
        else:
            return None
        
    def getValue(self, key, user = None):
        datum = self.session.query(SqlDatumSave).filter(self.sqlDatumSave.c.k == key).first()
        if datum != None:
            if user == None or datum.user == None or user == datum.user:
                return datum.value
            else:
                raise Exception("user don't have good rigths")
        return None

    def setValue(self, key, val, user = None):
        datum = self.session.query(SqlDatumSave).filter(self.sqlDatumSave.c.k == key).first()
        if datum != None:
            if user == None or datum.user == None or user == datum.user:
                datum.value = val
                self.session.add(datum)
            else:
                raise Exception("user don't have good rigths")
        else:
            datum = SqlDatumSave()
            datum.k = key
            datum.value = val
            datum.user = user
            self.session.add(datum)
        self.session.flush()
        return val

# Class for SQLalchemy mapping
class SqlDatumSave(object):
    def toS(self):
        return str(self.id) + ") " + str(self.k) + " = " + str(self.value)

