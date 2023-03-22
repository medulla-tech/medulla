# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
This module define the package get API.
It provides methods to get informations on packages.
"""
import re
import logging
import time

from twisted.python import failure
from twisted.internet import defer

from sqlalchemy.orm import create_session

from mmc.plugins.msc import MscConfig
from mmc.plugins.msc.database import MscDatabase
#from mmc.plugins.msc.mirror_api import MirrorApi
#from mmc.plugins.msc.qaction import qa_list_files

from pulse2.managers.group import ComputerGroupManager
import pulse2.apis.clients.package_get_api

class PackageGetA(pulse2.apis.clients.package_get_api.PackageGetA):
    def __init__(self, server, port = None, mountpoint = None, proto = 'http', login = ''):
        self.logger = logging.getLogger()
        bind = server
        credentials = ''
        if type(server) == dict:
            mountpoint = server['mountpoint']
            port = server['port']
            proto = server['protocol']
            bind = server['server']
            #if 'username' in server and 'password' in server and server['username'] != '':
            if server.has_key('username') and server.has_key('password') and server['username'] != '':
                login = "%s:%s@" % (server['username'], server['password'])
                credentials = "%s:%s" % (server['username'], server['password'])

        self.server_addr = '%s://%s%s:%s%s' % (proto, login, bind, str(port), mountpoint)
        self.config = MscConfig()
        if self.config.ma_verifypeer:
            pulse2.apis.clients.package_get_api.PackageGetA.__init__(self, credentials, self.server_addr, self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert)
        else:
            pulse2.apis.clients.package_get_api.PackageGetA.__init__(self, credentials, self.server_addr)

#def get_default_bundle_name(bundle_elem_nb = 0):
    #localtime = time.localtime()
    #title = "Bundle (%d) - %04d/%02d/%02d %02d:%02d:%02d" % (
        #bundle_elem_nb,
        #localtime[0],
        #localtime[1],
        #localtime[2],
        #localtime[3],
        #localtime[4],
        #localtime[5]
    #)
    #return title

#class SendBundleCommand:
    #def __init__(self, ctx, porders, targets, params, mode, gid = None, proxies = []):
        #self.ctx = ctx
        #self.porders = porders
        #self.targets = targets
        #self.params = params
        #self.mode = mode
        #self.gid = gid
        #self.bundle_id = None
        #self.proxies = proxies
        #self.pids = []
        #self.session = None

    #def onError(self, error):
        #logging.getLogger().error("SendBundleCommand: %s", str(error))
        #if self.session:
            ## Rollback the transaction
            #self.session.rollback()
            #self.session.close()
        #return self.deferred.callback([])

    #def sendResult(self, result):
        #return self.deferred.callback([self.bundle_id, result])

    #def send(self):
        #self.last_order = 0
        #self.first_order = len(self.porders)
        #for id in self.porders:
            #p_api, pid, order = self.porders[id]
            #self.pids.append(pid)
            #if int(order) > int(self.last_order):
                #self.last_order = order
            #if int(order) < int(self.first_order):
                #self.first_order = order

        ## treat bundle inventory and halt (put on the last command)
        #self.do_wol = self.params['do_wol']
        #self.do_imaging_menu = 'disable'
        #self.do_inventory = self.params['do_inventory']
        #self.issue_halt_to = self.params["issue_halt_to"]

        ## Build the list of all the different package APIs to connect to
        #self.p_apis = []
        #for p in self.porders:
            #p_api, _, _ = self.porders[p]
            #if p_api not in self.p_apis:
                #self.p_apis.append(p_api)

        #self.packages = {}
        #self.ppaths = {}
        #self.packageApiLoop()

    #def packageApiLoop(self):
        #"""
        #Loop over all packages package API to get package informations
        #"""
        #if self.p_apis:
            #self.p_api = self.p_apis.pop()
            ## Get package ID linked to the selected package API
            #self.p_api_pids = []
            #for p in self.porders:
                #p_api, pid, _ = self.porders[p]
                #if p_api == self.p_api:
                    #self.p_api_pids.append(pid)

            #d = PackageGetA(self.p_api).getPackagesDetail(self.p_api_pids)
            #d.addCallbacks(self.setPackagesDetail, self.onError)
        #else:
            #self.createBundle()

    #def setPackagesDetail(self, packages):
        #for i in range(len(self.p_api_pids)):
            #self.packages[self.p_api_pids[i]] = packages[i]
        #d = PackageGetA(self.p_api).getLocalPackagesPath(self.p_api_pids)
        #d.addCallbacks(self.setLocalPackagesPath, self.onError)

    #def setLocalPackagesPath(self, ppaths):
        #for i in range(len(self.p_api_pids)):
            #self.ppaths[self.p_api_pids[i]] = ppaths[i]
        #self.packageApiLoop()

    #def createBundle(self):
        ## treat bundle title
        #try:
            #title = self.params['bundle_title']
        #except:
            #title = '' # ie. "no title"
        #self.params['bundle_title'] = None

        #if title == None or title == '':
            #title = get_default_bundle_name(len(self.porders))
        ## Insert bundle object
        #self.session = create_session()
        #bundle = MscDatabase().createBundle(title, self.session)

        #commands = []
        #for p in self.porders:
            #p_api, pid, order = self.porders[p]
            #pinfos = self.packages[pid]
            #ppath = self.ppaths[pid]
            #params = self.params.copy()

            #if int(order) == int(self.first_order):
                #params['do_wol'] = self.do_wol
            #else:
                #params['do_wol'] = 'off'


            ## override possible choice of do_reboot from the gui by the one declared in the package
            ## (in bundle mode, the gui does not offer enough choice to say when to reboot)
            #params['do_reboot'] = pinfos['do_reboot']
            #cmd = prepareCommand(pinfos, params)
            #command = cmd.copy()
            #command['package_id'] = pid
            #command['connect_as'] = 'root'
            #command['mode'] = self.mode
            #command['root'] = ppath
            #command['order_in_bundle'] = order
            #command['proxies'] = self.proxies
            #command['fk_bundle'] = bundle.id
            #command['do_windows_update'] = "disable"
            #commands.append(command)
        #add = MscDatabase().addCommands(self.ctx, self.session, self.targets, commands, self.gid)
        #if type(add) != int:
            #add.addCallbacks(self.sendResult, self.onError)
        #else:
            #self.onError("Error while creating the bundle")

def prepareCommand(pinfos, params):
    """
    @param pinfos: getPackageDetail dict content
    @param params: command parameters
    @returns: dict with parameters needed to create the command in database
    @rtype: dict
    """
    ret = {}
    ret['start_file'] = pinfos['command']['command']
    ret['do_reboot'] = params['do_reboot']
    ret['do_reboot'] = ((ret['do_reboot'] == 'enable' or ret['do_reboot'] == 'on') and 'enable' or 'disable')
    #TODO : check that params has needed values, else put default one
    # as long as this method is called from the MSC php, the fields should be
    # set, but, if someone wants to call it from somewhere else...
    ret['start_script'] = (params['start_script'] == 'on' and 'enable' or 'disable')
    ret['clean_on_success'] = (params['clean_on_success'] == 'on' and 'enable' or 'disable')
    ret['do_wol'] = (params['do_wol'] == 'on' and 'enable' or 'disable')
    ret['do_wol_on_imaging'] = 'disable'
    ret['next_connection_delay'] = params['next_connection_delay']
    ret['max_connection_attempt'] = params['max_connection_attempt']
    ret['do_inventory'] = (params['do_inventory'] == 'on' and 'enable' or 'disable')
    ret['issue_halt_to'] = (params['issue_halt_to'] == ["done"] and "enable" or "disable")
    ret['maxbw'] = params['maxbw']
    if 'state' not in params :
        ret['state'] = 'active'
    else :
        ret['state'] = params['state']


    if 'proxy_mode' in params:
        ret['proxy_mode'] = params['proxy_mode']
    else:
        ret['proxy_mode'] = 'none'

    if 'deployment_intervals' in params:
        ret['deployment_intervals'] = params['deployment_intervals']
    else:
        ret['deployment_intervals'] = ''

    if 'parameters' in params:
        ret['parameters'] = params['parameters']
    else:
        ret['parameters'] = ''

    try:
        ret['start_date'] = convert_date(params['start_date'])
    except:
        ret['start_date'] = '0000-00-00 00:00:00' # ie. "now"

    try:
        ret['end_date'] = convert_date(params['end_date'])
    except:
        ret['end_date'] = '0000-00-00 00:00:00' # ie. "no end date"

    if 'ltitle' in params:
        ret['title'] = params['ltitle']
    else:
        ret['title'] = ''

    if ret['title'] == None or ret['title'] == '':
        localtime = time.localtime()
        ret['title'] = "%s (%s) - %04d/%02d/%02d %02d:%02d:%02d" % (
            pinfos['label'],
            pinfos['version'],
            localtime[0],
            localtime[1],
            localtime[2],
            localtime[3],
            localtime[4],
            localtime[5]
        )

    if pinfos['files'] != None:
        ret['files'] = map(lambda hm: hm['id']+'##'+hm['path']+'/'+hm['name'], pinfos['files'])
    else:
        ret['files'] = ''
    return ret

class SendPackageCommand:
    def __init__(self, ctx, pid, targets, params, mode, gid = None, bundle_id = None, order_in_bundle = None, proxies = [], cmd_type = 0):
        self.ctx = ctx
        self.pid = pid
        self.targets = targets
        self.params = params.copy()
        self.mode = mode
        self.gid = gid
        self.bundle_id = bundle_id
        self.order_in_bundle = order_in_bundle
        self.proxies = proxies
        self.cmd_type = cmd_type

    def send(self):
        from mmc.plugins.xmppmaster.master.lib.managepackage import apimanagepackagemsc
        self.pinfos =  apimanagepackagemsc.getPackageDetail(self.pid)
        return self.setRoot("/var/lib/pulse2/packages")

    def setRoot(self, root):
        logging.getLogger().debug(root)
        if self.pid != None and self.pid != '' and not root:
            return self.onError("Can't get path for package %s" % self.pid)
        self.root = root
        # If is an empty Package, avoid file uploading
        if 'size' in self.pinfos:
            if self.pinfos['size'] == 0 :
                self.pinfos['files'] = None
        # Prepare command parameters for database insertion
        cmd = prepareCommand(self.pinfos, self.params)
        # cmd['maxbw'] is in kbits, set in bits
        cmd['maxbw'] = int(cmd['maxbw']) * 1024
        cmd['do_wol_with_imaging'] = 'disable'
        cmd['do_windows_update'] = 'disable'
        _patterns = {'do_reboot': cmd['do_reboot'],
                     'do_halt': cmd['issue_halt_to'],
                     'do_wol': cmd['do_wol'],
                     'do_wol_with_imaging': cmd['do_wol_with_imaging'],
                     'do_windows_update': cmd['do_windows_update'],
                     'do_inventory': cmd['do_inventory'],
                     }
        cmd['start_file'], patternActions = MscDatabase().applyCmdPatterns(cmd['start_file'], _patterns)
        addCmd = MscDatabase().addCommand(  # TODO: refactor to get less args
            self.ctx,
            self.pid,
            cmd['start_file'],
            cmd['parameters'],
            cmd['files'],
            self.targets, # TODO : need to convert array into something that we can get back ...
            self.mode,
            self.gid,
            cmd['start_script'],
            cmd['clean_on_success'],
            cmd['start_date'],
            cmd['end_date'],
            "root", # TODO: may use another login name
            cmd['title'],
            patternActions['do_halt'],
            patternActions['do_reboot'],
            patternActions['do_wol'],
            patternActions['do_wol_with_imaging'],
            patternActions['do_windows_update'],
            cmd['next_connection_delay'],
            cmd['max_connection_attempt'],
            patternActions['do_inventory'],
            cmd['maxbw'],
            self.root,
            cmd['deployment_intervals'],
            self.bundle_id,
            self.order_in_bundle,
            cmd['proxy_mode'],
            self.proxies,
            cmd['state'],
            cmd_type = self.cmd_type
        )
        return addCmd

def convert_date(date = '0000-00-00 00:00:00'):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(date, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(date, "%Y/%m/%d %H:%M:%S"))
        except ValueError:
            timestamp = '0000-00-00 00:00:00'
    return timestamp


#def _p_apiuniq(list, x):
  #try:
    #list.index(x)
  #except:
    #list.append(x)

#def _merge_list(list, x):
    #for i in x:
      #try:
        #list.index(i)
      #except:
        #pass
    #rem = []
    #for i in list:
      #try:
        #x.index(i)
      #except:
        #rem.append(i)
    #for i in rem:
      #list.remove(i)

#class GetPackagesFiltered:

    #def __init__(self, ctx, filt):
        #self.ctx = ctx
        #self.filt = filt
        #self.packages = []

    #def get(self):
        #if "packageapi" in self.filt:
            #if 'pending' in self.filt:
                #ret = defer.maybeDeferred(PackageGetA(self.filt["packageapi"]).getAllPendingPackages, False)
            #else:
                #ret = defer.maybeDeferred(PackageGetA(self.filt["packageapi"]).getAllPackages, False)
            #ret.addCallbacks(self.sendResult, self.onError)
            #ret.addErrback(lambda err: self.onError(err))
        #else:
            #ret = self.sendResult()

    #def sendResult(self, packages = []):
        #ret = map(lambda m: [m, 0, self.filt['packageapi']], packages)
        #self.deferred.callback(ret)

    #def onError(self, error):
        #logging.getLogger().error("GetPackagesFiltered: %s", str(error))
        #self.deferred.callback([])

#class GetPackagesUuidFiltered:

    #def __init__(self, ctx, filt):
        #self.ctx = ctx
        #self.filt = filt

    #def onError(self, error):
        #logging.getLogger().error("GetPackagesUuidFiltered: %s", str(error))
        #return self.deferred.callback([])

    #def sendResult(self, packages = []):
        #self.deferred.callback(packages)

    #def get(self):
        #try:
            #self.machine = self.filt["uuid"]
            #d = MirrorApi().getApiPackage(self.machine)
            #d.addCallbacks(self.uuidFilter2, self.onError)
            #d.addErrback(lambda err: self.onError(err))
        #except KeyError:
            #self.sendResult()

    #def uuidFilter2(self, package_apis):
        #self.package_apis = package_apis
        ## warn as we do pop in package retrival but we want to keep the packages
        ## in the good order, we need to reverse the package api list order
        #self.package_apis.reverse()
        #d = MirrorApi().getMirror(self.machine)
        #d.addCallbacks(self.uuidFilter3, self.onError)
        #d.addErrback(lambda err: self.onError(err))

    #def uuidFilter3(self, mirror):
        #self.mirror = mirror
        #self.index = -1
        #self.packages = []
        #self.getPackagesLoop()

    #def getPackagesLoop(self, result = None):
        #if result and not isinstance(result, failure.Failure):
            #self.index = self.index + 1
            #self.packages.extend(map(lambda m: [m, self.index, self.p_api], result))
        #if self.package_apis:
            #if type(self.package_apis) == list:
                #self.p_api = self.package_apis.pop()
            #else:
                #self.p_api = self.package_apis
            #if 'pending' in self.filt:
                #d = defer.maybeDeferred(PackageGetA(self.p_api).getAllPendingPackages, self.mirror)
            #else:
                #d = defer.maybeDeferred(PackageGetA(self.p_api).getAllPackages, self.mirror)
            #d.addCallbacks(self.getPackagesLoop)
        #else:
            #self.sendResult(self.packages)

#class GetPackagesGroupFiltered:

    #def __init__(self, ctx, filt):
        #self.ctx = ctx
        #self.filt = filt
        #self.gid = None

    #def onError(self, error):
        #logging.getLogger().error("GetPackagesGroupFiltered: %s", str(error))
        #return self.deferred.callback([])

    #def sendResult(self, packages = []):
        #self.deferred.callback(packages)

    #def get(self):
        #try:
            #self.gid = self.filt["group"]
        #except KeyError:
            #self.sendResult()
        #if self.gid:
            #self.machines = []
            #if ComputerGroupManager().isdyn_group(self.ctx, self.gid):
                #if ComputerGroupManager().isrequest_group(self.ctx, self.gid):
                    #self.machines = ComputerGroupManager().requestresult_group(self.ctx, self.gid, 0, -1, '')
                #else:
                    #self.machines = ComputerGroupManager().result_group(self.ctx, self.gid, 0, -1, '')
            #else:
                #self.machines = ComputerGroupManager().result_group(self.ctx, self.gid, 0, -1, '')
            #d = MirrorApi().getApiPackages(self.machines)
            #d.addCallbacks(self.getMirrors, self.onError)
            #d.addErrback(lambda err: self.onError(err))

    #def getMirrors(self, package_apis):
        #self.package_apis = package_apis
        #d = MirrorApi().getMirrors(self.machines)
        #d.addCallbacks(self.getMirrorsResult, self.onError)
        #d.addErrback(lambda err: self.onError(err))

    #def getMirrorsResult(self, mirrors):
        #self.mirrors = mirrors
        #mergedlist = []
        #for i in range(len(self.package_apis)):
            #tmpmerged = []
            #for papi in self.package_apis[i]:
                #tmpmerged.append((papi, self.mirrors[i]))
            #mergedlist.insert(i, tmpmerged)

        ##if mergedlist:
        #if not len(mergedlist):
            #self.sendResult()
        #else:
            #plists = []
            #i = 0
            #for i in range(len(mergedlist[0])): # all line must have the same size!
                #plists.insert(i, [])
                #try:
                    #map(lambda x: _p_apiuniq(plists[i], x[i]), mergedlist)
                #except IndexError:
                    #logging.getLogger().error("Error with i=%d" %i)
            #self.plists = plists
            #self.index = -1
            #self.p_apis = None
            #self.packages = []
            #self.tmppackages = []
            #self.getPackagesLoop()

    #def getPackagesLoop(self, result = None):
        #if result:
            #if not isinstance(result, failure.Failure):
                #self.tmppackages.append(result)
            #else:
                #logging.getLogger().error("%s", str(result))
        #if not self.p_apis and self.tmppackages:
            ## Merge temporary results
            #lp = self.tmppackages[0]
            #map(lambda p: _merge_list(lp, p), self.tmppackages)
            #self.packages.extend(map(lambda m: [m, self.index, self.p_api_first], lp))
            #self.tmppackages = []
        #if self.plists and not self.p_apis:
            ## Fill self.p_apis if empty
            #self.p_apis = self.plists.pop()
            #self.p_api_first = self.p_apis[0][0]
            #self.index = self.index + 1
        #if self.p_apis:
            #p_api = self.p_apis.pop()
            #if 'pending' in self.filt:
                #d = defer.maybeDeferred(PackageGetA(p_api[0]).getAllPendingPackages, p_api[1])
            #else:
                #d = defer.maybeDeferred(PackageGetA(p_api[0]).getAllPackages, p_api[1])
            #d.addCallbacks(self.getPackagesLoop)
        #else:
            ## No more remote call to do, we are done
            #self.sendResult(self.packages)

#class GetPackagesAdvanced:

    #def __init__(self, ctx, filt):
        #self.ctx = ctx
        #self.filt = filt
        #self.packages = []

    #def get(self):
        #g1 = GetPackagesFiltered(self.ctx, self.filt)
        #g1.deferred = defer.Deferred()
        #g2 = GetPackagesUuidFiltered(self.ctx, self.filt)
        #g2.deferred = defer.Deferred()
        #g3 = GetPackagesGroupFiltered(self.ctx, self.filt)
        #g3.deferred = defer.Deferred()
        #dl = defer.DeferredList([g1.deferred, g2.deferred, g3.deferred])
        #dl.addCallback(self.sendResult)
        #g1.get()
        #g2.get()
        #g3.get()

    #def sendResult(self, results):
        ## Aggregate all results
        #for result in results:
            #status, packages = result
            #if status == defer.SUCCESS:
                #self.packages.extend(packages)
        ## Apply filter if wanted
        #try:
            #if 'bundle' in self.filt:
                #if self.filt['bundle'] == 1:
                    #self.packages = [p for p in self.packages if p[0]['sub_packages']]
                #else:
                    #self.packages = [p for p in self.packages if not p[0]['sub_packages']]

        #except KeyError:
            #pass
        ## Sort on the mirror order then on the label, and finally on the version number
        #self.packages.sort(lambda x, y: 10*cmp(x[1], y[1]) + 5*cmp(x[0]['label'], y[0]['label']) + cmp(x[0]['version'], y[0]['version']))
        #self.deferred.callback(self.packages)
