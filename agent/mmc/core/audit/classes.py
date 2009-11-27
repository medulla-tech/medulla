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

from sqlalchemy import func

class Action(object):
    pass

class Agent(object):
    pass

class Client(object):	
    pass

class Current_Value(object):

    def __init__(self,object_log,value):        
        self.object_log_id=object_log.id
        self.value=value

class Log(object):
    
    def __init__(self, action, module, agent, client, objectuser, result):
        self.action_id=action.id
        self.agent_id=agent.id
        self.client_id=client.id
        self.object_user_id=objectuser.id
        self.log_date=func.now()
        self.module_id=module.id
        self.result=result
        
    def getId(self):
        return self.id

    def __repr__(self):
        return [self.id,self.action_id,self.client_id,self.object_user_id,self.log_date,self.module_id,self.result]

class Object_Log(object):
    pass

class Object(object):
    pass	

class Parameters(object):
	
    def __init__(self,param_name,value):
        self.param_name=param_name
     	self.param_value=value

class Module(object):
    pass

class Previous_Value(object):
    
    def __init__(self,object_log,value):        
        self.object_log_id=object_log.id
        self.value=value

class Type(object):
    pass

class Version(object):
    pass
