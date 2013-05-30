#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva
#
# $Id$
#
# This file is part of MMC.
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import os
from ConfigParser import ConfigParser
from base64 import b64encode, b64decode

from mmc.site import mmcconfdir
from mmc.support.mmctools import RpcProxyI, ContextMakerI, SecurityContext

from mmc.plugins.msc.package_api import PackageGetA
from mmc.plugins.pkgs.package_put_api import PackagePutA
from mmc.plugins.pkgs.user_packageapi_api import UserPackageApiApi
from mmc.plugins.pkgs.config import PkgsConfig

from pulse2.version import getVersion, getRevision # pyflakes.ignore

APIVERSION = "0:0:0"

def getApiVersion(): return APIVERSION

def activate():
    logger = logging.getLogger()
    logger.debug("Pkgs is activating")
    config = PkgsConfig("pkgs")
    if config.disabled:
        logger.warning("Plugin pkgs: disabled by configuration.")
        return False
    return True

class ContextMaker(ContextMakerI):
    def getContext(self):
        s = SecurityContext()
        s.userid = self.userid
        return s

class ConfigReader(object):
    """Read and parse config files"""
    def __init__(self):
        agent_ini = os.path.join(mmcconfdir, 
                                "agent", 
                                "config.ini")
        self._agent_config = self.get_config(agent_ini)


    @classmethod
    def get_config(cls, inifile):
        """
        Get the configuration from config file

        @param inifile: path to config file
        @type inifile: string

        @return: ConfigParser.ConfigParser instance 
        """
        logging.getLogger().debug("Load config file %s" % inifile)
        if not os.path.exists(inifile) :
            logging.getLogger().error("Error while reading the config file: Not found.")
            return False

        config = ConfigParser()
        config.readfp(open(inifile))

        return config

    @property
    def agent_config(self):
        """ 
        Get the configuration of package server 

        @return: ConfigParser.ConfigParser instance 
        """
        return self._agent_config

class RpcProxy(RpcProxyI):
    def getPApiDetail(self, pp_api_id):
        def _getPApiDetail(result, pp_api_id = pp_api_id):
            for upa in result: 
                if upa['uuid'] == pp_api_id:
                    return upa
            return False
        
        d = self.upaa_getUserPackageApi()
        d.addCallback(_getPApiDetail)
        return d

    # PackagePutA
    def ppa_getPackageDetail(self, pp_api_id, pid):
        def _ppa_getPackageDetail(result, pp_api_id = pp_api_id, pid = pid):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return PackageGetA(upa).getPackageDetail(pid)
            return False
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_getPackageDetail)
        return d

    def ppa_pushPackage(self, pp_api_id, random_dir, files, local_mmc):
        def _ppa_pushPackage(result, pp_api_id = pp_api_id, random_dir = random_dir, files = files, local_mmc = local_mmc):
            def _encodeFiles(random_dir, files):
                encoded_files = []
                for file in files:
                    logging.getLogger().debug("Encoding file %s" % file['filename'])
                    tmp_dir = file['tmp_dir']
                    f = open(os.path.join(tmp_dir, random_dir, file['filename']), 'r')
                    encoded_files.append({
                        'filename': file['filename'],
                        'filebinary': b64encode(f.read()),
                    })
                    f.close()
                return encoded_files

            def _decodeFiles(random_dir, files):
                pkgs_tmp_dir = self.getPServerTmpDir()
                if not os.path.exists(os.path.join(pkgs_tmp_dir, random_dir)):
                    os.makedirs(os.path.join(pkgs_tmp_dir, random_dir))
                filepath = os.path.join(pkgs_tmp_dir, random_dir)
                for file in files:
                    logging.getLogger().debug("Decoding file %s" % file['filename'])
                    f = open(os.path.join(filepath, file['filename']), 'w')
                    f.write(b64decode(file['filebinary']))
                    f.close()
                    file['filebinary'] = False
                    file['tmp_dir'] = pkgs_tmp_dir
                return files

            for upa in result:
                if upa['uuid'] == pp_api_id:
                    local_pserver = self.getPServerIP() in ['localhost', '127.0.0.1'] and True or False
                    if local_mmc:
                        logging.getLogger().info("Push package from local mmc-agent...")
                        if local_pserver:
                            logging.getLogger().info("... to local package server")
                            return PackagePutA(upa).pushPackage(random_dir, files, local_pserver)
                        else:
                            logging.getLogger().info("... to external package server")
                            # Encode files (base64) and send them with XMLRPC
                            encoded_files = _encodeFiles(random_dir, files)
                            return PackagePutA(upa).pushPackage(random_dir, encoded_files, local_pserver)
                    else:
                        logging.getLogger().info("Push package from external mmc-agent...")
                        if local_pserver:
                            logging.getLogger().info("... to local package server")
                            # decode files
                            decoded_files = _decodeFiles(random_dir, files)
                            return PackagePutA(upa).pushPackage(random_dir, decoded_files, local_pserver)
                        else:
                            logging.getLogger().info("... to external package server")
                            return PackagePutA(upa).pushPackage(random_dir, files, local_pserver)
            logging.getLogger().warn("Failed to push package on %s"%(pp_api_id))
            return False
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_pushPackage)
        return d

    def ppa_putPackageDetail(self, pp_api_id, package, need_assign = True):
        def _ppa_putPackageDetail(result, pp_api_id = pp_api_id, package = package, need_assign = need_assign):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return PackagePutA(upa).putPackageDetail(package, need_assign)
            logging.getLogger().warn("Failed to put package details on %s"%(pp_api_id))
            return False
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_putPackageDetail)
        return d

    def ppa_dropPackage(self, pp_api_id, pid):
        def _ppa_dropPackage(result, pp_api_id = pp_api_id, pid = pid):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return PackagePutA(upa).dropPackage(pid)
            return False
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_dropPackage)
        return d

    def ppa_getTemporaryFiles(self, pp_api_id):
        def _ppa_getTemporaryFiles(result, pp_api_id = pp_api_id):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return PackagePutA(upa).getTemporaryFiles()
            return []
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_getTemporaryFiles)
        return d

    def ppa_getTemporaryFileSuggestedCommand(self, pp_api_id, tempdir):
        def _ppa_getTemporaryFilesSuggestedCommand(result, pp_api_id = pp_api_id, tempdir = tempdir):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return PackagePutA(upa).getTemporaryFilesSuggestedCommand(tempdir)
            return []
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_getTemporaryFilesSuggestedCommand)
        return d

    def ppa_associatePackages(self, pp_api_id, pid, files, level = 0):
        def _ppa_associatePackages(result, pp_api_id = pp_api_id, pid = pid, files = files, level = level):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return PackagePutA(upa).associatePackages(pid, files, level)
            return []
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_associatePackages)
        return d

    def ppa_getRsyncStatus(self, pp_api_id, pid):
        def _ppa_getRsyncStatus(result, pp_api_id = pp_api_id, pid = pid):
            for upa in result:
                if upa['uuid'] == pp_api_id:
                    return PackagePutA(upa).getRsyncStatus(pid)
            return []
        d = self.upaa_getUserPackageApi()
        d.addCallback(_ppa_getRsyncStatus)
        return d
    
    # UserPackageApiApi
    def upaa_getUserPackageApi(self):
        ctx = self.currentContext
        return UserPackageApiApi().getUserPackageApi(ctx.userid)

    def getMMCIP(self):
        config = ConfigReader()

        self.agent_config = config.agent_config

        return self.agent_config.get("main", "host")

    def getPServerIP(self):
        config = PkgsConfig("pkgs")
        return config.upaa_server

    def getPServerTmpDir(self):
        config = PkgsConfig("pkgs")
        return config.tmp_dir
