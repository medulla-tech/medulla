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
        self.server = xmlrpclib.Server(self.server_addr)
        self.xmlrpc = self.server.xmlrpc

    def getAllPackages(self, mirror = None):
        pa = self.xmlrpc.getAllPackages(mirror)
        return self.xmlrpc.getAllPackages(mirror)

    def getPackageDetail(self, pid):
        return self.xmlrpc.getPackageDetail(pid)

    def getPackageLabel(self, pid):
        return self.xmlrpc.getPackageLabel(pid)

    def getPackageVersion(self, pid):
        return self.xmlrpc.getPackageVersion(pid)

    def getPackageSize(self, pid):
        size = 0
        try:
            size = self.xmlrpc.getPackageSize(pid)
        except:
            pass
        return size

    def getPackageInstallInit(self, pid):
        return self.xmlrpc.getPackageInstallInit(pid)

    def getPackagePreCommand(self, pid):
        return self.xmlrpc.getPackagePreCommand(pid)

    def getPackageCommand(self, pid):
        return self.xmlrpc.getPackageCommand(pid)

    def getPackagePostCommandSuccess(self, pid):
        return self.xmlrpc.getPackagePostCommandSuccess(pid)

    def getPackagePostCommandFailure(self, pid):
        return self.xmlrpc.getPackagePostCommandFailure(pid)

    def getPackageFiles(self, pid):
        return self.xmlrpc.getPackageFiles(pid)

    def getFileChecksum(self, file):
        return self.xmlrpc.getFileChecksum(file)

    def getPackagesIds(self, label):
        return self.xmlrpc.getPackagesIds(label)

    def getPackageId(self, label, version):
        return self.xmlrpc.getPackageId(label, version)

    def isAvailable(self, pid, mirror):
        return self.xmlrpc.isAvailable(pid, mirror)



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
        start_inventory
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

