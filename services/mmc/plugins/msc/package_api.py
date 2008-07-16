import re
import dircache
import os
import logging
import time

import xmlrpclib
from twisted.web.xmlrpc import Proxy
from twisted.python import failure
from twisted.internet import defer

from mmc.plugins.msc import MscConfig
from mmc.support.mmctools import Singleton
from mmc.plugins.msc.database import MscDatabase
from mmc.plugins.msc.mirror_api import MirrorApi

from mmc.client import XmlrpcSslProxy, makeSSLContext

from mmc.plugins.pulse2.group import ComputerGroupManager


class PackageA:
    def __init__(self, server, port = None, mountpoint = None, proto = 'http', login = ''):
        self.logger = logging.getLogger()
        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            proto = server['protocol']
            bind = server['server']
            if server.has_key('username') and server.has_key('password') and server['username'] != '':
                login = "%s:%s@" % (server['username'], server['password'])
            
        self.server_addr = '%s://%s%s:%s%s' % (proto, login, bind, str(port), mountpoint)
        self.logger.debug('PackageA will connect to %s' % (self.server_addr))

        self.paserver = XmlrpcSslProxy(self.server_addr)
        self.config = MscConfig("msc")
        if self.config.ma_verifypeer:
            self.sslctx = makeSSLContext(self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert, False)
            self.paserver.setSSLClientContext(self.sslctx)
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args, value = []):
        self.logger.warn("PackageA:%s %s has failed: %s" % (funcname, args, error))
        return value

    def getAllPackages(self, mirror = None):
        if self.initialized_failed:
            return []
        d = self.paserver.callRemote("getAllPackages", mirror)
        d.addErrback(self.onError, "getAllPackages", mirror)
        return d

    def getPackageDetail(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageDetail", pid)
        d.addErrback(self.onError, "getPackageDetail", pid, False)
        return d

    def getPackageLabel(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageLabel", pid)
        d.addErrback(self.onError, "getPackageLabel", pid, False)
        return d

    def getPackageVersion(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageVersion", pid)
        d.addErrback(self.onError, "getPackageVersion", pid, False)
        return d


    def getPackageSize(self, pid):
        if self.initialized_failed:
            return 0
        d = self.paserver.callRemote("getPackageSize", pid)
        d.addErrback(self.onError, "getPackageSize", pid, 0)
        return d

    def getPackageInstallInit(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageInstallInit", pid)
        d.addErrback(self.onError, "getPackageInstallInit", pid, False)
        return d

    def getPackagePreCommand(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackagePreCommand", pid)
        d.addErrback(self.onError, "getPackagePreCommand", pid, False)
        return d

    def getPackageCommand(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageCommand", pid)
        d.addErrback(self.onError, "getPackageCommand", pid, False)
        return d

    def getPackagePostCommandSuccess(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackagePostCommandSuccess", pid)
        d.addErrback(self.onError, "getPackagePostCommandSuccess", pid, False)
        return d

    def getPackagePostCommandFailure(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackagePostCommandFailure", pid)
        d.addErrback(self.onError, "getPackagePostCommandFailure", pid, False)
        return d

    def getPackageFiles(self, pid):
        if self.initialized_failed:
            return []
        d = self.paserver.callRemote("getPackageFiles", pid)
        d.addErrback(self.onError, "getPackageFiles", pid)
        return d

    def getFileChecksum(self, file):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getFileChecksum", file)
        d.addErrback(self.onError, "getFileChecksum", file, False)
        return d

    def getPackagesIds(self, label):
        if self.initialized_failed:
            return []
        d = self.paserver.callRemote("getPackagesIds", label)
        d.addErrback(self.onError, "getPackagesIds", label)
        return d

    def getPackageId(self, label, version):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageId", label, version)
        d.addErrback(self.onError, "getPackageId", (label, version), False)
        return d

    def isAvailable(self, pid, mirror):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("isAvailable", pid, mirror)
        d.addErrback(self.onError, "getPackageId", (pid, mirror), False)
        return d

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


def _p_apiuniq(list, x):
  try:
    list.index(x)
  except:
    list.append(x)

def _merge_list(list, x):
    for i in x:
      try:
        list.index(i)
      except:
        pass
    rem = []
    for i in list:
      try:
        x.index(i)
      except:
        rem.append(i)
    for i in rem:
      list.remove(i)


class GetPackagesFiltered:

    def __init__(self, ctx, filt):
        self.ctx = ctx
        self.filt = filt
        self.packages = []

    def get(self):
        if "packageapi" in self.filt:
            ret = PackageA(self.filt["packageapi"]).getAllPackages(False)
            ret.addCallbacks(self.sendResult, self.onError)
        else:
            ret = self.sendResult()

    def sendResult(self, packages = []):
        logging.getLogger().debug(packages)
        ret = map(lambda m: [m, 0, self.filt['packageapi']], packages)
        self.deferred.callback(ret)

    def onError(self, error):
        logging.getLogger().error("Can't connect to package api: %s", str(error))
        self.deferred.callback([])

class GetPackagesUuidFiltered:

    def __init__(self, ctx, filt):
        self.ctx = ctx
        self.filt = filt

    def onError(error):
        logging.getLogger().error("Can't connect: %s", str(error))        
        return self.deferred.callback([])

    def sendResult(self, packages = []):
        self.deferred.callback(packages)

    def get(self):
        try:
            self.machine = self.filt["uuid"]
            d = MirrorApi().getApiPackage(self.machine)
            d.addCallbacks(self.uuidFilter2, self.onError)
        except KeyError:
            self.sendResult()

    def uuidFilter2(self, package_apis):
        self.package_apis = package_apis
        d = MirrorApi().getMirror(self.machine)
        d.addCallbacks(self.uuidFilter3, self.onError)

    def uuidFilter3(self, mirror):
        self.mirror = mirror
        self.index = -1
        self.packages = []
        self.getPackagesLoop()

    def getPackagesLoop(self, result = None):
        if result and not isinstance(result, failure.Failure):
            self.index = self.index + 1
            self.packages.extend(map(lambda m: [m, self.index, self.p_api], result))
        if self.package_apis:
            self.p_api = self.package_apis.pop()
            d = PackageA(self.p_api).getAllPackages(self.mirror)
            d.addCallbacks(self.getPackagesLoop)
        else:
            self.sendResult(self.packages)

class GetPackagesGroupFiltered:

    def __init__(self, ctx, filt):
        self.ctx = ctx
        self.filt = filt
        self.gid = None

    def onError(error):
        logging.getLogger().error("Can't connect: %s", str(error))        
        return self.deferred.callback([])

    def sendResult(self, packages = []):
        self.deferred.callback(packages)

    def get(self):
        try:
            self.gid = self.filt["group"]
        except KeyError:
            self.sendResult()
        if self.gid:
            self.machines = []
            if ComputerGroupManager().isdyn_group(self.ctx, self.gid):
                if ComputerGroupManager().isrequest_group(self.ctx, self.gid):
                    self.machines = map(lambda m: m['uuid'], ComputerGroupManager().requestresult_group(self.ctx, self.gid, 0, -1, ''))
                else:
                    self.machines = map(lambda m: m.uuid, ComputerGroupManager().result_group(self.ctx, self.gid, 0, -1, ''))
            else:
                self.machines = map(lambda m: m.uuid, ComputerGroupManager().result_group(self.ctx, self.gid, 0, -1, ''))
            d = MirrorApi().getApiPackages(self.machines)
            d.addCallbacks(self.getMirrors, self.onError)

    def getMirrors(self, package_apis):
        self.package_apis = package_apis
        d = MirrorApi().getMirrors(self.machines)
        d.addCallbacks(self.getMirrorsResult, self.onError)

    def getMirrorsResult(self, mirrors):
        self.mirrors = mirrors
        mergedlist = []
        for i in range(len(self.package_apis)):
            tmpmerged = []
            for papi in self.package_apis[i]:
                tmpmerged.append((papi, self.mirrors[i]))
            mergedlist.insert(i, tmpmerged)

        if not len(mergedlist):
            self.sendResult()
        else:
            plists = []
            for i in range(len(mergedlist[0])): # all line must have the same size!
                plists.insert(i, [])
                map(lambda x: _p_apiuniq(plists[i], x[i]), mergedlist)
            self.plists = plists
            self.index = -1
            self.p_apis = None
            self.packages = []
            self.tmppackages = []
            self.getPackagesLoop()

    def getPackagesLoop(self, result = None):
        if result:
            if not isinstance(result, failure.Failure):
                self.tmppackages.append(result)
            else:
                logging.getLogger().error("Error: %s", str(result))
        if not self.p_apis and self.tmppackages:
            # Merge temporary results
            lp = self.tmppackages[0]
            map(lambda p: _merge_list(lp, p), self.tmppackages)
            self.packages.extend(map(lambda m: [m, self.index, self.p_api_first], lp))
            self.tmppackages = []
        if self.plists and not self.p_apis:
            # Fill self.p_apis if empty
            self.p_apis = self.plists.pop()
            self.p_api_first = self.p_apis[0][0]
            self.index = self.index + 1
        if self.p_apis:
            p_api = self.p_apis.pop()
            d = PackageA(p_api[0]).getAllPackages(p_api[1])
            d.addCallbacks(self.getPackagesLoop)
        else:
            # No more remote call to do, we are done
            self.sendResult(self.packages)

class GetPackagesAdvanced:

    def __init__(self, ctx, filt):
        self.ctx = ctx
        self.filt = filt
        self.packages = []

    def get(self):
        g1 = GetPackagesFiltered(self.ctx, self.filt)
        g1.deferred = defer.Deferred()
        g2 = GetPackagesUuidFiltered(self.ctx, self.filt)
        g2.deferred = defer.Deferred()
        g3 = GetPackagesGroupFiltered(self.ctx, self.filt)
        g3.deferred = defer.Deferred()
        dl = defer.DeferredList([g1.deferred, g2.deferred, g3.deferred])
        dl.addCallback(self.sendResult)
        g1.get()
        g2.get()
        g3.get()

    def sendResult(self, results):
        # Aggregate all results
        for result in results:
            status, packages = result
            if status == defer.SUCCESS:
                self.packages.extend(packages)
        # Apply filter if wanted
        try:
            if self.filt['filter']:
                self.packages = filter(lambda p: re.search(self.filt['filter'], p[0]['label']), self.packages)
        except KeyError:
            pass
        # Sort on the mirror order then on the label, and finally on the version number        
        self.packages.sort(lambda x, y: 10*cmp(x[1], y[1]) + 5*cmp(x[0]['label'], y[0]['label']) + cmp(x[0]['version'], y[0]['version']))
        self.deferred.callback(self.packages)
