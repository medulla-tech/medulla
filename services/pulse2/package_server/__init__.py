#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
#
# $Id: __init__.py 30 2008-02-08 16:40:54Z nrueff $
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
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os.path
import logging
import twisted
import re
import time
import signal
import os
import sys
import shutil

from pulse2.package_server.config import config_addons
from pulse2.package_server.common import Common
from pulse2.package_server.common.serializer import PkgsRsyncStateSerializer
from pulse2.package_server.utilities import Singleton
import pulse2.package_server.thread_webserver
from threading import Thread, Semaphore
import threading
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet import utils
from twisted.internet import defer

"""
    Pulse2 PackageServer
"""

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
        if self.working:
            self.logger.debug("ThreadPackageDetect already running")
            return
        self.working = True
        self.logger.debug("ThreadPackageDetect is running")
        if self.config.package_detect_tmp_activate:
            Common().moveCorrectPackages()
        Common().detectNewPackages()
        self.logger.debug("ThreadPackageDetect end")                
        self.working = False
        
    def run(self):
        l = task.LoopingCall(self.runSub)
        l.start(self.config.package_detect_loop)

class ThreadPackageGlobalMirror(ThreadPackageHelper):
    def onError(self, reason, args):
        target, root = args
        self.logger.warning("ThreadPackageGlobalMirror failed to synchronise %s:%s %s"%(target, root, str(reason)))

    def onSuccess(self, result, args):
        target, root = args
        out, err, code = result
        if code == 0:
            self.logger.debug("ThreadPackageGlobalMirror succeed on %s:%s"%(target, root))
        else:
            self.logger.warning("ThreadPackageGlobalMirror mirroring command failed %s:%s %s"%(target, root, str(result)))

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
                args.extend(['--rsh', '/usr/bin/ssh -o %s'%(" -o ".join(self.config.package_mirror_command_options_ssh_options))])
            args.append(root)

            for target in self.config.package_mirror_target:
                l_args = args[:]
                l_args.append("%s:%s%s.." % (target, root, os.path.sep))
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
        self.logger.warning("ThreadPackageMirror failed to synchronise %s"%(str(reason)))

    def onSuccess(self, result, args):
        pid, target, is_deletion = args
        out, err, code = result
        if code == 0:
            self.logger.debug("ThreadPackageMirror succeed %s"%(str(result)))
            Common().removePackagesFromRsyncList(pid, target)
        else:
            self.logger.error("ThreadPackageMirror mirroring command failed %s"%(str(result)))
        
    def _runSub(self):
        def mirror_level0(result, args):
            pid, target, is_deletion = args
            out, err, code = result
            if code == 0:
                pkg = Common().packages[pid]
                self.logger.debug("Removing %s" % os.path.join(pkg.root, pid))
                os.rmdir(os.path.join(pkg.root, pid))
                exe = self.config.package_mirror_command
                args = []
                args.extend(self.config.package_mirror_level0_command_options)
                if type(self.config.package_mirror_command_options_ssh_options) == list:
                    args.extend(['--rsh', '/usr/bin/ssh -o %s'%(" -o ".join(self.config.package_mirror_command_options_ssh_options))])
                args.append(str("%s%s" % (pkg.root, os.path.sep)))
                args.append("%s:%s" % (target, pkg.root))
                self.logger.debug("execute mirror level0: %s %s"%(exe, str(args)))
                return createDeferred(exe, args, pid, target, False)
            else:
                self.logger.debug("ThreadPackageMirror failed %s"%(str(result)))

        def createDeferred(exe, args, pid, target, is_deletion = False):
            d = utils.getProcessOutputAndValue(exe, args)
            if is_deletion:
                d.addCallback(mirror_level0, (pid, target, is_deletion))
            else:
                d.addCallback(self.onSuccess, (pid, target, is_deletion))
            d.addErrback(self.onError, (pid, target))
            return d

        def cbEnding(result, self):
            self.logger.debug("ThreadPackageMirror end mirroring: %s" % str(result))
            self.working = False

        if self.working: 
            return
        self.working = True
        self.logger.debug("ThreadPackageMirror is looking for new things to mirror")
        dlist = []
        for pid, targets, pkg in Common().getPackagesThatNeedRsync():
            exe = self.config.package_mirror_command
            p_dir = os.path.join(pkg.root, pid)
            is_deletion = False
            if not os.path.exists(p_dir):
                # deletion = mirror empty dir + mirror top level on just 1 level
                os.mkdir(p_dir)
                # mark as deletion
                is_deletion = True
                
            for target in targets:
                if target == '':
                    continue
                self.logger.debug("ThreadPackageMirror will mirror %s on %s"%(pid, target))
                args = []
                args.extend(self.config.package_mirror_command_options)
                if type(self.config.package_mirror_command_options_ssh_options) == list:
                    args.extend(['--rsh', '/usr/bin/ssh -o %s'%(" -o ".join(self.config.package_mirror_command_options_ssh_options))])
                args.append(str(p_dir))
                args.append("%s:%s" % (target, pkg.root))
                self.logger.debug("execute : %s %s"%(exe, str(args)))

                dlist.append(createDeferred(exe, args, pid, target, is_deletion))

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
    
class ThreadLauncher(Singleton):
    def initialize(self, config):
        self.logger = logging.getLogger()
        self.config = config
        config_addons(config)
        Common().init(config)
        sync_status = PkgsRsyncStateSerializer().init(Common())
        
        if self.config.package_detect_activate:
            self.logger.debug("Package detect is activated")
            if self.config.package_detect_tmp_activate:
                self.logger.debug("Package detect in temporary folder is activated")
    
            self.logger.debug("Starting package detect thread")
            threadpd = ThreadPackageDetect(config)
            threadpd.setDaemon(True)
            threadpd.start()
            self.logger.debug("Package detect thread started")

        if self.config.package_mirror_activate:
            self.logger.debug("Starting package mirror thread")
            threadpm = ThreadPackageMirror(config, sync_status)
            threadpm.setDaemon(True)
            threadpm.start()
            self.logger.debug("Package mirror thread started")

            if self.config.package_global_mirror_activate:
                self.logger.debug("Starting global package mirror thread")
                threadgp = ThreadPackageGlobalMirror(config)
                threadgp.setDaemon(True)
                threadgp.start()
                self.logger.debug("Global package mirror thread started")

        thread_webserver.initialize(self.config)
        # FIXME: Little sleep because sometimes Python exits before the
        # threads have the time to start
        time.sleep(5)
