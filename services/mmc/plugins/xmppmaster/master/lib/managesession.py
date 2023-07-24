# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

import glob
import os
import json
import logging

logger = logging.getLogger()


class Session(Exception):
    pass


class SessionAssertion(Session, AssertionError):
    pass


class Sessionpathsauvemissing(Session, Exception):
    pass


class SessionkeyError(Session, KeyError):
    pass


class sessiondatainfo:
    def __init__(
        self,
        sessionid,
        datasession={},
        timevalid=10,
        eventend=None,
        handlefunc=None,
        pathfile=None,
    ):
        self.sessionid = sessionid
        # timevalid en minute
        self.timevalid = timevalid
        self.datasession = datasession
        self.eventend = eventend
        self.handlefunc = handlefunc
        self.pathfile = pathfile
        if pathfile == None:
            raise Sessionpathsauvemissing
        logger.debug("SESSION INFO CREATION")

    def jsonsession(self):
        session = {
            "sessionid": self.sessionid,
            "timevalid": self.timevalid,
            "datasession": self.datasession,
        }
        return json.dumps(session)

    def sauvesession(self):
        namefilesession = os.path.join(self.pathfile, self.sessionid)
        session = {
            "sessionid": self.sessionid,
            "timevalid": self.timevalid,
            "datasession": self.datasession,
        }
        with open(namefilesession, "w") as f:
            json.dump(session, f, indent=4)

    def updatesessionfromfile(self):
        namefilesession = os.path.join(self.pathfile, self.sessionid)
        logger.debug("SESSION INFO UPDATE SESSION")
        with open(namefilesession, "r") as fichier:
            session = json.load(fichier)
        self.datasession = session["datasession"]
        self.timevalid = session["timevalid"]

    def removesessionfile(self):
        namefilesession = os.path.join(self.pathfile, self.sessionid)
        os.remove(namefilesession)

    def getdatasession(self):
        return self.datasession

    def setdatasession(self, data):
        self.datasession = data
        self.sauvesession()

    def decrementation(self):
        self.timevalid = self.timevalid - 1
        if self.timevalid <= 0:
            logger.debug("appelle callend")
            self.callend()
        else:
            self.sauvesession()

    def settimeout(self, timeminute=10):
        self.timevalid = timeminute

    def isexiste(self, sessionid):
        return sessionid == self.sessionid

    def callend(self):
        logger.debug("signaler session fin")
        if self.handlefunc != None:
            self.handlefunc(self.datasession)
        if self.eventend != None:
            self.eventend.set()

    def __repr__(self):
        return "<session %s, validate %s, data %s, eventend %s> " % (
            self.sessionid,
            self.timevalid,
            self.datasession,
            self.eventend,
        )


class session:
    def __init__(self, typemachine=None):
        self.sessiondata = []

        if typemachine == "relayserver":
            self.dirsavesession = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "..", "sessionsrelayserver"
            )
        elif typemachine == "machine":
            self.dirsavesession = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "..", "sessionsmachine"
            )
        else:
            self.dirsavesession = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "..", "sessions"
            )

        if not os.path.exists(self.dirsavesession):
            os.makedirs(self.dirsavesession, mode=0o007)
        logger.debug("SESSION %s " % self.dirsavesession)
        self.loadsessions()

    def addsessiondatainfo(self, sessiondatainfo):
        if self.isexist(sessiondatainfo.sessionid):
            raise SessionAssertion
        else:
            self.sessiondata.append(sessiondatainfo)
            return sessiondatainfo

    def getcountsession(self):
        return len(self.sessiondata)

    def createsessiondatainfo(
        self, sessionid, datasession={}, timevalid=10, eventend=None
    ):
        logger.debug("SESSION CREATION UNE SESSION")
        obj = sessiondatainfo(
            sessionid, datasession, timevalid, eventend, pathfile=self.dirsavesession
        )
        self.sessiondata.append(obj)
        if len(datasession) != 0:
            obj.sauvesession()
        return obj

    def removefilesessionifnotsignal(self, namefilesession):
        with open(namefilesession, "r") as fichier:
            session = json.load(fichier)
        if "datasession" in session and "signal" in session["datasession"]:
            return True
        else:
            os.remove(namefilesession)
            return False

    def loadsessions(self):
        listfilesession = [
            x
            for x in glob.glob(os.path.join(self.dirsavesession, "*"))
            if (os.path.isfile(x) and os.path.basename(x).startswith("command"))
        ]
        for filesession in listfilesession:
            if self.removefilesessionifnotsignal(filesession):
                try:
                    # Session id is the name of the file
                    objsession = self.sessionfromsessiondata(
                        os.path.basename(filesession)
                    )
                    if objsession == None:
                        raise SessionkeyError
                    objsession.pathfile = self.dirsavesession
                    objsession.updatesessionfromfile()
                except SessionkeyError:
                    # Session does not exist
                    objsession = self.createsessiondatainfo(
                        os.path.basename(filesession)
                    )
                    objsession.updatesessionfromfile()

    def sauvesessions(self):
        for i in self.sessiondata:
            i.sauvesession()

    def sauvesessionid(self, sessionid):
        for i in self.sessiondata:
            for i in self.sessiondata:
                if i.sessionid == sessionid:
                    i.sauvesession()
                    return i
            return None

    def __decr__(self, x):
        x.decrementation()

    def decrementesessiondatainfo(self):
        list(filter(self.__decr__, self.sessiondata))
        self.__suppsessiondatainfo__()

    def __suppsessiondatainfo__(self):
        datasessioninfo = [x for x in self.sessiondata if x.timevalid <= 0]
        self.sessiondata = [x for x in self.sessiondata if x.timevalid > 0]
        # Delete session persistance file
        for i in datasessioninfo:
            i.removesessionfile()

    def __aff__(self, x):
        if x != None:
            logger.info(x)
            pass

    def len(self):
        return len(self.sessiondata)

    def affiche(self):
        list(map(self.__aff__, self.sessiondata))

    def sessionfromsessiondata(self, sessionid):
        for i in self.sessiondata:
            if i.sessionid == sessionid:
                return i
        return None
        # raise SessionkeyError

    def reactualisesession(self, sessionid, timeminute=10):
        for i in self.sessiondata:
            if i.sessionid == sessionid:
                i.settimeout(timeminute)
                break

    def clear(self, sessionid, objectxmpp=None):
        for i in range(0, self.len()):
            if sessionid == self.sessiondata[i].sessionid:
                self.sessiondata[i].callend()
                self.sessiondata[i].removesessionfile()
                self.sessiondata.remove(self.sessiondata[i])
                break
        if objectxmpp != None:
            objectxmpp.eventmanage.clear(sessionid)

    def clearnoevent(self, sessionid):
        for i in range(0, self.len()):
            if sessionid == self.sessiondata[i].sessionid:
                # renovefile
                self.sessiondata[i].removesessionfile()
                self.sessiondata.remove(self.sessiondata[i])
                break

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
            if i.sessionid == sessionid:
                i.setdatasession(data)

    def sessiongetdata(self, sessionid):
        for i in self.sessiondata:
            if i.sessionid == sessionid:
                return i.getdatasession()
        return None
