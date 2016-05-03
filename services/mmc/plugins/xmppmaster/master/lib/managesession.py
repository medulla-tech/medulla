# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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

class Session(Exception):
    pass

class SessionAssertion(Session, AssertionError):
    pass

class SessionkeyError(Session, KeyError):
    pass

class sessiondatainfo:
    def __init__(self, sessionid, datasession = {}, timevalid = 10, functionend = None):
        self.sessionid = sessionid
        #timevalid en minute
        self.timevalid = timevalid
        self.datasession = datasession
        self.functionend = functionend

    def decrementation(self):
        self.timevalid = self.timevalid - 1
        if self.timevalid == 0:
            self.callend()

    def settimeout(self, timeminute = 10):
        self.timevalid = timeminute

    def isexiste(self, sessionid):
        return sessionid == self.sessionid

    def callend(self):
        if self.functionend != None:
            self.functionend(self.datasession)

    def __repr__(self):
        return "<session {} validate {}, data {}, functionend {}> ".format(self.sessionid, self.timevalid, self.datasession,self.functionend)


class session:
    def __init__(self):
        self.sessiondata=[]

    def addsessiondatainfo(self, sessiondatainfo):
        if self.isexist(sessiondatainfo.sessionid):
            raise SessionAssertion
        else:
            self.sessiondata.append(sessiondatainfo)
            return sessiondatainfo

    def createsessiondatainfo(self, sessionid,  datasession = {},timevalid = 10, functionend = None):
        obj = sessiondatainfo(sessionid, datasession, timevalid, functionend )
        self.sessiondata.append(obj)
        return obj

    def __decr__(self,x):
        x.decrementation()

    def decrementesessiondatainfo(self):
        filter(self.__decr__, self.sessiondata)
        self.__suppsessiondatainfo__()

    def __suppsessiondatainfo__(self):
        self.sessiondata = [x  for x in self.sessiondata if x.timevalid != 0]

    def __aff__(self,x):
        print x

    def len(self):
        return len(self.sessiondata)

    def affiche(self):
        map(self.__aff__, self.sessiondata)

    def sessionfromsessiondata(self, sessionid):
        for i in self.sessiondata:
            if i.sessionid == sessionid :
                return i
        raise SessionkeyError

    def reactualisesession(self, sessionid, timeminute = 10):
        for i in self.sessiondata:
            if i.sessionid == sessionid :
                i.settimeout(timeminute)
                break

    def clear(self, sessionid):
        for i in range(0,self.len()):
            if sessionid==self.sessiondata[i].sessionid:
                print "clear %s"%self.sessiondata[i].sessionid
                self.sessiondata.remove(self.sessiondata[i]) 
                break;

    def isexist(self, sessionid):
        for i in self.sessiondata:
            if i.sessionid == sessionid:
                return True
        return False