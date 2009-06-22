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

import time

from mmc.support.mmctools import Singleton
from sqlalchemy import *
from classes import *

class AuditRecord:
    
    def __init__(self, action, plugin, user, object, param, client, agent, previous, current):
        """
        Create a AuditRecord instance which contains all information that will
        be logged into database.
        
        @param action: action name 
        @type action: string
        @param plugin: plugin name
        @type action: string
        @param plugin: plugin name
        @type plugin: string
        @param user: user name
        @type user: string
        @param object: list tuple of object which contains object name and object type [('object','typeobject')...]
        @type object: list
        @param client: tuple which represent client (clienthost, clienttype)
        @type client: tuple
        @param param: parameters
        @type param: dict 
        @param agent: represent agent hostname
        @type agent: string
        """
        # action string
        self.action=action
        # plugin string
        self.plugin=plugin
        # String
        self.user=user
        # Dictionnary of string
        self.parameters=param
        # list of couple (object, type)
        self.objects=object
        # 
        self.client=client
        # string
        self.agent=agent
        # list of string list
        self.previousattribute=previous
        # list of string list
        self.currentattribute=current


class AuditRecordDB(AuditRecord):

    def __init__(self, parent, session, action, module, user, object, param, client, agent, current, previous):
        """ 
        Insert New log in database 
        @param action: action name 
        @type action: string
        @param module: module name
        @type action: string
        @param module: module name
        @type module: string
        @param user: user name
        @type user: string
        @param object: list tuple of object which contains object name and object type [('object','typeobject')...]
        @type object: list
        @param client: tuple which represent client (clienthost, clienttype)
        @type client: tuple
        @param param: parameters
        @type param: dict 
        @param agent: represent agent hostname
        @type agent: string
        """
        
        AuditRecord.__init__(self, action, module, user, object, param, client, agent, current, previous)
        self.session = session
        self.session.begin()
        
        # get module_id and action_id of action
        bdmodule = self.session.query(Module).filter(parent.module_table.c.module_name==module).first()
        if bdmodule == None:
            bdmodule = Module()
            bdmodule.module_name = module
            self.session.save(bdmodule)
            self.session.flush()

        # get action object action already exist and is insert in setup_db
        bdaction = self.session.query(Action).filter(and_(parent.action_table.c.action_details==action, parent.action_table.c.module_id==bdmodule.id)).first()
        if bdaction == None:
            count = self.session.query(Action).filter(parent.action_table.c.module_id==bdmodule.id).count()
            bdaction = Action()
            bdaction.id = count
            bdaction.module_id = bdmodule.id
            bdaction.action_details = action
            self.session.save(bdaction)
            self.session.flush()

        # get client object
        bdclient = self.session.query(Client).filter(and_(parent.client_table.c.client_type==client[1], parent.client_table.c.client_host==client[0])).first()
        
        if bdclient == None:
            bdclient = Client()
            bdclient.client_type = client[1]
            bdclient.client_host = client[0]
            self.session.save(bdclient)
            self.session.flush()


        # get agent object
        bdagent = self.session.query(Agent).filter(parent.agent_table.c.agent_host==agent).first()
        if bdagent == None:
            bdagent = Agent()
            bdagent.agent_host = agent
            self.session.save(bdagent)
            self.session.flush()

        # get user object
        # FIXME user must be constant ok 
        bduser = self.session.query(Object).filter(and_(parent.object_table.c.object_name==user,parent.object_table.c.type_id==1)).first()
        if bduser == None:
            utype = self.session.query(Type).filter(parent.type_table.c.type == 'USER').first()            
            bduser = Object()
            bduser.object_name = user
            bduser.type_id = utype.id
            self.session.save(bduser)
            self.session.flush()

        # Log(...)
        self.bdlog = Log(bdaction, bdmodule, bdagent, bdclient, bduser, False)
        # Insert Object_Log
        self.session.save(self.bdlog)
        self.session.flush()
        
        parentobj=None
        if object != None:
            for i,j in object:
                #Get or Insert Type id of object
                bdtype = self.session.query(Type).filter(parent.type_table.c.type==j).first()
                if bdtype == None:
                    bdtype = Type()
                    bdtype.type = j
                    self.session.save(bdtype)
                    self.session.flush()
                
                # Object is not parent
                # l'objet peut ne pas avoir de parent
                obj = self.session.query(Object).filter(and_(parent.object_table.c.object_name==i, parent.object_table.c.type_id==bdtype.id)).first()

                if obj == None:          
                    obj = Object()
                    obj.object_name = i
                    obj.type_id = bdtype.id
                    
                    
                    if bdtype.id == 2:
                        obj.parent = None
                    else:
                        obj.parent = parentobj
                    self.session.save(obj)
                    self.session.flush()
                #
                # Insert in object_log table
                #
                
                parentobj = obj.id
                bdobjectlog = Object_Log()
                bdobjectlog.object_id = obj.id
                bdobjectlog.log_id = self.bdlog.id
                self.session.save(bdobjectlog)
                self.session.flush()
                # object type is attribute
                if obj.type_id==2:
                    bdobjectlogattr=bdobjectlog
              
        #insert current value
        if current != None:
            if type(current) == tuple or type(current) == list :
                for i in current:            
                     cv = Current_Value(bdobjectlogattr, i)
                     self.session.save(cv)
            else:
                cv = Current_Value(bdobjectlogattr, current)
                self.session.save(cv)

        #insert previous value        
        if previous != None:
            if type(previous) == tuple or type(previous) == list:
                for i in previous:             
                     pv = Previous_Value(bdobjectlogattr, i)
                     self.session.save(pv)      
            else:          
                pv = Previous_Value(bdobjectlogattr, previous)
                self.session.save(pv)  

        # relations on log_parameters        
        if param != None:
            for i in param:
                if type(i)==list:
                    for j in i:
                        p = Parameters(j, str(i[j]))
                        self.bdlog.param_log.append(p)
                else:
                    p = Parameters(i, str(param[i]))
                    self.bdlog.param_log.append(p)
        
        self.session.save_or_update(self.bdlog)
        self.session.flush()
        self.session.commit()
        
    def commit(self):
        """
        Valid the log and set the result attribute to True if action succeeds
        """
        self.bdlog.result = True
        self.session.save_or_update(self.bdlog)
        self.session.flush()
        self.session.close()
