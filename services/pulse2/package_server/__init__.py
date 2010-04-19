# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
    Pulse2 Package Server
"""

import os.path
import logging
import time
import os

from pulse2.package_server.config import config_addons
from pulse2.package_server.common import Common
from pulse2.package_server.common.serializer import PkgsRsyncStateSerializer
import pulse2.utils

from threading import Thread
from twisted.internet import task
from twisted.internet import utils
from twisted.internet import defer

REVISION = int("$Rev$".split(':')[1].strip(' $'))
VERSION = "1.3.0"


def getRevision():
    return REVISION


def getVersion():
    return VERSION


class ThreadPackageHelper(Thread):
    def __init__(self, config):
        Thread.__init__(self)
        self.logger = logging.getLogger()
        self.config = config
        self.working = False

    def log_message(self, format, *args):
        self.logger.info(format % args)


class ThreadPackageDetect(ThreadPackageHelper):
    def runSub(self):
        try:
            if self.working:
                self.logger.debug("###############= ThreadPackageDetect already running")
                return
            self.working = True
            logging.getLogger().debug("\n")
            logging.getLogger().debug("###############> ThreadPackageDetect is running")
            if self.config.package_detect_tmp_activate:
                Common().moveCorrectPackages()
            Common().detectNewPackages()
            logging.getLogger().debug("###############< ThreadPackageDetect end\n")
        except Exception, e:
            logging.getLogger().error('an Exception happened when trying to detect packages:' + str(e))
        self.working = False

    def run(self):
        l = task.LoopingCall(self.runSub)
        l.start(self.config.package_detect_loop)


class ThreadPackageGlobalMirror(ThreadPackageHelper):
    def onError(self, reason, args):
        target, root = args
        self.logger.warning("ThreadPackageGlobalMirror failed to synchronise %s:%s %s" % (target, root, str(reason)))

    def onSuccess(self, result, args):
        target, root = args
        out, err, code = result
        if code == 0:
            self.logger.debug("ThreadPackageGlobalMirror succeed on %s:%s" % (target, root))
        else:
            self.logger.warning("ThreadPackageGlobalMirror mirroring command failed %s:%s %s" % (target, root, str(result)))

    def _runSub(self):
        def createDeferred(exe, args, target, root):
            d = utils.getProcessOutputAndValue(exe, args)
            d.addCallback(self.onSuccess, (target, root))
            d.addErrback(self.onError, (target, root))
            return d

        def cbEnding(result, self):
            self.logger.debug("ThreadPackageGlobalMirror end mirroring")
            self.working = False

        if self.working:
            return

        self.working = True
        self.logger.debug("ThreadPackageGlobalMirror start global mirroring")
        dlist = []
        all_roots = Common().getAllPackageRoot()
        for root in all_roots:
            exe = self.config.package_mirror_command
            args = []
            args.extend(self.config.package_global_mirror_command_options)
            if type(self.config.package_mirror_command_options_ssh_options) == list:
                args.extend(['--rsh', '/usr/bin/ssh -o %s' % (" -o ".join(self.config.package_mirror_command_options_ssh_options))])
            args.append(root)

            for target in self.config.package_mirror_target:
                l_args = args[:]
                l_args.append("%s:%s%s.." % (target, root, os.path.sep))
                self.logger.debug("ThreadPackageGlobalMirror execute : %s %s" % (exe, str(l_args)))
                dlist.append(createDeferred(exe, l_args, target, root))

        dl = defer.DeferredList(dlist)
        dl.addCallback(cbEnding, (self))
        return dl

    def runSub(self):
        try:
            self._runSub()
        except Exception, e:
            self.logger.error("ThreadPackageGlobalMirror: " + str(e))
            self.working = False

    def run(self):
        l = task.LoopingCall(self.runSub)
        l.start(self.config.package_global_mirror_loop)


class ThreadPackageMirror(ThreadPackageHelper):
    def __init__(self, config, sync_status):
        ThreadPackageHelper.__init__(self, config)
        self.status = self.config.package_mirror_status_file
        if not sync_status:
            # sync global
            Common().rsyncPackageOnMirrors()

    def onError(self, reason, args):
        pid, target = args
        self.logger.warning("ThreadPackageMirror failed to synchronise %s" % (str(reason)))

    def onSuccess(self, result, args):
        pid, target, is_deletion = args
        out, err, code = result
        if code == 0:
            self.logger.debug("ThreadPackageMirror succeed %s" % (str(result)))
            Common().removePackagesFromRsyncList(pid, target)
        else:
            self.logger.error("ThreadPackageMirror mirroring command failed %s" % (str(result)))

    def _runSub(self):
        def mirror_level0(result, args):
            pid, target, is_deletion = args
            out, err, code = result
            if code == 0:
                pkg = Common().packages[pid]
                try:
                    self.logger.debug("Removing %s" % (pkg.root))
                    os.rmdir(pkg.root)
                    exe = self.config.package_mirror_command
                    args = []
                    args.extend(self.config.package_mirror_level0_command_options)
                    if type(self.config.package_mirror_command_options_ssh_options) == list:
                        args.extend(['--rsh', '/usr/bin/ssh -o %s' % (" -o ".join(self.config.package_mirror_command_options_ssh_options))])
                    args.append(str("%s%s" % (os.path.dirname(pkg.root), os.path.sep)))
                    args.append("%s:%s" % (target, os.path.dirname(pkg.root)))
                    self.logger.debug("ThreadPackageMirror execute mirror level0 : %s %s" % (exe, str(args)))
                    return createDeferred(exe, args, pid, target, False)
                except Exception, e:
                    self.logger.error("ThreadPackageMirror mirror level0 failed for package %s : %s" % (pid, str(e)))
            else:
                self.logger.debug("ThreadPackageMirror failed %s" % (str(result)))

        def createDeferred(exe, args, pid, target, is_deletion = False):
            d = utils.getProcessOutputAndValue(exe, args)
            if is_deletion:
                d.addCallback(mirror_level0, (pid, target, is_deletion))
            else:
                d.addCallback(self.onSuccess, (pid, target, is_deletion))
            d.addErrback(self.onError, (pid, target))
            return d

        def cbEnding(result, self):
            if result == []:
                self.logger.debug("ThreadPackageMirror end mirroring")
            else:
                self.logger.debug("ThreadPackageMirror end mirroring: %s" % str(result))
            self.working = False

        if self.working:
            self.logger.debug("already running")
            return
        self.working = True
        self.logger.debug("ThreadPackageMirror is looking for new things to mirror")
        dlist = []
        for pid, targets, pkg in Common().getPackagesThatNeedRsync():
            exe = self.config.package_mirror_command
            p_dir = pkg.root
            is_deletion = False
            if not os.path.exists(p_dir):
                # deletion = mirror empty dir + mirror top level on just 1 level
                os.mkdir(p_dir)
                # mark as deletion
                is_deletion = True

            for target in targets:
                if target == '':
                    continue
                try:
                    self.logger.debug("ThreadPackageMirror will mirror %s on %s" % (pid, target))
                    args = []
                    args.extend(self.config.package_mirror_command_options)
                    if type(self.config.package_mirror_command_options_ssh_options) == list:
                        args.extend(['--rsh', '/usr/bin/ssh -o %s' % (" -o ".join(self.config.package_mirror_command_options_ssh_options))])
                    args.append(str(p_dir))
                    args.append("%s:%s" % (target, os.path.dirname(pkg.root)))
                    self.logger.debug("ThreadPackageMirror execute : %s %s" % (exe, str(args)))
                    dlist.append(createDeferred(exe, args, pid, target, is_deletion))
                except Exception, e:
                    self.logger.error("ThreadPackageMirror failed to mirror %s : %s" % (pid, str(e)))

        dl = defer.DeferredList(dlist)
        dl.addCallback(cbEnding, (self))
        return dl

    def runSub(self):
        try:
            self._runSub()
        except Exception, e:
            self.logger.error("ThreadPackageMirror: " + str(e))
            self.working = False

    def run(self):
        l = task.LoopingCall(self.runSub)
        l.start(self.config.package_mirror_loop)


class ThreadLauncher(pulse2.utils.Singleton):
    def initialize(self, config):
        self.logger = logging.getLogger()
        self.config = config
        config_addons(config)
        Common().init(config)
        sync_status = PkgsRsyncStateSerializer().init(Common())

        if self.config.package_detect_activate:
            self.logger.info("Package detection activated")
            if self.config.package_detect_tmp_activate:
                self.logger.info("Package detection activated for temporary folder")
            if self.config.package_detect_smart:
                self.logger.info("Package detection mechanism will be '%s' (%s)" % (self.config.packageDetectSmartMethod(), str(self.config.package_detect_smart_time)))

            self.logger.info("Starting package detection thread")
            threadpd = ThreadPackageDetect(config)
            threadpd.setDaemon(True)
            threadpd.start()
            self.logger.info("Package detection thread started")

        if self.config.package_mirror_activate:
            self.logger.info("Starting package mirror thread")
            self.threadpm = ThreadPackageMirror(config, sync_status)
            self.threadpm.setDaemon(True)
            self.logger.info("Package mirror thread started")

            if self.config.package_global_mirror_activate:
                self.logger.info("Starting global package mirror thread")
                self.threadgp = ThreadPackageGlobalMirror(config)
                self.threadgp.setDaemon(True)
                self.logger.info("Global package mirror thread started")

        from pulse2.package_server import thread_webserver
        thread_webserver.initialize(self.config)
        # FIXME: Little sleep because sometimes Python exits before the
        # threads have the time to start
        time.sleep(5)

    def runThreads(self):
        if self.config.package_mirror_activate:
            self.logger.info("Package mirror thread start")
            self.threadpm.start()
            if self.config.package_global_mirror_activate:
                self.logger.info("Global package mirror thread start")
                self.threadgp.start()


def init_logger_debug():
    """
    Add two new level of debug
    """
    DEBUG1 = 9
    DEBUG2 = 8
    setattr(logging, "DEBUG1", DEBUG1)
    setattr(logging, "DEBUG2", DEBUG2)

    logging.addLevelName(logging.DEBUG1, "DEBUG1")
    logging.addLevelName(logging.DEBUG2, "DEBUG2")

    def debug1(logger, message):
        return logger.log(logging.DEBUG1, message)

    def debug2(logger, message):
        return logger.log(logging.DEBUG2, message)

    logging.RootLogger.debug1 = debug1
    logging.RootLogger.debug2 = debug2
