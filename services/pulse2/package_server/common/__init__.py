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
import shutils
import logging
from pulse2.package_server.parser import PackageParser

class Common(Singleton):
    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

        self.file_properties = {}
        self.packages = {}
        self.mp2p = {}
        self.reverse = {}
        self.files = {}
        self.fid2file = {}
        self.parser = PackageParser(config)
        proto = 'http'
        if self.config.enablessl:
            proto = 'https'

        try:
            if len(self.config.mirrors) > 0:
                for mirror_params in self.config.mirrors:
                    try:
                        _getPackages(
                            mirror_params['mount_point'],
                            mirror_params['src'],
                            proto,
                            mirror_params['file_access_uri'],
                            mirror_params['file_access_port'],
                            mirror_params['file_access_path']
                        )
                    except Exception, e:
                        self.logger.error(e)

            if len(self.config.package_api_get) > 0:
                for mirror_params in self.config.package_api_get:
                    try:
                        _getPackages(mirror_params['mount_point'], mirror_params['src'])
                    except Exception, e:
                        self.logger.error(e)

            if len(self.config.package_api_put) > 0:
                for mirror_params in self.config.package_api_put:
                    try:
                        _getPackages(mirror_params['mount_point'], mirror_params['src'])
                    except Exception, e:
                        self.logger.error(e)

            _buildReverse()
            _buildFileList()

            self.logger.info("Common : finish loading %d packages" % (len(self.packages)))
        except Exception, e:
            self.logger.error("Common : failed to finish loading packages"
            raise e
    
    def checkPath4package(self, path): # TODO check if still used
        # TODO get conf.xml files in path, parse them, and fill the hashes
        return False

    def associatePackage2mp(self, pid, mp):
        conf = self.h_desc(mp) # TODO move h_desc from server to common
        for desc in self.descBySrc(conf['src']): # TODO move descBySrc from server to common
            if desc['type'] != 'mirror_files'
                self.mp2p[desc['mp']].append(pid)

    def addPackage(self, pid, pa):
        # return pid for success
        # raise ARYDEFPKG for already existing package
        try:
            if self.packages.has_key(pid):
                if self.packages[pid] == pa:
                    return pid
                raise "ARYDEFPKG"
            self.packages[pid] = pa
            if not self.reverse.has_key(pa.label):
                self.reverse[pa.label] = {}
            self.reverse[pa.label][pa.version] = pid
        except Exception, e:
            self.logger.error(e)
            raise e
        return pid

    def editPackage(self, pid, pack):
        try:
            if self.packages.has_key(pid):
                old = self.packages[pid]
                self.reverse[old.label][old.version] = None # TODO : can't remove, so we will have to check that value != None...
            self.packages[pid] = ack
            if not self.reverse.has_key(pack.label):
                self.reverse[pack.label] = {}
            self.reverse[pack.label][pack.version] = pid
        except Exception, e:
            self.logger.error(e)
            raise e
        return pid

    def writePackageTo(self, pid, mp):
        if self.packages.has_key(pid):
            self.logger.error("package %s is not defined"%(pid))
            raise "UNDEFPKG"
        xml = self.parser.concat(self.packages[pid])
        params = self.h_desc(mp)
        path = params['src']

        if os.path.exists("%s/%s/conf.xml" % (path, pid)):
            shutil.move("%s/%s/conf.xml" % (path, pid), "%s/%s/conf.xml.bkp" % (path, pid)
        os.mkdir("%s/%s" % (path, pid))
        f = open("%s/%s/conf.xml" % (path, pid), 'w+')
        f.write(xml)
        f.close()
        return [pid, "%s/%s" % (path, pid)]

    def writeFileIntoPackage(self, pid, file):
        pass


    def package(self, pid):
        return self.packages[pid]

    def packages(self, mp): #TODO check the clone memory impact
        ret = []
        try:
            for k in self.packages:
                if self.mp2p.has_key(k):
                    ret.append(k)
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
        return ret



    def _getPackages(self, mp, src, file_access_proto = '', file_access_uri = '', file_access_port = '', file_access_path = ''):
        if not os.path.exists(src):
            raise "Src does not exists for mount point '#{%s}' (%s)" %(mp, src)
    
        self.mp2p[mp] = []

        Find.find2(src) do |file|
            if File.basename(file) == 'conf.xml'
                _treatDir(File.dirname(file), mp, file_access_proto, file_access_uri, file_access_port, file_access_path)
            end
        end


