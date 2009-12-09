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

from sqlalchemy import *
from classes import *

class AuditReaderDB:

    def __init__(self, parent, session):
        self.session = session
        self.parent = parent
        
    def getlog(self, start, end, plug, user, type, date1, date2, object, action):
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
        
        qlog = self.session.query(Log)
        
        #
        # Filter by plugin
        #
        
        if plug != 0:
            plugin = self.session.query(Plugin).filter(self.parent.plugin_table.c.plugin_name.like("%"+plug+"%")).first()
            if plugin != None:        
                
                ql = qlog.filter(self.parent.log_table.c.plugin_id==plugin.id)
                qlog = ql
            else:
                self.session.close()
                return None
        
        #
        # Filter by date
        #
        
        if (date1 != 0) and (date2 != 0):    
            
            ql = qlog.filter(and_(self.parent.log_table.c.log_date>=date1,self.parent.log_table.c.log_date<=date2))
            qlog = ql
        
        #
        # Filter by user
        #
        
        if user != 0:
            object_user = self.session.query(Object).filter(and_(self.parent.object_table.c.type_id==1,self.parent.object_table.c.object_name.like("%"+user+"%"))).first()
            if object_user==None:
                self.session.close()
                return None
            else:
               
               ql = qlog.filter(self.parent.log_table.c.object_user_id==object_user.id)
               qlog = ql

        #
        # Filter by action
        #
        
        if action != 0:
            action = self.session.query(Action).filter(self.parent.action_table.c.action_details.like("%"+action+"%")).all()
            if action != []:
                oraction = or_(self.parent.log_table.c.action_id==action[0].id)
                for idact in action:
                        oraction = or_(oraction,self.parent.log_table.c.action_id==idact.id)
                ql = qlog.filter(oraction)
                qlog = ql
            else:
                return None
        
        
        #
        # Filter by object
        #
        
                
        if object != 0:
            obj= self.session.query(Object).filter(self.parent.object_table.c.object_name.like("%"+object+"%")).all()
            if obj != []:
                orobj = or_(self.parent.object_log_table.c.object_id==obj[0].id)
                for idobj in obj:
                    orobj = or_(orobj,self.parent.object_log_table.c.object_id==idobj.id)
                object_log = self.session.query(Object_Log).filter(orobj).all()
                orobjlog = or_(self.parent.log_table.c.id==object_log[0].log_id)
                for idobjectlog in object_log:
                    orobjlog = or_(orobjlog,self.parent.log_table.c.id==idobjectlog.log_id)
                ql = qlog.filter(orobjlog)
            #ql = qlog.filter(self.parent.object_table.c.object_name.like("%"+object+"%")).join("obj_log")
            
                qlog = ql
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
        return [logcount, self.getarraylogs(qlog.order_by(desc(self.parent.log_table.c.id)).limit(end-start).offset(start))]
    
    def get_by_Id(self,id):
        """
        Return a log dict 
        @param id: id in log table 
        @type id: int
        """
        qlog = self.session.query(Log).filter(self.parent.log_table.c.id==id)
        return self.getarraylogs(qlog)
    
    def getarraylogs(self,qlog):
        """
        return an array of log
        @param qlog: list of Log
        @type qlog: list
        """
        
        self.logresult=[]
        
        for logs in qlog:
                laction = self.session.query(Action).filter(and_(self.parent.action_table.c.id==logs.action_id, self.parent.action_table.c.plugin_id==logs.plugin_id)).first()
                lparam = self.session.query(Parameters).filter(self.parent.param_table.c.log_id == logs.id).all()
                lplugin = self.session.query(Plugin).filter(self.parent.plugin_table.c.id == logs.plugin_id).first()
                lclient = self.session.query(Client).filter(self.parent.client_table.c.id == logs.client_id).first()
                #listobj = self.session.query(Object_Log).filter(self.parent.object_log_table.c.log_id == logs.id).order_by(desc(self.parent.object_log_table.c.id)).all()
                listobj = self.session.query(Object_Log).filter(self.parent.object_log_table.c.log_id == logs.id).all()
                luser = self.session.query(Object).filter(self.parent.object_table.c.id == logs.object_user_id).first()
                lagent = self.session.query(Agent).filter(self.parent.agent_table.c.id == logs.agent_id).first()
                #put params in dict
                if lparam != None:
                    parameters={}
                    for param in lparam :
                        parameters.__setitem__(str(param.param_name),str(param.param_value))
                if listobj != None:
                    llistobj=[]
                    for objects in listobj:
                        lobject = self.session.query(Object).filter(self.parent.object_table.c.id == objects.object_id).first()
                        ltype = self.session.query(Type).filter(self.parent.type_table.c.id == lobject.type_id).first()
                        
                        #
                        #    Object is an LDAP Attribute
                        #
                       
                        if lobject.type_id==2:
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
                            
                            llistobj.append({"object":str(lobject.object_name), "type":str(ltype.type), "previous":pattr,"current":cattr})        
                        else:
                        
                            llistobj.append({"object":str(lobject.object_name), "type":str(ltype.type)})
                #
                #    Final array
                #                            
                        
                self.logresult.append({"id":str(logs.id),
                    "date":str(logs.log_date),
                    "commit":logs.result,
                    "user":luser.object_name,
                    "action":laction.action_details,
                    "plugin":lplugin.plugin_name,
                    "client-type":lclient.client_type, 
                    "client-host":lclient.client_host, 
                    "agent-host":lagent.agent_host,
                    "objects":llistobj,
                    "parameters":parameters})
        self.session.close()
        return self.logresult
        
    def __str__(self):     
        for i in self.logresult:
            print i
        
    def get_action_type(self,action,type):
        """
        Return a list of action or type it depends on action value or type
        @param action: action = 1 return list of actions
        @type action: int
        @param type: type = 1 return list of objects types
        @type type: int
        """
        res={}
        if action!= 0:
            for i in self.session.query(Action).all():
                res.__setitem__(i.action_details,i.action_details)
            self.session.close()
            return res
        elif type!= 0:
            for i in self.session.query(Type).all():
                res.__setitem__(i.type,i.type)
            self.session.close()
            return res
