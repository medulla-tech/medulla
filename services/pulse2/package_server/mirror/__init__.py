#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
    Pulse2 PackageServer Mirror API
"""
import logging
from pulse2.package_server.common import Common
from pulse2.package_server.xmlrpc import MyXmlrpc


class Mirror(MyXmlrpc):
    type = "Mirror"

    def __init__(self, mp, name=""):
        MyXmlrpc.__init__(self)
        self.logger = logging.getLogger()
        self.name = name
        self.mp = mp
        if Common().getPackages(self.mp) is None:
            e = "(%s) %s : can't initialise at %s correctly" % (
                self.type,
                self.name,
                self.mp,
            )
            self.logger.error(e)
            raise Exception(e)
        self.logger.info(
            "(%s) %s : initialised with packages : %s"
            % (self.type, self.name, str(list(Common().getPackages(self.mp).keys())))
        )

    def xmlrpc_getServerDetails(self):
        return [Common().package(x).toH() for x in Common().getPackages(self.mp)]

    def xmlrpc_isAvailable(self, pid):
        return pid in Common().getPackages(self.mp)

    def xmlrpc_getFilesURI(self, fids):
        ret = []
        for fid in fids:
            ret.append(self.xmlrpc_getFilePath(fid))
        return ret

    def xmlrpc_getFileURI(self, fid):
        return self.xmlrpc_getFilePath(fid)

    def xmlrpc_getFilePath(self, fid):
        f = Common().getFile(fid, self.mp)
        if f is None:
            return ""
        else:
            return f
