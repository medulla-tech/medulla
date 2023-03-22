# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
from sqlalchemy.orm import create_session


class Syncthingsync(object):

    def getId(self):
        if self.id is not None:
            return self.id
        else:
            return 0

    def getDate(self):
        if self.date != None:
            return self.date
        else:
            return ""

    def getUuidpackage(self):
        if self.uuidpackage is not None:
            return self.uuidpackage
        else:
            return ""

    def getTypesynchro(self):
        if self.typesynchro is not None:
            return self.typesynchro
        else:
            return ""

    def getRelayserver_jid(self):
        if self.relayserver_jid is not None:
            return self.relayserver_jid
        else:
            return ""

    def getWatching(self):
        if self.watching is not None:
            return self.watching
        else:
            return ""


    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {
            'id' : self.getId(),
            'date' : self.getDate(),
            'uuidpackage' : self.getUuidpackage(),
            'typesynchro': self.getTypesynchro(),
            'relayserver_jid': self.getRelayserver_jid(),
            'watching': self.getWatching()
        }
