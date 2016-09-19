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
import glob 
import os
import json
import pprint

class Session(Exception):
    pass

class SessionAssertion(Session, AssertionError):
    pass

class Sessionpathsauvemissing(Session, Exception):
    pass

class SessionkeyError(Session, KeyError):
    pass


class sessiondatainfo:

    def __init__(self, sessionid, datasession = {}, timevalid = 10, eventend = None, handlefunc = None, pathfile = None):
        self.sessionid = sessionid
        #timevalid en minute
        self.timevalid = timevalid
        self.datasession = datasession
        self.eventend = eventend
        self.handlefunc = handlefunc
        self.pathfile = pathfile
        if pathfile == None:
            raise Sessionpathsauvemissing
        print "SESSION INFO CREATION"

    def jsonsession(self):
        session = { 'sessionid' : self.sessionid,'timevalid':self.timevalid,'datasession':self.datasession}
        return json.dumps(session)
    
    def sauvesession(self):
        namefilesession = os.path.join( self.pathfile, self.sessionid )
        session = { 'sessionid' : self.sessionid, 'timevalid' : self.timevalid, 'datasession' : self.datasession }
        with open(namefilesession, 'w') as f:
            json.dump(session, f, indent = 4)
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(self.datasession)

    def updatesessionfromfile(self):
        namefilesession = os.path.join( self.pathfile, self.sessionid )
        print "SESSION INFO UPDATE SESSION"
        with open(namefilesession, "r") as fichier:
            session = json.load(fichier)
        self.datasession = session['datasession']
        self.timevalid = session['timevalid']

    def removesessionfile(self):
        namefilesession = os.path.join( self.pathfile, self.sessionid )
        os.remove(namefilesession)

    def getdatasession(self):
        return self.datasession

    def setdatasession(self, data):
        self.datasession=data
        self.sauvesession()

    def decrementation(self):
        self.timevalid = self.timevalid - 1
        if self.timevalid <= 0:
            print "appelle callend"
            self.callend()
        else:
            self.sauvesession()

    def settimeout(self, timeminute = 10):
        self.timevalid = timeminute

    def isexiste(self, sessionid):
        return sessionid == self.sessionid

    def callend(self):
        print "signaler session fin"
        if self.handlefunc != None:
            self.handlefunc(self.datasession)
        if self.eventend != None:
            self.eventend.set()

    def __repr__(self):
        #return "<session {}, validate {}, data {}, eventend {}> ".format(self.sessionid, self.timevalid, self.datasession, self.eventend)
        return "<session %s, validate %s, data %s, eventend %s> "%(self.sessionid, self.timevalid, self.datasession, self.eventend)

class session:
    def __init__(self, typemachine = None):
        self.sessiondata = []

        if(typemachine == "relayserver"):
            self.dirsavesession = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"sessionsrelayserver")
        elif typemachine == "machine":
            self.dirsavesession = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"sessionsmachine")
        else :
            self.dirsavesession = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".." ,"sessions")

        if not os.path.exists(self.dirsavesession):
            os.makedirs(self.dirsavesession, mode=0007)
        print "SESSION %s "%self.dirsavesession
        self.loadsessions()

    def addsessiondatainfo(self, sessiondatainfo):
        if self.isexist(sessiondatainfo.sessionid):
            raise SessionAssertion
        else:
            self.sessiondata.append(sessiondatainfo)
            return sessiondatainfo

    def createsessiondatainfo(self, sessionid,  datasession = {},timevalid = 10, eventend = None):
        print "SESSION CREATION UNE SESSION"
        obj = sessiondatainfo(sessionid, datasession, timevalid, eventend ,pathfile=self.dirsavesession)
        self.sessiondata.append(obj)
        if len(datasession) != 0:
            obj.sauvesession()
        return obj

    def removefilesessionifnotsignal(self, namefilesession):
        with open(namefilesession, "r") as fichier:
            session = json.load(fichier)
        if 'datasession' in session and 'signal' in session['datasession']:
            return True
        else:
            os.remove(namefilesession)
            return False

    def loadsessions(self):
        listfilesession = [x  for x in glob.glob(os.path.join(self.dirsavesession, "*" )) if (os.path.isfile(x) and os.path.basename(x).startswith( 'command'))]
        #print listfilesession
        for filesession in listfilesession:
            if self.removefilesessionifnotsignal(filesession):
                try:
                    #lasession id est le nom du fichier
                    objsession = self.sessionfromsessiondata(os.path.basename(filesession))
                    if objsession== None: raise SessionkeyError
                    objsession.pathfile = self.dirsavesession
                    objsession.updatesessionfromfile()
                except SessionkeyError:
                    #session non exist
                    objsession = self.createsessiondatainfo(os.path.basename(filesession))
                    objsession.updatesessionfromfile()


    def sauvesessions(self):
        for i in self.sessiondata:
            i.sauvesession()

    def sauvesessionid(self,sessionid):
        for i in self.sessiondata:
            for i in self.sessiondata:
                if i.sessionid == sessionid :
                    i.sauvesession()
                    return i
            return None

    def __decr__(self,x):
        x.decrementation()

    def decrementesessiondatainfo(self):
        filter(self.__decr__, self.sessiondata)
        self.__suppsessiondatainfo__()

    def __suppsessiondatainfo__(self):
        datasessioninfo = [x  for x in self.sessiondata if x.timevalid <= 0]
        self.sessiondata = [x  for x in self.sessiondata if x.timevalid > 0]
        #effacefichier persistance session
        for i in datasessioninfo:
            i.removesessionfile()

    def __aff__(self,x):
        if x != None : print x

    def len(self):
        return len(self.sessiondata)

    def affiche(self):
        map(self.__aff__, self.sessiondata)

    def sessionfromsessiondata(self, sessionid):
        for i in self.sessiondata:
            if i.sessionid == sessionid :
                return i
        return None    
        #raise SessionkeyError

    def reactualisesession(self, sessionid, timeminute = 10):
        for i in self.sessiondata:
            if i.sessionid == sessionid :
                i.settimeout(timeminute)
                break

    def clear(self, sessionid, objectxmpp = None):
        for i in range(0,self.len()):
            if sessionid == self.sessiondata[i].sessionid:
                self.sessiondata[i].callend()
                self.sessiondata[i].removesessionfile()
                self.sessiondata.remove(self.sessiondata[i])
                break;
        if objectxmpp != None:
            objectxmpp.eventmanage.clear(sessionid)

    def clearnoevent(self, sessionid):
        for i in range(0, self.len()):
            if sessionid == self.sessiondata[i].sessionid:
                #renovefile
                self.sessiondata[i].removesessionfile()
                self.sessiondata.remove(self.sessiondata[i])
                break;

    def isexist(self, sessionid):
        for i in self.sessiondata:
            if i.sessionid == sessionid:
                return True
        return False

    def sessionevent(self, sessionid):
        for i in self.sessiondata:
            if i.sessionid == sessionid and i.eventend != None:
                return i
        return None

    def sessionstop(self):
        for i in range(0, self.len()):
            self.sessiondata[i].sauvesession()
        self.sessiondata = []
            
    def sessionsetdata(self, sessionid, data):
        for i in self.sessiondata:
            if i.sessionid == sessionid :
                i.setdatasession(data)

