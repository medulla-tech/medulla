# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Contains classes that define records for the audit system
"""

import logging

from sqlalchemy.orm import create_session
from sqlalchemy import and_
from mmc.core.audit.classes import Record, Module, Object, Object_Log, Event, Parameters, Initiator, Type, Source, Previous_Value, Current_Value

class AuditRecord:

    """
    Base class for a audit record object
    """

    def __init__(self, module, event, user, objects, param, initiator, source, current, previous):
        """
        Create a AuditRecord instance which contains all information that will
        be logged into database.

        @param module: module name
        @type module: string
        @param event: event name
        @type event: string
        @param user: user name
        @type user: string
        @param objects: list tuple of object which contains object uri and object type [('object','typeobject')...]
        @type objects: list
        @param client: tuple which represent client (clienthost, clienttype)
        @type client: tuple
        @param param: parameters
        @type param: dict
        @param agent: represent agent hostname
        @type agent: string
        """
        # module string
        self.module = module
        assert(type(self.module) == unicode)
        # action string
        self.event = event
        assert(type(self.event) == unicode)
        # String
        self.user=user
        assert(type(self.user) == tuple)
        assert(len(self.user) == 2)
        # Dictionnary of string
        self.parameters = param
        assert(type(self.parameters) == dict)
        # list of couple (object, type)
        self.objects=objects
        assert(type(self.objects) == list)
        #
        self.initiator = initiator
        assert(type(self.initiator) == tuple)
        assert(len(self.initiator) == 2)
        #
        self.source = source
        assert(type(source) == str)
        # list of string list
        self.previousattribute=previous
        # list of string list
        self.currentattribute=current


class AuditRecordDB(AuditRecord):

    """
    Class for objects that store an audit record into a database
    """

    def __init__(self, parent, module, event, user, objects, param, initiator, source, current, previous):
        """
        Insert New log in database
        @param action: action name
        @type action: string
        @param module: module name
        @type action: string
        @param module: module name
        @type module: string
        @param user: tuple with user name and type
        @type user: tuple
        @param objects: list tuple of object which contains object uri and object type [('object','typeobject')...]
        @type objects: list
        @param client: tuple which represent client (clienthost, clienttype)
        @type client: tuple
        @param param: parameters
        @type param: dict
        @param agent: represent agent hostname
        @type agent: string
        """
        AuditRecord.__init__(self, module, event, user, objects, param, initiator, source, current, previous)
        session = create_session()
        session.begin()
        try:
            # get module object from database
            bdmodule = session.query(Module).filter(parent.module_table.c.name==module).first()
            # insert module object in database if it is not available
            if bdmodule == None:
                bdmodule = Module()
                bdmodule.name = module
                session.add(bdmodule)
                session.flush()

            # get event object from database
            bdevent = session.query(Event).filter(and_(parent.event_table.c.name == event, parent.event_table.c.module_id == bdmodule.id)).first()
            # insert event object in database if it is not available
            if bdevent == None:
                bdevent = Event()
                bdevent.module_id = bdmodule.id
                bdevent.name = event
                session.add(bdevent)
                session.flush()

            # get initiator object
            bdinitiator = session.query(Initiator).filter(and_(parent.initiator_table.c.application == initiator[1], parent.initiator_table.c.hostname == initiator[0])).first()
            # put it in database if it is not available
            if bdinitiator == None:
                bdinitiator = Initiator()
                bdinitiator.application = initiator[1]
                bdinitiator.hostname = initiator[0]
                session.add(bdinitiator)
                session.flush()

            # get source object
            bdsource = session.query(Source).filter(parent.source_table.c.hostname == source).first()
            # put it in database if not available
            if bdsource == None:
                bdsource = Source()
                bdsource.hostname = source
                session.add(bdsource)
                session.flush()

            # get user type
            utype = session.query(Type).filter(parent.type_table.c.type == self.user[1]).first()
            if utype == None:
                utype = Type()
                utype.type = self.user[1]
                session.add(utype)
                session.flush()

            # get user object
            bduser = session.query(Object).filter(and_(parent.object_table.c.uri == self.user[0], parent.object_table.c.type_id == utype.id)).first()
            if bduser == None:
                bduser = Object()
                bduser.uri = self.user[0]
                bduser.type_id = utype.id
                session.add(bduser)
                session.flush()

            # Fill in record to emit
            self.record = Record()
            self.record.event_id = bdevent.id
            self.record.module_id = bdmodule.id
            self.record.source_id = bdsource.id
            self.record.initiator_id = bdinitiator.id
            self.record.user_id = bduser.id
            # Set result status to undone
            self.record.result = False
            # Insert Object_Log
            session.add(self.record)
            session.flush()

            parentobj = None
            bdobjectlog = None
            if objects != None:
                for i,j in objects:
                    # Get or Insert Type id of object
                    bdtype = session.query(Type).filter(parent.type_table.c.type==j).first()
                    if bdtype == None:
                        bdtype = Type()
                        bdtype.type = j
                        session.add(bdtype)
                        session.flush()

                    # Get or insert object
                    obj = session.query(Object).filter(and_(parent.object_table.c.uri==i, parent.object_table.c.type_id==bdtype.id, parent.object_table.c.parent==parentobj)).first()
                    if obj == None:
                        obj = Object()
                        obj.uri = i
                        obj.type_id = bdtype.id
                        obj.parent = parentobj
                        session.add(obj)
                        session.flush()

                    bdobjectlog = Object_Log()
                    bdobjectlog.object_id = obj.id
                    bdobjectlog.record_id = self.record.id
                    session.add(bdobjectlog)
                    session.flush()

                    # Keep a reference to this object, because it may be
                    # the parent of the next object to store
                    parentobj = obj.id

            if bdobjectlog != None:
                # Insert current value
                if current != None:
                    if type(current) == tuple or type(current) == list :
                        for i in current:
                             cv = Current_Value(bdobjectlog, i)
                             session.add(cv)
                    else:
                        cv = Current_Value(bdobjectlog, current)
                        session.add(cv)

                # Insert previous value
                if previous != None:
                    if type(previous) == tuple or type(previous) == list:
                        for i in previous:
                             pv = Previous_Value(bdobjectlog, i)
                             session.add(pv)
                    else:
                        pv = Previous_Value(bdobjectlog, previous)
                        session.add(pv)

            # relations on log_parameters
            if param != None:
                for i in param:
                    if type(i)==list:
                        for j in i:
                            p = Parameters(j, str(i[j]))
                            self.record.param_log.append(p)
                    else:
                        p = Parameters(i, str(param[i]))
                        self.record.param_log.append(p)

            session.add(self.record)
            session.commit()
        except:
            session.rollback()
            logging.getLogger().error("Error with the audit database connection")
            raise
        session.close()

    def commit(self):
        """
        Valid the log and set the result attribute to True if event succeeds
        """
        self.record.result = True
        session = create_session()
        session.begin()
        try:
            session.add(self.record)
            session.commit()
        except:
            session.rollback()
            logging.getLogger().error("Error with the audit database connection")
            raise
        session.close()
