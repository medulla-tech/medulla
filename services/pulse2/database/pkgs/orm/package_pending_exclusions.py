# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

class Package_pending_exclusions(object):
    def getId(self):
        if self.id is not None:
            return self.id

        return 0

    def getRelayserver_jid(self):
        if self.relayserver_jid is not None:
            return self.relayserver_jid

        return ""

    def to_array(self):
        """
        This function serialize the object to dict.

        Returns:
            Dict of elements contained into the object.
        """
        return {"id": self.getId(), "getRelayserver_jid": self.getRelayserver_jid()}
