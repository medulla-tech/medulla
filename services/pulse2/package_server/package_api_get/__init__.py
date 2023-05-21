#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
    Pulse2 Modules
"""
import logging
import os
from pulse2.package_server.common import Common
from pulse2.package_server.xmlrpc import MyXmlrpc


class PackageApiGet(MyXmlrpc):
    type = "PackageApiGet"

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
            raise e
        self.logger.info(
            "(%s) %s : initialised with packages : %s"
            % (self.type, self.name, str(list(Common().getPackages(self.mp).keys())))
        )

    def xmlrpc_getServerDetails(self):
        return [Common().package(x).toH() for x in Common().getPackages(self.mp)]

    def xmlrpc_getAllPackages(self, mirror=None):
        return [Common().package(x).toH() for x in Common().getPackages(self.mp)]

    def xmlrpc_getAllPendingPackages(self, mirror=None):
        ret = Common().getPendingPackages(self.mp)
        r = []
        for x in ret:
            p = ret[x].toH()
            self.logger.debug(Common().newAssociation)
            self.logger.debug(Common().inEdition)
            if p["id"] in Common().newAssociation or p["id"] in Common().inEdition:
                p["why"] = "association"
            r.append(p)
        return r

    def xmlrpc_getPackagesDetail(self, pidlist):
        return [p.toH() for p in Common().packagelist(pidlist, self.mp)]

    def xmlrpc_getPackageDetail(self, pid):
        try:
            ret = Common().package(pid, self.mp).toH()
        except KeyError:
            # We don't own this package
            ret = {}
        except Exception as e:
            # Another unknown error
            self.logger.exception(e)
            ret = {}
        return ret

    def xmlrpc_getLocalPackagesPath(self, pidlist):
        return [os.path.dirname(p.root) for p in Common().packagelist(pidlist)]

    def xmlrpc_getLocalPackagePath(self, pid):
        try:
            ret = os.path.dirname(Common().package(pid, self.mp).root)
        except KeyError:
            # We don't own this package
            ret = {}
        except Exception as e:
            # Another unknown error
            self.logger.exception(e)
            ret = {}
        return ret

    def xmlrpc_getPackageLabel(self, pid):
        return Common().package(pid, self.mp).label

    def xmlrpc_getPackageVersion(self, pid):
        return Common().package(pid, self.mp).version

    def xmlrpc_getPackageSize(self, pid):
        return Common().package(pid, self.mp).size

    def xmlrpc_getPackageInstallInit(self, pid):
        return Common().package(pid, self.mp).initcmd.toH()

    def xmlrpc_getPackagePreCommand(self, pid):
        return Common().package(pid, self.mp).precmd.toH()

    def xmlrpc_getPackageCommand(self, pid):
        return Common().package(pid, self.mp).cmd.toH()

    def xmlrpc_getPackagePostCommandSuccess(self, pid):
        return Common().package(pid, self.mp).postcmd_ok.toH()

    def xmlrpc_getPackagePostCommandFailure(self, pid):
        return Common().package(pid, self.mp).postcmd_ko.toH()

    def xmlrpc_getPackageHasToReboot(self, pid):
        return Common().package(pid, self.mp).reboot

    def xmlrpc_getPackageLicenses(self, pid):
        return Common().package(pid, self.mp).licenses

    def xmlrpc_getPackageAssociateinventory(self, pid):
        return Common().package(pid, self.mp).associateinventory

    def xmlrpc_getPackageQvendor(self, pid):
        return Common().package(pid, self.mp).Qvendor

    def xmlrpc_getPackageQsoftware(self, pid):
        return Common().package(pid, self.mp).Qsoftware

    def xmlrpc_getPackageQversion(self, pid):
        return Common().package(pid, self.mp).Qversion

    def xmlrpc_getPackageBoolcnd(self, pid):
        return Common().package(pid, self.mp).boolcnd

    def xmlrpc_getPackageFiles(self, pid):  # TODO remove the internals
        return [x.toH() for x in Common().package(pid, self.mp).files.internals]

    def xmlrpc_getFileChecksum(self, file):
        return None

    def xmlrpc_getPackagesIds(self, label):
        return Common().reverse(self.mp)[label]

    def xmlrpc_getPackageId(self, label, version):
        return Common().reverse(self.mp)[label][version]

    def xmlrpc_isAvailable(self, pid, mirror):
        return True
