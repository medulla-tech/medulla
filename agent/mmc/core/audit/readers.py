
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
Contains classes that read records for the audit system
"""

from sqlalchemy import and_, or_, desc
from mmc.core.audit.classes import Record, Module, Object, Object_Log, Event, Parameters, Initiator, Type, Source, Previous_Value, Current_Value

class AuditReaderDB:

    def __init__(self, parent, session):
        self.session = session
        self.parent = parent

    def getLog(self, start, end, plug, user, type, date1, date2, object, action):
        """
            @param start: start of search
            @param end: end of search
            @param plug: plugin search
            @param user: searched user
            @param type: type of object searched
            @param date1: begin date
            @param date2: end date
            @param object: object name searched
            @param action: action name searched
            @type start: string
            @type end: string
            @type plug: string
            @type user: string
            @type type: string
            @type date1: string
            @type date2: string
            @type object: string
            @type action: string
        """
        qlog = self.session.query(Record)

        #
        # Filter by module
        #
        if plug != 0:
            plugin = self.session.query(Module).filter(self.parent.module_table.c.name.like("%"+plug+"%")).first()
            if plugin != None:

                ql = qlog.filter(self.parent.record_table.c.module_id==plugin.id)
                qlog = ql
            else:
                self.session.close()
                return None

        #
        # Filter by date
        #
        if (date1 != 0) and (date2 != 0):
            ql = qlog.filter(and_(self.parent.record_table.c.date>=date1,self.parent.record_table.c.date<=date2))
            qlog = ql
        elif (date1 != 0):
            ql = qlog.filter(self.parent.record_table.c.date>=date1)
            qlog = ql
        elif (date2 != 0):
            ql = qlog.filter(self.parent.record_table.c.date<=date2)
            qlog = ql
        #
        # Filter by user
        #
        if user != 0:
            # type_id: 1 => USER
            # type_id: 2 => SYSTEMUSER
            object_user = self.session.query(Object).filter(
                and_(
                    or_(
                        self.parent.object_table.c.type_id==1,
                        self.parent.object_table.c.type_id==2,
                    ),
                    self.parent.object_table.c.uri.like("%"+user+"%"),
                )).first()
            if object_user==None:
                self.session.close()
                return None
            else:
               ql = qlog.filter(self.parent.record_table.c.user_id==object_user.id)
               qlog = ql

        #
        # Filter by event
        #
        if action != 0:
            action = self.session.query(Event).filter(self.parent.event_table.c.name.like("%"+action+"%")).all()
            if action != []:
                oraction = or_(self.parent.record_table.c.event_id==action[0].id)
                for idact in action:
                        oraction = or_(oraction,self.parent.record_table.c.event_id==idact.id)
                ql = qlog.filter(oraction)
                qlog = ql
            else:
                return None


        #
        # Filter by object
        #
        if object != 0:
            obj= self.session.query(Object).filter(self.parent.object_table.c.uri.like("%"+object+"%")).all()
            if obj != []:
                orobj = or_(self.parent.object_log_table.c.object_id==obj[0].id)
                for idobj in obj:
                    orobj = or_(orobj,self.parent.object_log_table.c.object_id==idobj.id)
                object_log = self.session.query(Object_Log).filter(orobj).all()
                if object_log:
                    orobjlog = or_(self.parent.record_table.c.id==object_log[0].record_id)
                    for idobjectlog in object_log:
                        orobjlog = or_(orobjlog,self.parent.record_table.c.id==idobjectlog.record_id)
                        ql = qlog.filter(orobjlog)
                        #ql = qlog.filter(self.parent.object_table.c.uri.like("%"+object+"%")).join("obj_log")
                    qlog = ql
                else:
                    self.session.close()
                    return None
            else:
                self.session.close()
                return None
        #
        # Filter by type
        #
        if type != 0:
            typ = self.session.query(Type).filter(self.parent.type_table.c.type.like("%"+type+"%")).first()
            if typ != None:
                ql = qlog.filter(self.parent.object_table.c.type_id==typ.id).join("obj_log")
                qlog = ql
            else:
                self.session.close()
                return None
        logcount = qlog.count()

        return [logcount, self.getArrayLogs(qlog.order_by(desc(self.parent.record_table.c.id)).limit(end-start).offset(start))]

    def getLogById(self,id):
        """
        Return a log dict
        @param id: id in log table
        @type id: int
        """
        qlog = self.session.query(Record).filter(self.parent.record_table.c.id==id)
        return self.getArrayLogs(qlog)

    def getArrayLogs(self,qlog):
        """
        return an array of log
        @param qlog: list of Log
        @type qlog: list
        """

        self.logresult=[]

        for record in qlog:
            laction = self.session.query(Event).filter(and_(self.parent.event_table.c.id==record.event_id, self.parent.event_table.c.module_id==record.module_id)).first()
            lparam = self.session.query(Parameters).filter(self.parent.param_table.c.record_id == record.id).all()
            lplugin = self.session.query(Module).filter(self.parent.module_table.c.id == record.module_id).first()
            lclient = self.session.query(Initiator).filter(self.parent.initiator_table.c.id == record.initiator_id).first()
            listobj = self.session.query(Object_Log).filter(self.parent.object_log_table.c.record_id == record.id).all()
            luser = self.session.query(Object).filter(self.parent.object_table.c.id == record.user_id).first()
            lagent = self.session.query(Source).filter(self.parent.source_table.c.id == record.source_id).first()

            #put params in dict
            if lparam != None:
                parameters={}
                for param in lparam :
                    parameters.__setitem__(str(param.param_name),str(param.param_value))

            llistobj=[]
            if listobj != None:
                for objects in listobj:

                    lobject = self.session.query(Object).filter(self.parent.object_table.c.id == objects.object_id).first()
                    ltype = self.session.query(Type).filter(self.parent.type_table.c.id == lobject.type_id).first()

                    #
                    #    Object is an LDAP Attribute
                    #
                    #if lobject.type_id==2:
                    lpattr = self.session.query(Previous_Value).filter(self.parent.previous_value_table.c.object_log_id==objects.id).all()
                    #
                    # Put attr in array !
                    #

                    pattr=[]
                    for p in lpattr:
                        pattr.append(p.value)

                    lcattr = self.session.query(Current_Value).filter(self.parent.current_value_table.c.object_log_id==objects.id).all()

                    cattr=[]
                    for c in lcattr:
                        cattr.append(c.value)

                    llistobj.append({"object":str(lobject.uri), "type":str(ltype.type), "previous":pattr,"current":cattr})
                #else:
                 #   llistobj.append({})
                    #llistobj.append({"object":str(lobject.uri), "type":str(ltype.type)})
            #
            #    Final array
            #
            self.logresult.append({
                "id":str(record.id),
                "date":str(record.date),
                "commit":record.result,
                "user":luser.uri,
                "action":laction.name,
                "plugin":lplugin.name,
                "client-type":lclient.application,
                "client-host":lclient.hostname,
                "agent-host":lagent.hostname,
                "objects":llistobj,
                "parameters":parameters,
            })
        self.session.close()
        return self.logresult

    def __str__(self):
        for i in self.logresult:
            print i

    def getActionType(self,action,type):
        """
        Return a list of action or type it depends on action value or type
        @param action: action = 1 return list of actions
        @type action: int
        @param type: type = 1 return list of objects types
        @type type: int
        """
        res={}
        if action != 0:
            for i in self.session.query(Event).all():
                res.__setitem__(i.name,i.name)
            self.session.close()
            return res
        elif type != 0:
            for i in self.session.query(Type).all():
                if i.type != "SYSTEMUSER":
                    res.__setitem__(i.type,i.type)
            self.session.close()
            return res
