#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
    Medulla2 Modules
"""
import os
from shutil import move
import time
import logging
from base64 import b64decode
from medulla.package_server.package_api_get import PackageApiGet
from medulla.package_server.types import Package
from medulla.package_server.common import Common
from medulla.package_server.common.getCommand import getCommand
from medulla.package_server.config import P2PServerCP


class PackageApiPut(PackageApiGet):
    type = "PackageApiPut"

    def __init__(self, mp, name="", tmp_input_dir=""):
        PackageApiGet.__init__(self, mp, name)
        self.tmp_input_dir = tmp_input_dir
        self.config = P2PServerCP()

    def xmlrpc_getTemporaryFiles(self):
        self.logger.debug("xmlrpc_getTemporaryFiles")
        ret = []
        if os.path.exists(self.tmp_input_dir):
            for f in os.listdir(self.tmp_input_dir):
                ret.append([f, os.path.isdir(os.path.join(self.tmp_input_dir, f))])
        return ret

    def xmlrpc_getTemporaryFilesSuggestedCommand(self, tempdir):
        ret = {
            "version": "0.1",
            "commandcmd": [],
        }

        suggestedCommand = []

        # In some cases, tempdir can be an empty list
        # if True, don't enter in this piece of code
        if not isinstance(tempdir, list):
            if os.path.exists(self.tmp_input_dir):
                for f in os.listdir(os.path.join(self.tmp_input_dir, tempdir)):
                    f = os.path.join(self.tmp_input_dir, tempdir, f)
                    if os.path.isfile(f):
                        c = getCommand(f)
                        command = c.getCommand()
                        if command is not None:
                            suggestedCommand.append(command)

        ret["commandcmd"] = "\n".join(suggestedCommand)
        return ret

    def xmlrpc_pushPackage(self, random_dir, files, local_files):
        if local_files:
            logging.getLogger().info("pushing package from a local mmc-agent")
        else:
            logging.getLogger().info("pushing package from an external mmc-agent")

        if not os.path.exists(self.tmp_input_dir):
            os.makedirs(self.tmp_input_dir)
        filepath = os.path.join(self.tmp_input_dir, random_dir)
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        for file in files:
            if local_files:
                logging.getLogger().debug("Move file %s" % file["filename"])
                move(
                    os.path.join(file["tmp_dir"], random_dir, file["filename"]),
                    os.path.join(filepath, file["filename"]),
                )
                os.chmod(os.path.join(filepath, file["filename"]), 0o660)
            else:
                logging.getLogger().debug("Decode file %s" % file["filename"])
                f = open(os.path.join(filepath, file["filename"]), "w")
                f.write(b64decode(file["filebinary"]))
                f.close()

        return True

    def xmlrpc_associatePackages(self, pid, fs, level=0):
        files = []
        ret = True

        for f in fs:
            if not os.path.exists(os.path.join(self.tmp_input_dir, f)):
                ret = False
            else:
                files.append(os.path.join(self.tmp_input_dir, f))
        if not ret:
            return [False, "Some files are missing"]

        try:
            ret_assoc = Common().associateFiles(self.mp, pid, files, level)
        except exceptions.OSError as e:
            return [False, str(e)]

        if not self.config.package_detect_activate:
            # Run the detectNewPackages stuff to register our new package
            # FIXME: the next line force the new package to be detected
            del Common().packages[pid]
            for i in range(10):
                ret = Common().detectNewPackages()
                if ret:
                    break
                time.sleep(1)
        errors = []
        if ret_assoc[1] & 1:
            errors.append("Some files failed to be erased")
        # COULD ADD SOME MORE FLAGS

        ret_assoc[1] = errors
        return ret_assoc

    def xmlrpc_removeFilesFromPackage(self, pid, files):
        try:
            return Common().removeFilesFromPackage(pid, files)
        except Exception as e:
            return [False, str(e)]

    def xmlrpc_putPackageDetail(self, package, need_assign=True):
        self.logger.debug("xmlrpc_putPackageDetail")
        pa = Package()
        pa.fromH(package)
        if pa.id in Common().dontgivepkgs and len(Common().dontgivepkgs[pa.id]) > 0:
            return (False, "This package is curently locked")

        ret = Common().editPackage(package["id"], pa, need_assign, self.mp)
        if not ret:
            return False

        # Create conf file in package
        ret = Common().writePackageTo(package["id"], self.mp)
        ret, confdir = ret
        if not ret:
            return False

        ret = Common().associatePackage2mp(package["id"], self.mp)
        if not ret:
            return False

        if not P2PServerCP().package_detect_activate:
            del Common().inEdition[package["id"]]

        # Force packavge detection
        Common().detectNewPackages()
        Common()._createMD5File(pa.root, force_compute=True)
        # Reload all package info
        # desc = Common().desc
        # Common().init(Common().config)
        # Common().desc = desc

        return (True, package["id"], confdir, pa.toH())

    def xmlrpc_dropPackage(self, pid):
        ret = Common().dropPackage(pid, self.mp)
        if not ret:
            return False

        ret = Common().desassociatePackage2mp(pid, self.mp)
        if not ret:
            return False

        return pid

    def xmlrpc_getRsyncStatus(self, pid):
        return Common().getRsyncStatus(pid, self.mp)

    def xmlrpc_putPackageLabel(self, pid, label):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackageVersion(self, pid, version):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackageSize(self, pid, size):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackageInstallInit(self, pid, cmd):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackagePreCommand(self, pid, cmd):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackageCommand(self, pid, cmd):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackagePostCommandSuccess(self, pid, cmd):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackagePostCommandFailure(self, pid, cmd):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_putPackageFiles(self, pid, a_files):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )

    def xmlrpc_addPackageFile(self, pid, file):
        self.logger.warn(
            "(%s) %s : call to an unimplemented method" % (self.type, self.name)
        )
