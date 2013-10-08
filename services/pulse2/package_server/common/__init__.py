#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
    Pulse2 PackageServer
"""
import os.path
import os
import stat
import time
import re
import shutil
import hashlib
import logging
import random
from pulse2.package_server.types import File
from pulse2.package_server.parser import PackageParser
from pulse2.package_server.find import Find
import pulse2.utils
from pulse2.package_server.utilities import md5file
from pulse2.package_server.common.serializer import PkgsRsyncStateSerializer

class Common(pulse2.utils.Singleton):
    """  Base class
    """

    MD5SUMS = "MD5SUMS"
    CONFXML = "conf.xml"

    SMART_DETECT_NOTPLUGGED = 0
    SMART_DETECT_NOCHANGES  = 1
    SMART_DETECT_PATHPB     = 2
    SMART_DETECT_CHANGES    = 3
    SMART_DETECT_ERROR      = 4

    def init(self, config):
        self.working = True
        self.working_pkgs = {}
        self.logger = logging.getLogger()
        self.logger.info("Loading PackageServer > Common")
        self.config = config

        self.file_properties = {}
        self.packages = {}
        self.mp2p = {}
        self.reverse = {}
        self.files = {}
        self.fid2file = {}
        self.parser = PackageParser()
        self.parser.init(self.config)
        self.desc = []
        self.already_declared = {}
        self.dontgivepkgs = {}
        self.need_assign = {}
        self.temp_check_changes = {'LAST':{}, 'LOOP':{}, 'SIZE':{}}
        self.packageDetectionDate = {}
        self.newAssociation = {}
        self.inEdition = {}
        self.mp2src = {}

        try:
            self._detectPackages()
            self._buildReverse()
            self._buildFileList()

            self.logger.info("Common : finish loading %d packages" % (len(self.packages)))
            self.working = False
        except Exception, e:
            self.logger.error("Common : failed to finish loading packages")
            self.working = False
            raise e

    def debug(self):
        self.logger.debug2("# START ################")
        self.logger.debug2(">> self.packages")
        self.logger.debug2(self.packages)
        self.logger.debug2(">> self.mp2p")
        self.logger.debug2(self.mp2p)
        self.logger.debug2(">> self.reverse")
        self.logger.debug2(self.reverse)
        self.logger.debug2(">> self.files")
        self.logger.debug2(self.files)
        self.logger.debug2(">> self.fid2file")
        self.logger.debug2(self.fid2file)
        self.logger.debug2(">> self.desc")
        self.logger.debug2(self.desc)
        self.logger.debug2(">> self.already_declared")
        self.logger.debug2(self.already_declared)
        self.logger.debug2(">> self.dontgivepkgs")
        self.logger.debug2(self.dontgivepkgs)
        self.logger.debug2(">> self.need_assign")
        self.logger.debug2(self.need_assign)
        self.logger.debug2(">> self.temp_check_changes")
        self.logger.debug2(self.temp_check_changes)
        self.logger.debug2(">> self.packageDetectionDate")
        self.logger.debug2(self.packageDetectionDate)
        self.logger.debug2(">> self.newAssociation")
        self.logger.debug2(self.newAssociation)
        self.logger.debug2(">> self.inEdition")
        self.logger.debug2(self.inEdition)
        self.logger.debug2(">> self.mp2src")
        self.logger.debug2(self.mp2src)
        self.logger.debug2("# END ##################")

    def _detectPackages(self, new = False):
        runid = int(random.random()*50000)
        if len(self.config.mirrors) > 0:
            for mirror_params in self.config.mirrors:
                try:
                    access = {
                        'proto':self.config.proto,
                        'file_access_uri':mirror_params['file_access_uri'],
                        'file_access_port':mirror_params['file_access_port'],
                        'file_access_path':mirror_params['file_access_path']
                    }
                    if mirror_params.has_key('mirror'):
                        access = {
                            'proto':'',
                            'file_access_uri':'',
                            'file_access_port':'',
                            'file_access_path':'',
                            'mirror':mirror_params['mirror']
                        }
                    self.logger.debug("Getting packages for %s %s %s" % (
                        mirror_params['mount_point'],
                        mirror_params['src'],
                        str(access),
                    ))
                    self.mp2src[mirror_params['mount_point']] = mirror_params['src']
                    self._getPackages(
                        mirror_params['mount_point'],
                        mirror_params['src'],
                        access,
                        new,
                        runid
                    )
                except Exception, e:
                    mp = mirror_params['mount_point']
                    if self.mp2src.has_key(mp): del self.mp2src[mp]
                    self.logger.error("_detectPackages failed for mirrors")
                    self.logger.error(str(e))

        if len(self.config.package_api_get) > 0:
            for mirror_params in self.config.package_api_get:
                try:
                    self.logger.debug("Getting packages for %s %s" % (
                        mirror_params['mount_point'],
                        mirror_params['src']
                    ))
                    self.mp2src[mirror_params['mount_point']] = mirror_params['src']
                    self._getPackages(mirror_params['mount_point'], mirror_params['src'], {}, new, runid)
                except Exception, e:
                    mp = mirror_params['mount_point']
                    if self.mp2src.has_key(mp): del self.mp2src[mp]
                    self.logger.error("_detectPackages failed for package api get")
                    self.logger.error(e)

        if len(self.config.package_api_put) > 0:
            for mirror_params in self.config.package_api_put:
                try:
                    self.logger.debug("Getting packages for %s %s" % (
                        mirror_params['mount_point'],
                        mirror_params['src']
                    ))
                    self.mp2src[mirror_params['mount_point']] = mirror_params['src']
                    self._getPackages(mirror_params['mount_point'], mirror_params['src'], {}, new, runid)
                except Exception, e:
                    mp = mirror_params['mount_point']
                    if self.mp2src.has_key(mp): del self.mp2src[mp]
                    self.logger.error("_detectPackages failed for package api put")
                    self.logger.error(e)

    def _detectRemovedAndEditedPackages(self):
        """
        Look for no more available conf.xml files, and unregister packages.
        """
        todelete = []
        for pid in self.packages:
            try:
                proot = self._getPackageRoot(pid)
                confxml = os.path.join(proot, "conf.xml")
                if os.path.exists(confxml) and self.packageDetectionDate.has_key(pid) and self.packageDetectionDate[pid] != self.__getDate(confxml): # EDITED
                    self.logger.debug("Package %s has been modified (%s)" % (pid, confxml))
                    #self.__removePackage(pid, proot)
                    #todelete.append(pid)
                    #if confxml in self.already_declared:
                    #    del self.already_declared[confxml]
                elif not os.path.exists(confxml): # SUPPRESSED
                    self.logger.debug("Package %s no more exists (%s)" % (pid, confxml))
                    self.__removePackage(pid, proot)
                    todelete.append(pid)
                    if confxml in self.already_declared:
                        del self.already_declared[confxml]
            except Exception, e:
                self.logger.error("Common._detectRemovedAndEditedPackages : an exception happened")
                self.logger.debug(type(e))
                self.logger.info(e)
        if not self.config.package_mirror_activate:
            # For the mirror stuff to work, we do not remove the package from
            # our main packages dict
            for pid in todelete:
                self.suppressFromInternal(pid)

    def suppressFromInternal(self, pid):
        if not self.packages.has_key(pid):
            self.logger.debug("Package %s is not in Common().packages"%(pid))
            if self.packageDetectionDate.has_key(pid):
                del self.packageDetectionDate[pid]
        else:
            self.logger.debug("Package %s removed from internal hashes"%(pid))
            pkg = self.packages[pid]
            try:
                # WARN if self.reverse[pkg.label] dont exists!
                del self.reverse[pkg.label][pkg.version]
                if len(self.reverse[pkg.label].keys()) == 0:
                    del self.reverse[pkg.label]
            except Exception, e:
                self.logger.error("Common.suppressFromInternal : an exception happened")
                self.logger.debug(type(e))
                self.logger.info(e)
            if self.packageDetectionDate.has_key(pid):
                del self.packageDetectionDate[pid]
            if self.packages.has_key(pid):
                del self.packages[pid]

    def __removePackage(self, pid, proot):
        # Remove the package from the mirror
        done = []
        for desc in self.descBySrc(os.path.dirname(proot)):
            if desc['type'] != 'mirror_files':
                mp = desc['mp']
                if pid in self.mp2p[mp]:
                    if mp not in done:
                        self.dropPackage(pid, mp)
                        self.desassociatePackage2mp(pid, mp)
                        done.append(mp)

    def moveCorrectPackages(self):
        """
        Look for valid package in the input dir of each, and move them to the
        mirror repository
        """
        if self.working:
            self.logger.debug("Common : already working")
            return
        self.working = True
        self.logger.debug("Common : getting valid temporary packages")
        try:
            if len(self.config.package_api_put) > 0:
                for mirror_params in self.config.package_api_put:
                    if os.path.exists(mirror_params['tmp_input_dir']):
                        self._moveNewPackage(mirror_params)
        except Exception, e:
            self.logger.error("moveCorrectPackages: " + str(e))
        self.working = False

    def detectNewPackages(self):
        if self.working:
            self.logger.debug("Common.detectNewPackages : already working")
            return False
        try: # BUG : need to put the catch level down!
            self.working = True
            self.working_pkgs = {}
            self.logger.debug1("Common.detectNewPackages : detecting new packages...")
            self._detectPackages(True)
            self.logger.debug1("Common.detectNewPackages : detecting removed or edited packages...")
            self._detectRemovedAndEditedPackages()
            self.logger.debug1("Common.detectNewPackages : build reverse list...")
            self._buildReverse()
            self.logger.debug1("Common.detectNewPackages : build file list...")
            self._buildFileList()
            self.logger.debug1("Common.detectNewPackages : done")
            self.working = False
            return True
        except TypeError, e:
            self.working = False
            self.logger.error("Common.detectNewPackages : a type error happened")
            self.logger.info(e)
        except Exception, e:
            self.working = False
            self.logger.error("Common.detectNewPackages : an exception happened")
            self.logger.debug(type(e))
            self.logger.info(e)
        return False

    def setDesc(self, description):
        self.desc = description

    def h_desc(self, mp):
        for d in self.desc:
            if d['mp'] == mp:
                return d
        return None

    def descBySrc(self, src):
        ret = []
        for d in self.desc:
            if 'src' in d and d['src'] == src:
                ret.append(d)
        return ret

    def checkPath4package(self, path): # TODO check if still used
        # TODO get conf.xml files in path, parse them, and fill the hashes
        return False

    def associatePackage2mp(self, pid, mp):
        conf = self.h_desc(mp)
        for desc in self.descBySrc(conf['src']):
            if desc['type'] != 'mirror_files':
                if not self.mp2p[desc['mp']].__contains__(pid):
                    self.logger.debug("Link package %s to %s" % (pid, desc['mp']))
                    self.mp2p[desc['mp']].append(pid)
        return True

    def desassociatePackage2mp(self, pid, mp):
        """
        Remove association between a package and mirrors
        """
        conf = self.h_desc(mp)
        for desc in self.descBySrc(conf['src']):
            if desc['type'] != 'mirror_files':
                if pid in self.mp2p[desc['mp']]:
                    self.logger.debug("Unlink package %s from %s" % (pid, desc['mp']))
                    self.mp2p[desc['mp']].remove(pid)
        return True

    ######################################################
    # methods to treat all rsync mechanism
    def getAllPackageRoot(self):
        ret = {}
        for m in self.desc:
            if m.has_key('src') and not ret.has_key(m['src']):
                ret[m['src']] = None
        return ret.keys()

    def rsyncPackageOnMirrors(self, pid = None):
        if pid == None:
            self.logger.debug("rsyncPackageOnMirrors for all packages")
            for pid in self.packages:
                self.dontgivepkgs[pid] = self.config.package_mirror_target[:]
        else:
            self.logger.debug("rsyncPackageOnMirrors for '%s'"%(pid))
            self.dontgivepkgs[pid] = self.config.package_mirror_target[:]
        PkgsRsyncStateSerializer().serialize()

    def isPackageAccessible(self, pid):
        return (not self.dontgivepkgs.has_key(pid) and not self.need_assign.has_key(pid) and self.packages[pid].hasFile())

    def getPackagesThatNeedRsync(self):
        if self.dontgivepkgs != {}:
            self.logger.debug("getPackagesThatNeedRsync : " + str(self.dontgivepkgs))
        ret = []
        rem = []
        for x in self.dontgivepkgs:
            if not self.packages.has_key(x) or not self.packages[x]:
                rem.append(x)
            else:
                ret.append([x, self.dontgivepkgs[x], self.packages[x]])
        for x in rem:
            del self.dontgivepkgs[x]
        return ret

    def removePackagesFromRsyncList(self, pid, target):
        if self.dontgivepkgs.has_key(pid):
            modif = False
            try:
                i = self.dontgivepkgs[pid].index(target)
                del self.dontgivepkgs[pid][i]
                modif = True
            except ValueError:
                self.logger.warning("PackageMirror: no %s target defined for package %s" % (target, pid))
            if len(self.dontgivepkgs[pid]) == 0:
                del self.dontgivepkgs[pid]
                modif = True
                self.logger.info("PackageMirror: package %s successfully mirrored everywhere" % pid)
                pkg = self.packages[pid]
                p_dir = pkg.root
                if not os.path.exists(p_dir):
                    self.logger.debug("PackageMirror: removing package %s from available packages" % pid)
                    self.suppressFromInternal(pid)
            if modif:
                PkgsRsyncStateSerializer().serialize()
            return True
        else:
            self.logger.warning("PackageMirror don't know this package : %s"%(pid))
            return False
    ######################################################

    def addPackage(self, pid, pa, need_assign = True):
        # return pid for success
        # raise ARYDEFPKG for already existing package
        try:
            if self.packages.has_key(pid):
                if self.packages[pid] == pa:
                    return pid
                raise Exception("ARYDEFPKG")
            if need_assign:
                Common().need_assign[pid] = True
            elif self.config.package_mirror_activate:
                Common().rsyncPackageOnMirrors(pid)
            self.packages[pid] = pa
            if not self.reverse.has_key(pa.label):
                self.reverse[pa.label] = {}
            self.reverse[pa.label][pa.version] = pid
        except Exception, e:
            self.logger.error("addPackage failed")
            self.logger.error(e)
            raise e
        return pid

    def reloadPackage(self, pid, pack):
        try:
            old = self.packages[pid]
            try:
                self.reverse[old.label][old.version] = None # TODO : can't remove, so we will have to check that value != None...
            except Exception, e:
                self.logger.error("Common.reloadPackage : an exception happened")
                self.logger.debug(type(e))
                self.logger.info(e)
            pack.setFiles(old.files)
            pack.size = old.size
            if self.config.package_mirror_activate:
                Common().rsyncPackageOnMirrors(pid)
            self.packages[pid] = pack
            if not self.reverse.has_key(pack.label):
                self.reverse[pack.label] = {}
            self.reverse[pack.label][pack.version] = pid
        except Exception, e:
            self.logger.error("reloadPackage failed")
            self.logger.error(e)
            raise e
        return pid

    def editPackage(self, pid, pack, need_assign = True):
        try:
            if self.packages.has_key(pid):
                old = self.packages[pid]
                try:
                    self.reverse[old.label][old.version] = None # TODO : can't remove, so we will have to check that value != None...
                except Exception, e:
                    self.logger.error("Common.editPackage : an exception happened")
                    self.logger.debug(type(e))
                    self.logger.info(e)
                    raise e
                pack.setFiles(old.files)
                pack.size = old.size
            if need_assign:
                Common().need_assign[pid] = True
            elif self.config.package_mirror_activate:
                Common().rsyncPackageOnMirrors(pid)
            self.packages[pid] = pack
            if not self.reverse.has_key(pack.label):
                self.reverse[pack.label] = {}
            self.reverse[pack.label][pack.version] = pid
        except Exception, e:
            self.logger.error("editPackage failed")
            self.logger.error(e)
            raise e
        return pid

    def writePackageTo(self, pid, mp):
        if not self.packages.has_key(pid):
            self.logger.error("package %s is not defined"%(pid))
            raise Exception("UNDEFPKG")
        xml = self.parser.concat(self.packages[pid])
        params = self.h_desc(mp)
        path = params['src']

        confdir = os.path.join(path, pid)
        self.packages[pid].setRoot(confdir)
        confxml = os.path.join(confdir, "conf.xml")
        confxmltmp = confxml + '.tmp'
        if not os.path.exists(confdir):
            os.mkdir(confdir)
        try:
            f = open(confxmltmp, 'w+')
            f.write(xml)
            f.close()
        except Exception, e:
            self.logger.error("Error while writing new conf.xml file")
            self.logger.error(e)
            if os.path.exists(confxmltmp):
                os.remove(confxmltmp)
            del self.inEdition[pid]
            return (None, None)
        if os.path.exists(confxml):
            os.remove(confxml)
        # notify it's an edition
        self.inEdition[pid] = True
        shutil.move(confxmltmp, confxml)
        self.packageDetectionDate[pid] = self.__getDate(confxml)
        if not os.path.exists(confxml):
            self.logger.error("Error while moving the new conf.xml file")

        return [pid, confdir]

    def associateFiles(self, mp, pid, files, level = 0):
        # Always need assign because this function can
        # add new files to existing package
        Common().need_assign[pid] = True
        if not self.packages.has_key(pid):
            return [False, "This package don't exists"]
        path = self._getPackageRoot(pid)
        self.logger.debug("File association will put files in %s" % (path))
        files_out = []
        err = 0
        level = int(level)
        for f in files:
            if level == 0:
                fo = os.path.join(path, os.path.basename(f))
                self.logger.debug("File association will move %s to %s" % (f, fo))
                files_out.append(fo)
                if os.path.isdir(f):
                    shutil.copytree(f, fo)
                    self.logger.debug("File association will remove %s"%(f))
                    shutil.rmtree(f)
                else:
                    shutil.copy2(f, fo)
                    self.logger.debug("File association will remove %s"%(f))
                    os.unlink(f)
            elif level == 1:
                for f1 in os.listdir(f):
                    f1 = os.path.join(f, f1)
                    fo = os.path.join(path, os.path.basename(f1))
                    self.logger.debug("File association will move %s to %s" % (f1, fo))
                    files_out.append(fo)
                    if os.path.isdir(f1):
                        shutil.copytree(f1, fo)
                        self.logger.debug("File association will remove %s"%(f1))
                        shutil.rmtree(f1)
                    else:
                        shutil.copy2(f1, fo)
                        self.logger.debug("File association will remove %s"%(f1))
                        os.unlink(f1)
                self.logger.debug("File association will remove %s"%(f1))
                shutil.rmtree(f)
        self._treatFiles(files_out, mp, pid, access = {})
        if len(files_out):
            self._createMD5File(os.path.dirname(files_out[0]))
        del Common().need_assign[pid]
        Common().newAssociation[pid] = True
        if self.config.package_mirror_activate:
            Common().rsyncPackageOnMirrors(pid)
        # Force new packages detection
        self.detectNewPackages()
        # Reloading all packages info
        desc = self.desc
        self.init(self.config)
        self.desc = desc
        return [True, err]

    def removeFilesFromPackage(self,pid,files):
        # Checking if package exists
        if not self.packages.has_key(pid):
            return [False, "This package don't exists"]
        # Checking files param
        if type(files) == str:
            files = [files]
        if type(files) != list:
            return [False, "files param must be string or array of string"]
        path = self._getPackageRoot(pid)
        # Deleting files
        try:
            for file in files:
                filepath = os.path.join(path, file)
                os.unlink(filepath)
            # Reloading all packages info
            desc = self.desc
            self.init(self.config)
            self.desc = desc
            return [True,0]
        except Exception as e:
            return [False,str(e)]


    def dropPackage(self, pid, mp):
        """
        Physically removes the given package content from the disk (if setted)
        Also mark the package as not available
        """
        if not self.packages.has_key(pid):
            self.logger.error("package %s is not defined"%(pid))
            raise Exception("UNDEFPKG")
        params = self.h_desc(mp)
        path = params['src']
        #self.logger.debug()

        if self.config.real_package_deletion: # TODO : why do we pass here when modifying!
            p_dir = os.path.join(path, pid)
            self.logger.debug("is going to delete %s" % (p_dir))
            shutil.rmtree(p_dir, ignore_errors = True)
        else:
            confxml = os.path.join(path, pid, 'conf.xml')
            if os.path.exists(confxml):
                shutil.move(os.path.join(path, pid, 'conf.xml'), os.path.join(path, pid, 'conf.xml.rem'))
        # TODO remove package from mirrors
        if self.config.package_mirror_activate:
            Common().rsyncPackageOnMirrors(pid)

        return pid

    def writeFileIntoPackage(self, pid, file):
        pass

    def packagelist(self, pidlist, mp = None):
        return self.getPackages(mp, False, True, pidlist)

    def package(self, pid, mp = None):
        return self.__packageSelection(pid, mp, False, True)

    def getPendingPackages(self, mp):
        ret = self.getPackages(mp, True)
        return ret

    def getPackages(self, mp, pending = False, all = False, pidlist = None): #TODO check the clone memory impact
        # "all" override "pending" flag
        ret = {}
        ordered = []
        try:
            if pidlist == None:
                for k in self.packages:
                    if pidlist != None:
                        if not k in pidlist:
                            continue
                    p = self.__packageSelection(k, mp, pending, all)
                    if p != None:
                        ret[k] = p
                return ret
            else:
                for id in pidlist:
                    if not self.packages.has_key(id): # shouldn't happen, but who knows...
                        continue
                    p = self.__packageSelection(id, mp, pending, all)
                    if p != None:
                        ordered.append(p)
                return ordered
        except Exception, e:
            self.logger.error("getPackages failed")
            self.logger.error(e)
            return None

    def __packageSelection(self, pid, mp = None, pending = False, all = False):
        is_acc = self.isPackageAccessible(pid)
        if not all:
            is_acc = is_acc and not self.newAssociation.has_key(pid) and not self.inEdition.has_key(pid)
        if (is_acc and not pending) or (not is_acc and pending) or (all and is_acc):
            if (mp != None and pid in self.mp2p[mp]) or (mp == None):
                return self.packages[pid]
        return None

    def getRsyncStatus(self, pid, mp):
        if self.isPackageAccessible(pid):
            return map(lambda h: [h, 'OK'], self.config.package_mirror_target)
        if not pid in self.dontgivepkgs:
            return map(lambda h: [h, 'NOK'], self.config.package_mirror_target)
        ret = []
        nok = self.dontgivepkgs[pid]
        for h in self.config.package_mirror_target:
            if h in nok:
                ret.append([h, 'NOK'])
            else:
                ret.append([h, 'OK'])
        return ret

    def reverse(self, mp): #TODO check the clone memory impact
        ret = []
        try:
            for k in self.reverse:
                if self.mp2p.has_key(k):
                    ret.append(k)
        except Exception, e:
            self.logger.error("reverse failed")
            self.logger.error(e)
            raise e
        return ret

    def getFile(self, fid, mp = None):
        if self.files.has_key(fid):
            return self.files[fid].toURI(mp)
        return None

# private
    def _getPackageRoot(self, pid):
        return self.packages[pid].root

    def _moveNewPackage(self, mirror_params):
        Find().find(mirror_params['tmp_input_dir'], self._moveNewPackageSub, [mirror_params['src']])

    def _moveNewPackageSub(self, file, src):
        if os.path.basename(file) == 'conf.xml':
            file = os.path.dirname(file)
            confxml = os.path.join(file, "conf.xml")
            l_package = self.parser.parse(confxml)
            l_package.setRoot(os.path.dirname(file))
            if l_package == None:
                return False
            if not os.path.exists(os.path.join(src, l_package.id)):
                self.logger.debug("New valid temporary package detected")
                shutil.copytree(file, os.path.join(src, l_package.id))

    def _getPackages(self, mp, src, access = None, new = False, runid = -1):
        if access is None: # dont modify the default value!
            access = {}
        if not os.path.exists(src):
            raise Exception("Src does not exists for mount point '#{%s}' (%s)" %(mp, src))

        if new:
            Find().find(src, self._treatNewConfFile, (mp, access, runid))
        else:
            self.mp2p[mp] = []
            Find().find(src, self._treatConfFile, (mp, access))

    def _createMD5File(self, dirname):
        """
        Create the MD5SUMS file for a directory content
        """
        fmd5name = os.path.join(dirname, self.MD5SUMS)
        if os.path.exists(fmd5name):
            os.unlink(fmd5name)
        if not os.path.exists(fmd5name): # create file only if it do not exists
            self.logger.info("Computing MD5 sums file %s" % fmd5name)
            md5sums = []
            for root, dirs, files in os.walk(dirname):
                for name in files:
                    if name != self.CONFXML:
                        try:
                            filepath = os.path.join(root, name)
                            f = file(filepath, "rb")
                            md5sums.append([filepath[len(dirname)+1:], hashlib.md5(f.read()).hexdigest()])
                            f.close()
                        except IOError, e:
                            self.logger.warn("Error while reading %s: %s" % (filepath, e))
            fmd5 = file(fmd5name, "w+b")
            md5sums.sort(lambda x, y: cmp(x[0], y[0]))
            for name, md5hash in md5sums:
                fmd5.write("%s  %s\n" % (md5hash, name))
                self.logger.debug("%s  %s\n" % (md5hash, name))
            fmd5.close()

    def _hasChanged(self, dir, pid, runid = -1):
        if not self.config.package_detect_smart:
            return self.SMART_DETECT_NOTPLUGGED
        if not os.path.exists(dir) or not os.path.isdir(dir):
            return self.SMART_DETECT_PATHPB

        t = time.time()
        known_action = False
        failure = False
        # check that the last modification date is old enough
        if self.config.SMART_DETECT_LAST in self.config.package_detect_smart_method:
            if self.temp_check_changes['LAST'].has_key(pid):
                self.temp_check_changes['LAST'][pid]['###HASCHANGED_LAST###'] = False
            else:
                self.temp_check_changes['LAST'][pid] = { '###HASCHANGED_LAST###':False }
            # start by checking the package directory
            self.__subHasChangedLast(dir, pid, t)
            # then if it has not changed, we check what's inside
            if not self.temp_check_changes['LAST'][pid]['###HASCHANGED_LAST###']:
                Find().find(dir, self.__subHasChangedLast, [pid,t])
            # something has changed in the last X secondes
            if self.temp_check_changes['LAST'][pid]['###HASCHANGED_LAST###']:
                self.logger.debug("package '%s' was modified in the last %s seconds"%(str(pid), str(self.config.package_detect_smart_time)))
                failure = True
            known_action = True

        # check that the package size has not change between two detect loop (detected one loop after the package is here for real)
        if self.config.SMART_DETECT_SIZE in self.config.package_detect_smart_method:
            if not self.temp_check_changes['SIZE'].has_key(pid):
                self.temp_check_changes['SIZE'][pid] = [0, 0]
            previous, previous_t = self.temp_check_changes['SIZE'][pid]
            if (t - previous_t) < (self.config.package_detect_loop - 1): # only try this method once per detect loop
                failure = True
            else:
                self.__subHasChangedGetGlobalSize(dir, pid, previous_t)
                size, t2 = self.temp_check_changes['SIZE'][pid]
                if previous != size:
                    self.temp_check_changes['SIZE'][pid] = [size, t]
                    self.logger.debug("package '%s' was modified, '%s' bytes added"%(str(pid), str(size-previous)))
                    failure = True
            if failure and (self.newAssociation.has_key(pid) or self.inEdition.has_key(pid)):
                failure = False
            known_action = True

        if self.config.SMART_DETECT_LOOP in self.config.package_detect_smart_method and False: # TOBEDONE
            if not self.temp_check_changes['LOOP'].has_key(pid):
                self.temp_check_changes['LOOP'][pid] = {}
            self.temp_check_changes['LOOP'][pid]['###HASCHANGED_LOOP###'] = False
            Find().find(dir, self.__subHasChangedLoop, [pid,time.time(),runid])
            if self.temp_check_changes['LOOP'][pid]['###HASCHANGED_LOOP###']:
                failure = True
            else:
                del self.temp_check_changes['LOOP'][pid]
            known_action = True

        # if one of the action fail (detect that at least one file changed)
        if failure:
            return self.SMART_DETECT_CHANGES

        # if some of the actions have been executed and we are still there, that mean that they succeed, ie: no changes detected
        if known_action:
            return self.SMART_DETECT_NOCHANGES

        self.logger.debug("smart detect hasChange, dont know this smart method : %s"%(str(self.config.packageDetectSmartMethod)))
        return self.SMART_DETECT_ERROR

    def __subHasChangedGetGlobalSize(self, dir, pid, previous_t=None):
        if previous_t == None:
            previous_t = time.time() - self.config.package_detect_loop
        self.temp_check_changes['SIZE'][pid] = [0, previous_t]
        Find().find(dir, self.__subHasChangedGetSize, [pid])

    def __subHasChangedGetSize(self, file, pid):
        try:
            self.temp_check_changes['SIZE'][pid][0] += os.path.getsize(file)
        except Exception, e:
            self.logger.debug("__subHasChangedGetSize except %s"%(str(e)))
            raise e

    def __initialiseChangedLast(self, pid, file, s = None):
        if s == None:
            s = self.__getDate(file)
        if not self.temp_check_changes['LAST'].has_key(pid):
            self.temp_check_changes['LAST'][pid] = { '###DATE###' : s }
        elif not self.temp_check_changes['LAST'][pid].has_key('###DATE###') or self.temp_check_changes['LAST'][pid]['###DATE###'] < s:
            self.temp_check_changes['LAST'][pid]['###DATE###'] = s

    def __subHasChangedLast(self, file, pid, t):
        """
        check if the file has change in the last X secondes
        if yes, ###HASCHANGED_LAST### is set to true
        """
        s = self.__getDate(file)
        if (t - s) < self.config.package_detect_smart_time:
            # if the file has just been associated
            # TODO check if the file has just been edited
            if self.newAssociation.has_key(pid) or self.inEdition.has_key(pid):
                self.__initialiseChangedLast(pid, file, s)
                self.logger.debug("\t")

            if not self.temp_check_changes['LAST'][pid].has_key('###DATE###'):
                self.temp_check_changes['LAST'][pid]['###HASCHANGED_LAST###'] = True
            elif self.temp_check_changes['LAST'][pid]['###DATE###'] < s:
                self.temp_check_changes['LAST'][pid]['###HASCHANGED_LAST###'] = True

    def __subHasChangedLoop(self, file, pid, t, runid = -1):
        s = self.__getDate(file)
        if self.temp_check_changes['LOOP'][pid].has_key(file):
            if s != self.temp_check_changes['LOOP'][pid][file][0]:
                self.temp_check_changes['LOOP'][pid][file][0] = s
                self.temp_check_changes['LOOP'][pid]['###HASCHANGED_LOOP###'] = True
            elif runid == self.temp_check_changes['LOOP'][pid][file][1]:
                self.temp_check_changes['LOOP'][pid]['###HASCHANGED_LOOP###'] = True
        else:
            self.temp_check_changes['LOOP'][pid][file] = [s, runid]
            self.temp_check_changes['LOOP'][pid]['###HASCHANGED_LOOP###'] = True
        self.temp_check_changes['LOOP'][pid][file][1] = runid

    def __getDate(self, conffile):
        return os.stat(conffile)[stat.ST_MTIME]

    def _treatNewConfFile(self, file, mp, access, runid = -1):
        if os.path.basename(file) == 'conf.xml':
            l_package = self.parser.parse(file)
            if l_package == None: return
            if self.working_pkgs.has_key(l_package.id): return
            l_package.setRoot(os.path.dirname(file))
            isReady = self._hasChanged(os.path.dirname(file), l_package.id, runid)
            if not self.already_declared.has_key(file):
                if isReady == self.SMART_DETECT_CHANGES:
                    self.logger.debug("'%s' has changed recently"%(str(l_package.id)))
                else:
                    if not self.need_assign.has_key(l_package.id):
                        self.logger.debug("detect a new package %s"%(l_package.id))
                        self._createMD5File(os.path.dirname(file))
                        pid = self._treatDir(os.path.dirname(file), mp, access, True, l_package)
                        self.associatePackage2mp(pid, mp)
                        self.already_declared[file] = True
                        if self.newAssociation.has_key(pid):
                            del self.newAssociation[pid]
                        if self.inEdition.has_key(pid):
                            del self.inEdition[pid]
                        self.packageDetectionDate[pid] = self.__getDate(file)
                        if self.config.package_mirror_activate:
                            Common().rsyncPackageOnMirrors(pid)
                    else:
                        self.logger.debug("detect a new package that is in assign phase %s"%(l_package.id))
            else:
                if self.inEdition.has_key(l_package.id): # the config file has been changed from the gui, only need to get new date and size
                    pid = l_package.id
                    self.logger.debug("detect an already detected package (edition mode) : %s"%(pid))
                    del self.inEdition[pid]
                    # put the new date/size
                    self.packageDetectionDate[pid] = self.__getDate(file)
                    self.__subHasChangedGetGlobalSize(l_package.root, pid)
                    self.temp_check_changes['LAST'][pid]['###DATE###'] = self.packageDetectionDate[pid]

                    if self.config.package_mirror_activate:
                        Common().rsyncPackageOnMirrors(pid)
                elif isReady == self.SMART_DETECT_CHANGES: # reload the content of the config file
                    self.logger.debug("'%s' has changed"%(str(l_package.id)))
                    self._createMD5File(os.path.dirname(file))
                    pid = self._treatDir(os.path.dirname(file), mp, access, True, l_package, True) # force loading
                    self.associatePackage2mp(pid, mp)
                    self.packageDetectionDate[pid] = self.__getDate(file)
                    if self.config.package_mirror_activate:
                        Common().rsyncPackageOnMirrors(pid)


    def _treatConfFile(self, file, mp, access):
        if os.path.basename(file) == 'conf.xml':
            if self.already_declared.has_key(file) and self.already_declared[file]:
                self._treatDir(os.path.dirname(file), mp, access)
                return

            self.logger.debug("_treatConfFile %s"%(file))
            self._createMD5File(os.path.dirname(file))
            pid = self._treatDir(os.path.dirname(file), mp, access)
            self.already_declared[file] = True
            if self.newAssociation.has_key(pid):
                del self.newAssociation[pid]
            if self.inEdition.has_key(pid):
                del self.inEdition[pid]
            self.packageDetectionDate[pid] = self.__getDate(file)
            l_package = self.packages[pid]
            self.__subHasChangedGetGlobalSize(l_package.root, l_package.id)
            self.temp_check_changes['LAST'][pid] = {'###DATE###': self.packageDetectionDate[pid]}

    def _treatFiles(self, files, mp, pid, access):
        toRelative = self.packages[pid].root
        for f in files:
            path = re.sub('//', '/', '/'+re.sub(re.escape(os.path.dirname(toRelative)), '', os.path.dirname(f)))
            size = int(self._treatFile(pid, f, path, access))
            self.packages[pid].size = int(self.packages[pid].size) + size

    def _treatDir(self, file, mp, access, new = False, l_package = None, force = False):
        pid = None
        try:
            if os.path.isdir(file):
                self.logger.debug("loading package metadata (xml) in %s"%(file))
                if l_package == None:
                    confxml = os.path.join(file, "conf.xml")
                    l_package = self.parser.parse(confxml)
                l_package.setRoot(file)
                if l_package == None:
                    self.logger.debug("package failed to parse in %s"%(file))
                    return False

                pid = l_package.id
                if not pid in self.working_pkgs:
                    self.working_pkgs[pid] = l_package

                self.mp2p[mp].append(pid)
                if not force and self.packages.has_key(pid) and not self.newAssociation.has_key(pid) and not self.inEdition.has_key(pid):
                    if new:
                        self.logger.debug("package '%s' already exists" % (pid))
                    return False

                toRelative = self.mp2src[mp]
                size = 0
                self.logger.debug("declare %s in packages"%(pid))
                self.packages[pid] = l_package
                if len(self.packages[pid].specifiedFiles) > 0:
                    # just get sizes and md5
                    for sfile in self.packages[pid].specifiedFiles:
                        f = "%s%s%s%s%s" % (toRelative, os.sep, pid, toRelative, sfile['filename'])
                        path = re.sub(os.path.basename(f) , '', "%s%s%s%s" % (os.sep, pid, os.sep, sfile['filename']))
                        if not os.exists(f):
                            self.logger.warn("the file %s is declared in the package configuration file, but is not in the package directory"%(sfile['filename']))
                            raise Exception("MISSINGFILE")
                        size += self._treatFile(pid, f, path, access, sfile['id'])
                else:
                    # find all files and then get sizes and md5
                    files = self._getFiles(file)
                    for f in files:
                        path = '/'+re.sub(re.escape(toRelative+os.sep), '', os.path.dirname(f))
                        size += self._treatFile(pid, f, path, access)
                self.packages[pid].size = size
                self.logger.debug("Package size = %d" % size)

                if new:
                    self.desassociatePackage2mp(pid, mp)
        except Exception, err:
            if hasattr(err, 'message') and err.message == 'MISSINGFILE':
                self.logger.error("__treatDir failed (missing file)")
                self.logger.error(err)
                #"package %s won't be loaded because one of the declared file is missing"% (pid))
                self.mp2p[mp][pid] = None
            elif hasattr(err, 'message') and err.message == 'DBLFILE':
                self.logger.error("__treatDir failed (double file)")
                self.logger.error(err)
                # :"package %s won't be loaded because one of its file is already declared in an other package"%(pid))
                self.mp2p[mp][pid] = None
            elif hasattr(err, 'message'):
                self.logger.error("__treatDir failed")
                self.logger.error(err.message)
                self.mp2p[mp][pid] = None
            else:
                self.logger.error("__treatDir failed")
                self.logger.error(err)
                if pid != None:
                    self.mp2p[mp][pid] = None
            raise err
        return str(pid)

    def _treatFile(self, pid, f, path, access = None, fid = None):
        if access is None: # dont modify the default value!
            access = {}
        (fsize, fmd5) = [0,0]
        if not self.file_properties.has_key(f):
            fsize = os.path.getsize(f)
            fmd5 = md5file(f)
            self.logger.debug('ish: Creating md5 entry for '+f)
            self.file_properties[f] = [fsize, fmd5]
        else:
            (fsize, fmd5) = self.file_properties[f]

        file = File(os.path.basename(f), path, fmd5, fsize, access, fid)
        self.packages[pid].addFile(file)
        if self.fid2file.has_key(file.id) and self.fid2file[file.id] != file.checksum:
            raise Exception("DBLFILE")
        self.fid2file[file.id] = file.checksum
        return fsize

    def _getFiles(self, path):
        files = []
        for pfile in os.listdir(path):
            if os.path.isdir("%s%s%s" % (path , os.sep, pfile)):
                files.extend(self._getFiles("%s%s%s" % (path , os.sep, pfile)))
            else:
                if os.path.basename(pfile) != 'conf.xml':
                    files.append("%s%s%s" % (path , os.sep, pfile))
        return files

    def _buildReverse(self):
        for package in self.working_pkgs.values():
            if not self.reverse.has_key(package.label):
                self.reverse[package.label] = {}
            self.reverse[package.label][package.version] = package.id

    def _buildFileList(self):
        for package in self.working_pkgs.values():
            self.logger.debug("Building file list for package %s" % package.id)
            for file in package.files.internals: # TODO dont access to internals !
                self.logger.debug("file id %s => %s" % (file.id, file.toURI()))
                self.files[file.id] = file
