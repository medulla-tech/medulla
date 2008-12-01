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
        bind = server
        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            proto = server['protocol']
            bind = server['server']
            if server.has_key('username') and server.has_key('password') and server['username'] != '':
                login = "%s:%s@" % (server['username'], server['password'])

        self.server_addr = '%s://%s%s:%s%s' % (proto, login, bind, str(port), mountpoint)
        self.logger.debug('PackageA will connect to %s' % (self.server_addr))

        self.config = MscConfig("msc")
        if self.config.ma_verifypeer:
            self.paserver = XmlrpcSslProxy(self.server_addr)
            self.sslctx = makeSSLContext(self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert, False)
            self.paserver.setSSLClientContext(self.sslctx)
        else:
            self.paserver = Proxy(self.server_addr)
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args, value = []):
        self.logger.warn("PackageA:%s %s has failed: %s" % (funcname, args, error))
        return error

    def getAllPackages(self, mirror = None):
        if self.initialized_failed:
            return []
        d = self.paserver.callRemote("getAllPackages", mirror)
        d.addErrback(self.onError, "getAllPackages", mirror)
        return d

    def getAllPendingPackages(self, mirror = None):
        try:
            d = self.paserver.callRemote("getAllPendingPackages", mirror)
            d.addErrback(self.onError, "getAllPendingPackages", mirror)
            return d
        except:
            return []

    def __convertDoReboot(self, pkg):
        try:
            do_reboot = pkg['reboot']
            if do_reboot == '' or do_reboot == '0' or do_reboot == 0 or do_reboot == u'0' or do_reboot == 'false' or do_reboot == u'false' or do_reboot == False or do_reboot == 'disable' or do_reboot == u'disable' or do_reboot == 'off' or do_reboot == u'off':
                pkg['do_reboot'] = 'disable'
            elif do_reboot == '1' or do_reboot == 1 or do_reboot == u'1' or do_reboot == 'true' or do_reboot == u'true' or do_reboot == True or do_reboot == 'enable' or do_reboot == u'enable' or do_reboot == 'on' or do_reboot == u'on':
                pkg['do_reboot'] = 'enable'
            else:
                self.logger.warning("Dont know option '%s' for do_reboot, will use 'disable'"%(do_reboot)) 
            del pkg['reboot']
        except KeyError:
            pkg['do_reboot'] = 'disable'
        return pkg
        
    def getPackageDetail(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageDetail", pid)
        d.addCallback(self.__convertDoReboot)
        d.addErrback(self.onError, "getPackageDetail", pid, False)
        return d

    def getPackageLabel(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageLabel", pid)
        d.addErrback(self.onError, "getPackageLabel", pid, False)
        return d

    def _erGetLocalPackagePath(self):
        return self.config.repopath

    def getLocalPackagePath(self, pid):
        if self.initialized_failed:
            return self.config.repopath
        d = self.paserver.callRemote("getLocalPackagePath", pid)
        d.addErrback(self._erGetLocalPackagePath)
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

    def getPackageHasToReboot(self, pid):
        if self.initialized_failed:
            return False
        d = self.paserver.callRemote("getPackageHasToReboot", pid)
        d.addErrback(self.onError, "getPackageHasToReboot", pid, False)
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

class SendBundleCommand:
    def __init__(self, ctx, porders, targets, params, mode, gid = None, proxies = []):
        self.ctx = ctx
        self.porders = porders
        self.targets = targets
        self.params = params
        self.mode = mode
        self.gid = gid
        self.bundle_id = None
        self.proxies = proxies
        
    def onError(self, error):
        logging.getLogger().error("SendBundleCommand: %s", str(error))
        return self.deferred.callback([])

    def sendResult(self, result):
        return self.deferred.callback([self.bundle_id, result])

    def send(self):
        # treat bundle title
        try:
            title = self.params['bundle_title']
        except:
            title = '' # ie. "no title"
        self.params['bundle_title'] = None

        if title == None or title == '':
            localtime = time.localtime()
            title = "Bundle (%s) - %04d/%02d/%02d %02d:%02d:%02d" % (
                str(len(self.porders)),
                localtime[0],
                localtime[1],
                localtime[2],
                localtime[3],
                localtime[4],
                localtime[5]
            )

        last_order = 0
        for id in self.porders:
            p_api, pid, order = self.porders[id]
            if order > last_order:
                last_order = order

        # treat bundle inventory and halt (put on the last command)
        do_inventory = self.params['do_inventory']
        try:
            issue_halt_to = self.params['issue_halt_to']
        except: # just in case issue_halt_to has not been set
            issue_halt_to = ''

        bundle = MscDatabase().createBundle(title)
        self.bundle_id = bundle.id

        ret = []
        for id in self.porders:
            p_api, pid, order = self.porders[id]
            if order == last_order:
                self.params['do_inventory'] = do_inventory
                self.params['issue_halt_to'] = issue_halt_to
            else:
                self.params['do_inventory'] = 'off'
                self.params['issue_halt_to'] = ''
            g = SendPackageCommand(self.ctx, p_api, pid, self.targets, self.params, self.mode, self.gid, self.bundle_id, order, self.proxies)
            g.deferred = defer.Deferred()
            g.send()
            ret.append(g.deferred)

        if len(ret) == 0:
            self.onError("No order to send")
        else:
            dl = defer.DeferredList(ret)
            dl.addCallback(self.sendResult)
            return dl
        return False

class SendPackageCommand:
    def __init__(self, ctx, p_api, pid, targets, params, mode, gid = None, bundle_id = None, order_in_bundle = None, proxies = []):
        self.ctx = ctx
        self.p_api = p_api.copy()
        self.pid = pid
        self.targets = targets
        self.params = params.copy()
        self.mode = mode
        self.gid = gid
        self.bundle_id = bundle_id
        self.order_in_bundle = order_in_bundle
        self.proxies = proxies

    def onError(self, error):
        logging.getLogger().error("SendPackageCommand: %s", str(error))
        return self.deferred.errback(error)

    def sendResult(self, id_command = -1):
        return self.deferred.callback(id_command)

    def send(self):
        d = PackageA(self.p_api).getPackageDetail(self.pid)
        d.addCallbacks(self.setPackage, self.onError)

    def setPackage(self, package):
        self.cmd = package['command']
        self.a_files = package['files']
        self.label = package['label']
        self.version = package['version']
        self.do_reboot = package['do_reboot']
        d = PackageA(self.p_api).getLocalPackagePath(self.pid)
        d.addCallbacks(self.setRoot, self.onError)

    def setRoot(self, root):
        self.root = root
        start_file = self.cmd['command']
        #TODO : check that params has needed values, else put default one
        # as long as this method is called from the MSC php, the fields should be
        # set, but, if someone wants to call it from somewhere else...
        start_script = (self.params['start_script'] == 'on' and 'enable' or 'disable')
        clean_on_success = (self.params['clean_on_success'] == 'on' and 'enable' or 'disable')
        do_wol = (self.params['do_wol'] == 'on' and 'enable' or 'disable')
        next_connection_delay = self.params['next_connection_delay']
        max_connection_attempt = self.params['max_connection_attempt']
        do_inventory = (self.params['do_inventory'] == 'on' and 'enable' or 'disable')
        issue_halt_to = self.params['issue_halt_to']
        maxbw = self.params['maxbw']

        try:
            deployment_intervals = self.params['deployment_intervals']
        except KeyError:
            deployment_intervals = ''

        try:
            parameters = self.params['parameters']
        except KeyError:
            parameters = ''

        try:
            start_date = convert_date(self.params['start_date'])
        except:
            start_date = '0000-00-00 00:00:00' # ie. "now"

        try:
            end_date = convert_date(self.params['end_date'])
        except:
            end_date = '0000-00-00 00:00:00' # ie. "no end date"

        try:
            title = self.params['title']
        except:
            title = '' # ie. "no title"

        if title == None or title == '':
            localtime = time.localtime()
            title = "%s (%s) - %04d/%02d/%02d %02d:%02d:%02d" % (
                self.label,
                self.version,
                localtime[0],
                localtime[1],
                localtime[2],
                localtime[3],
                localtime[4],
                localtime[5]
            )

        files = map(lambda hm: hm['id']+'##'+hm['path']+'/'+hm['name'], self.a_files)

        MscDatabase().addCommand(  # TODO: refactor to get less args
            self.ctx,
            self.pid,
            start_file,
            parameters,
            files,
            self.targets, # TODO : need to convert array into something that we can get back ...
            self.mode,
            self.gid,
            start_script,
            clean_on_success,
            start_date,
            end_date,
            "root", # TODO: may use another login name
            title,
            issue_halt_to,
            self.do_reboot,
            do_wol,
            next_connection_delay,
            max_connection_attempt,
            do_inventory,
            maxbw,
            self.root,
            deployment_intervals,
            self.bundle_id,
            self.order_in_bundle,
            self.proxies
        ).addCallbacks(self.sendResult, self.onError)

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
            if 'pending' in self.filt:
                ret = PackageA(self.filt["packageapi"]).getAllPendingPackages(False)
            else:
                ret = PackageA(self.filt["packageapi"]).getAllPackages(False)
            ret.addCallbacks(self.sendResult, self.onError)
            ret.addErrback(lambda err: self.onError(err))
        else:
            ret = self.sendResult()

    def sendResult(self, packages = []):
        ret = map(lambda m: [m, 0, self.filt['packageapi']], packages)
        self.deferred.callback(ret)

    def onError(self, error):
        logging.getLogger().error("GetPackagesFiltered: %s", str(error))
        self.deferred.callback([])

class GetPackagesUuidFiltered:

    def __init__(self, ctx, filt):
        self.ctx = ctx
        self.filt = filt

    def onError(self, error):
        logging.getLogger().error("GetPackagesUuidFiltered: %s", str(error))
        return self.deferred.callback([])

    def sendResult(self, packages = []):
        self.deferred.callback(packages)

    def get(self):
        try:
            self.machine = self.filt["uuid"]
            d = MirrorApi().getApiPackage(self.machine)
            d.addCallbacks(self.uuidFilter2, self.onError)
            d.addErrback(lambda err: self.onError(err))
        except KeyError:
            self.sendResult()

    def uuidFilter2(self, package_apis):
        self.package_apis = package_apis
        d = MirrorApi().getMirror(self.machine)
        d.addCallbacks(self.uuidFilter3, self.onError)
        d.addErrback(lambda err: self.onError(err))

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
            if 'pending' in self.filt:
                d = PackageA(self.p_api).getAllPendingPackages(self.mirror)
            else:
                d = PackageA(self.p_api).getAllPackages(self.mirror)
            d.addCallbacks(self.getPackagesLoop)
        else:
            self.sendResult(self.packages)

class GetPackagesGroupFiltered:

    def __init__(self, ctx, filt):
        self.ctx = ctx
        self.filt = filt
        self.gid = None

    def onError(self, error):
        logging.getLogger().error("GetPackagesGroupFiltered: %s", str(error))
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
                    self.machines = ComputerGroupManager().requestresult_group(self.ctx, self.gid, 0, -1, '')
                else:
                    self.machines = ComputerGroupManager().result_group(self.ctx, self.gid, 0, -1, '')
            else:
                self.machines = ComputerGroupManager().result_group(self.ctx, self.gid, 0, -1, '')
            d = MirrorApi().getApiPackages(self.machines)
            d.addCallbacks(self.getMirrors, self.onError)
            d.addErrback(lambda err: self.onError(err))

    def getMirrors(self, package_apis):
        self.package_apis = package_apis
        d = MirrorApi().getMirrors(self.machines)
        d.addCallbacks(self.getMirrorsResult, self.onError)
        d.addErrback(lambda err: self.onError(err))

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
            n = len(mergedlist[0])
            i = 0
            for i in range(len(mergedlist[0])): # all line must have the same size!
                plists.insert(i, [])
                try:
                    map(lambda x: _p_apiuniq(plists[i], x[i]), mergedlist)
                except IndexError:
                    logging.getLogger().error("Error with i=%d" %i)
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
            if 'pending' in self.filt:
                d = PackageA(p_api[0]).getAllPendingPackages(p_api[1])
            else:
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
                self.packages = filter(lambda p: re.search(self.filt['filter'], p[0]['label'], re.I), self.packages)
        except KeyError:
            pass
        # Sort on the mirror order then on the label, and finally on the version number
        self.packages.sort(lambda x, y: 10*cmp(x[1], y[1]) + 5*cmp(x[0]['label'], y[0]['label']) + cmp(x[0]['version'], y[0]['version']))
        self.deferred.callback(self.packages)
