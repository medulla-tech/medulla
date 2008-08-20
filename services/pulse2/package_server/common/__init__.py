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

"""
    Pulse2 PackageServer
"""
import twisted.web.html
import twisted.web.xmlrpc
import os
import re
import shutil
import logging
from pulse2.package_server.types import *
from pulse2.package_server.parser import PackageParser
from pulse2.package_server.find import Find
from pulse2.package_server.utilities import md5file, md5sum, Singleton


class Common(Singleton):
    def init(self, config):
        self.working = True
        self.working_pkgs = []
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
        
    def _detectPackages(self, new = False):
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
                    self._getPackages(
                        mirror_params['mount_point'],
                        mirror_params['src'],
                        access,
                        new
                    )
                except Exception, e:
                    self.logger.error(e)

        if len(self.config.package_api_get) > 0:
            for mirror_params in self.config.package_api_get:
                try:
                    self._getPackages(mirror_params['mount_point'], mirror_params['src'], {}, new)
                except Exception, e:
                    self.logger.error(e)

        if len(self.config.package_api_put) > 0:
            for mirror_params in self.config.package_api_put:
                try:
                    self._getPackages(mirror_params['mount_point'], mirror_params['src'], {}, new)
                except Exception, e:
                    self.logger.error(e)

    def moveCorrectPackages(self):
        if self.working:
            self.logger.debug("Common : already working")
            return
        self.working = True
        self.logger.debug("Common : getting valid temporary packages")
        if len(self.config.package_api_put) > 0:
            for mirror_params in self.config.package_api_put:
                if os.path.exists(mirror_params['tmp_input_dir']):
                    self._moveNewPackage(mirror_params)
        self.working = False

    def detectNewPackages(self):
        if self.working:
            self.logger.debug("Common : already working")
            return
        self.working = True
        self.working_pkgs = []
        self.logger.debug("Common : detecting new packages...")
        self._detectPackages(True)
        self._buildReverse()
        self._buildFileList()
        self.working = False

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
                self.mp2p[desc['mp']].append(pid)
        return True

    def desassociatePackage2mp(self, pid, mp):
        conf = self.h_desc(mp)
        for desc in self.descBySrc(conf['src']):
            if desc['type'] != 'mirror_files':
                self.mp2p[desc['mp']].remove(pid)
        return True

    def addPackage(self, pid, pa, need_assign = True):
        # return pid for success
        # raise ARYDEFPKG for already existing package
        try:
            if self.packages.has_key(pid):
                if self.packages[pid] == pa:
                    return pid
                raise Exception("ARYDEFPKG")
            if need_assign:
                Common().dontgivepkgs[pid] = []
                Common().dontgivepkgs[pid].extend(self.config.package_mirror_target)
            self.packages[pid] = pa
            if not self.reverse.has_key(pa.label):
                self.reverse[pa.label] = {}
            self.reverse[pa.label][pa.version] = pid
        except Exception, e:
            self.logger.error(e)
            raise e
        return pid

    def editPackage(self, pid, pack, need_assign = True):
        try:
            if self.packages.has_key(pid):
                old = self.packages[pid]
                self.reverse[old.label][old.version] = None # TODO : can't remove, so we will have to check that value != None...
                pack.setFiles(old.files)
            if need_assign:
                Common().dontgivepkgs[pid] = []
                Common().dontgivepkgs[pid].extend(self.config.package_mirror_target)
            self.packages[pid] = pack
            if not self.reverse.has_key(pack.label):
                self.reverse[pack.label] = {}
            self.reverse[pack.label][pack.version] = pid
        except Exception, e:
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
        self.packages[pid].setRoot(path)
        confxml = os.path.join(confdir, "conf.xml")
        if os.path.exists(confxml):
            shutil.move(confxml, confxml + ".bkp")
        if not os.path.exists(confdir):
            os.mkdir(confdir)
        f = open(confxml, 'w+')
        f.write(xml)
        f.close()
        return [pid, confdir]

    def associateFiles(self, mp, pid, files, level = 0):
        if not self.packages.has_key(pid):
            return [False, "This package don't exists"]
        params = self.h_desc(mp)
        path = self._getPackageRoot(pid)
        files_out = []
        for f in files:
            if level == 0:
                fo = os.path.join(path, pid, os.path.basename(f))
                self.logger.debug("File association will move %s to %s" % (f, fo))
                files_out.append(fo)
                shutil.move(f, fo)
            elif level == 1:
                for f1 in os.listdir(f):
                    f1 = os.path.join(f, f1)
                    fo = os.path.join(path, pid, os.path.basename(f1))
                    self.logger.debug("File association will move %s to %s" % (f1, fo))
                    files_out.append(fo)
                    shutil.move(f1, fo)
                shutil.rmtree(f)
           
        self._treatFiles(files_out, mp, pid, access = {})
        Common().dontgivepkgs[pid] = []
        Common().dontgivepkgs[pid].extend(self.config.package_mirror_target)
        return [True]

    def dropPackage(self, pid, mp):
        if not self.packages.has_key(pid):
            self.logger.error("package %s is not defined"%(pid))
            raise Exception("UNDEFPKG")
        params = self.h_desc(mp)
        path = params['src']

        if not os.path.exists(os.path.join(path, pid, 'conf.xml')):
            self.logger.error("package %s does not exists"%(pid))
            raise Exception("UNDEFPKG")

        if self.config.real_package_deletion:
            shutil.rmtree(os.path.join(path, pid))
        else:
            shutil.move(os.path.join(path, pid, 'conf.xml'), os.path.join(path, pid, 'conf.xml.rem'))
        # TODO remove package from mirrors
        return pid

    def writeFileIntoPackage(self, pid, file):
        pass

    def package(self, pid, mp = None):
        if mp == None:
            if not self.dontgivepkgs.has_key(pid) and self.packages[pid].hasFile():
                return self.packages[pid]
            return None
        try:
            if not self.dontgivepkgs.has_key(pid) and self.packages[pid].hasFile():
                self.mp2p[mp].index(pid)
                return self.packages[pid]
            return None
        except:
            pass
        return None

    def getPackages(self, mp): #TODO check the clone memory impact
        ret = {}
        try:
            for k in self.packages:
                if not self.dontgivepkgs.has_key(k) and self.packages[k].hasFile():
                    try:
                        self.mp2p[mp].index(k)
                        ret[k] = self.packages[k]
                    except:
                        pass
        except Exception, e:
            self.logger.error(e)
        return ret

    def reverse(self, mp): #TODO check the clone memory impact
        ret = []
        try:
            for k in self.reverse:
                if self.mp2p.has_key(k):
                    ret.append(k)
        except Exception, e:
            self.logger.error(e)
            raise e
        return ret

    def getFile(self, fid):
        if self.files.has_key(fid):
            return self.files[fid]
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
            
    def _getPackages(self, mp, src, access = {}, new = False): 
        if not os.path.exists(src):
            raise Exception("Src does not exists for mount point '#{%s}' (%s)" %(mp, src))
    
        if new:
            Find().find(src, self._treatNewConfFile, (mp, access))
        else:
            self.mp2p[mp] = []
            Find().find(src, self._treatConfFile, (mp, access)) 

    def _treatNewConfFile(self, file, mp, access):
        if os.path.basename(file) == 'conf.xml':
            if not self.already_declared.has_key(file):
                pid = self._treatDir(os.path.dirname(file), mp, access, True)
                self.associatePackage2mp(pid, mp)
                self.already_declared[file] = True
                
    def _treatConfFile(self, file, mp, access):
        if os.path.basename(file) == 'conf.xml':
            self._treatDir(os.path.dirname(file), mp, access)
            self.already_declared[file] = True

    def _treatFiles(self, files, mp, pid, access):
        conf = self.h_desc(mp)
        toRelative = self.packages[pid].root
        for f in files:
            path = '/'+re.sub(re.escape("%s%s%s%s" % (toRelative, os.sep, pid, os.sep)), '', os.path.dirname(f))
            size = int(self._treatFile(pid, f, path, access))
            self.packages[pid].size = int(self.packages[pid].size) + size
        
    def _treatDir(self, file, mp, access, new = False):
        pid = None
        try:
            if os.path.isdir(file):
                self.logger.debug("loading package metadata (xml) in %s"%(file))
                confxml = os.path.join(file, "conf.xml")
                l_package = self.parser.parse(confxml)
                l_package.setRoot(os.path.dirname(file))
                if l_package == None:
                    return False
                    
                pid = l_package.id
                self.working_pkgs.append(l_package)

                self.mp2p[mp].append(pid)
                if self.packages.has_key(pid):
                    return False

                toRelative = os.path.dirname(file)
                size = 0
                self.packages[pid] = l_package #self.parser.parse(confxml)
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
                self.logger.error(err)
                #"package %s won't be loaded because one of the declared file is missing"% (pid))
                self.mp2p[mp][pid] = None
            elif hasattr(err, 'message') and err.message == 'DBLFILE':
                self.logger.error(err)
                # :"package %s won't be loaded because one of its file is already declared in an other package"%(pid))
                self.mp2p[mp][pid] = None
            elif hasattr(err, 'message'):
                self.logger.error(err.message)
                self.mp2p[mp][pid] = None
            else:
                self.logger.error(err)
                if pid != None:
                    self.mp2p[mp][pid] = None
            raise err
        return pid

    def _treatFile(self, pid, f, path, access = {}, fid = None): #file_access_proto, file_access_uri, file_access_port, file_access_path, fid = None):
        (fsize, fmd5) = [0,0]
        if not self.file_properties.has_key(f):
            fsize = os.path.getsize(f)
            fmd5 = md5file(f)
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
            if os.path.isdir(pfile):
                files.extend(self._getFiles(pfile))
            else:
                if os.path.basename(pfile) != 'conf.xml':
                    files.append("%s%s%s" % (path , os.sep, pfile))
        return files

    def _buildReverse(self):
        for package in self.working_pkgs:
            if not self.reverse.has_key(package.label):
                self.reverse[package.label] = {}
            self.reverse[package.label][package.version] = package.id

    def _buildFileList(self):
        for package in self.working_pkgs:
            for file in package.files.internals: # TODO dont access to internals ! 
                self.files[file.id] = file.toURI()

