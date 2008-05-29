import re
import dircache
import os
import logging
import time

import xmlrpclib

from mmc.plugins.msc import MscConfig
from mmc.support.mmctools import Singleton
from mmc.plugins.msc.database import MscDatabase
from mmc.plugins.msc.mirror_api import MirrorApi

class PackageA:
    def __init__(self, server, port = None, mountpoint = None):
        self.logger = logging.getLogger()

        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            server = server['server']

        self.server_addr = 'http://'+server+':'+str(port) + mountpoint
        self.logger.debug('PackageA will connect to %s' % (self.server_addr))
        try:
            self.server = xmlrpclib.Server(self.server_addr)
            self.xmlrpc = self.server.xmlrpc
            self.initialized_failed = False
        except:
            self.logger.warn('PackageA failed to connect to %s' % (self.server_addr))
            self.initialized_failed = True

    def getAllPackages(self, mirror = None):
        if self.initialized_failed:
            return []
        try:
            return self.xmlrpc.getAllPackages(mirror)
        except:
            self.logger.warn('PackageA:getAllPackages fails %s'%(str(mirror)))
            return []

    def getPackageDetail(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackageDetail(pid)
        except:
            self.logger.warn('PackageA:getPackageDetail fails %s'%(str(pid)))
            return False

    def getPackageLabel(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackageLabel(pid)
        except:
            self.logger.warn('PackageA:getPackageLabel fails %s'%(str(pid)))
            return False

    def getPackageVersion(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackageVersion(pid)
        except:
            self.logger.warn('PackageA:getPackageVersion fails %s'%(str(pid)))
            return False

    def getPackageSize(self, pid):
        if self.initialized_failed:
            return 0
        size = 0
        try:
            size = self.xmlrpc.getPackageSize(pid)
        except:
            pass
        return size

    def getPackageInstallInit(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackageInstallInit(pid)
        except:
            self.logger.warn('PackageA:getPackageInstallInit fails %s'%(str(pid)))
            return False

    def getPackagePreCommand(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackagePreCommand(pid)
        except:
            self.logger.warn('PackageA:getPackagePreCommand fails %s'%(str(pid)))
            return False

    def getPackageCommand(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackageCommand(pid)
        except:
            self.logger.warn('PackageA:getPackageCommand fails %s'%(str(pid)))
            return False

    def getPackagePostCommandSuccess(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackagePostCommandSuccess(pid)
        except:
            self.logger.warn('PackageA:getPackagePostCommandSuccess fails %s'%(str(pid)))
            return False

    def getPackagePostCommandFailure(self, pid):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackagePostCommandFailure(pid)
        except:
            self.logger.warn('PackageA:getPackagePostCommandFailure fails %s'%(str(pid)))
            return False

    def getPackageFiles(self, pid):
        if self.initialized_failed:
            return []
        try:
            return self.xmlrpc.getPackageFiles(pid)
        except:
            self.logger.warn('PackageA:getPackageFiles fails %s'%(str(pid)))
            return []

    def getFileChecksum(self, file):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getFileChecksum(file)
        except:
            self.logger.warn('PackageA:getFileChecksum fails %s'%(str(file)))
            return False

    def getPackagesIds(self, label):
        if self.initialized_failed:
            return []
        try:
            return self.xmlrpc.getPackagesIds(label)
        except:
            self.logger.warn('PackageA:getPackagesIds fails %s'%(str(label)))
            return []

    def getPackageId(self, label, version):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.getPackageId(label, version)
        except:
            self.logger.warn('PackageA:getPackageId fails %s'%(str(label), str(version)))
            return False

    def isAvailable(self, pid, mirror):
        if self.initialized_failed:
            return False
        try:
            return self.xmlrpc.isAvailable(pid, mirror)
        except:
            self.logger.warn('PackageA:isAvailable fails %s %s'%(str(pid), str(mirror)))
            return False



from mmc.plugins.msc.mirror_api import MirrorApi

def send_package_command(ctx, pid, targets, params, p_api, mode, gid = None):
    cmd = PackageA(p_api).getPackageCommand(pid)
    start_file = cmd['command']
    a_files = PackageA(p_api).getPackageFiles(pid)
    #TODO : check that params has needed values, else put default one
    # as long as this method is called from the MSC php, the fields should be
    # set, but, if someone wants to call it from somewhere else...
    start_script = (params['start_script'] == 'on' and 'enable' or 'disable')
    delete_file_after_execute_successful = (params['delete_file_after_execute_successful'] == 'on' and 'enable' or 'disable')
    wake_on_lan = (params['wake_on_lan'] == 'on' and 'enable' or 'disable')
    next_connection_delay = params['next_connection_delay']
    max_connection_attempt = params['max_connection_attempt']
    start_inventory = (params['start_inventory'] == 'on' and 'enable' or 'disable')
    maxbw = params['maxbw']

    try:
        parameters = params['parameters']
    except KeyError:
        parameters = ''

    try:
        start_date = convert_date(params['start_date'])
    except:
        start_date = '0000-00-00 00:00:00' # ie. "now"

    try:
        end_date = convert_date(params['end_date'])
    except:
        end_date = '0000-00-00 00:00:00' # ie. "no end date"

    try:
        title = params['title']
    except:
        title = '' # ie. "no title"

    if title == None or title == '':
        localtime = time.localtime()
        title = "%s (%s) - %04d/%02d/%02d %02d:%02d:%02d" % (
            PackageA(p_api).getPackageLabel(pid),
            PackageA(p_api).getPackageVersion(pid),
            localtime[0],
            localtime[1],
            localtime[2],
            localtime[3],
            localtime[4],
            localtime[5]
        )

    files = map(lambda hm: hm['id']+'##'+hm['path']+'/'+hm['name'], a_files)

    id_command = MscDatabase().addCommand(  # TODO: refactor to get less args
        start_file,
        parameters,
        files,
        targets, # TODO : need to convert array into something that we can get back ...
        mode,
        gid,
        start_script,
        delete_file_after_execute_successful,
        start_date,
        end_date,
        ctx.userid,
        ctx.userid,
        title,
        wake_on_lan,
        next_connection_delay,
        max_connection_attempt,
        start_inventory,
        0,
        maxbw
    )
    return id_command

def convert_date(date = '0000-00-00 00:00:00'):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(date, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(date, "%Y/%m/%d %H:%M:%S"))
        except ValueError:
            timestamp = '0000-00-00 00:00:00'
    return timestamp

