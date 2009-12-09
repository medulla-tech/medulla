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

class Event(object):
    pass

class Source(object):
    pass

class Initiator(object):	
    pass

class Current_Value(object):

    def __init__(self,object_log,value):        
        self.object_log_id=object_log.id
        self.value=value

class Record(object):
            
    def getId(self):
        return self.id

    def __repr__(self):
        return [self.id, self.event_id, self.initiator_id, self.object_user_id, self.log_date, self.module_id, self.result]

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
