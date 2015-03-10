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

import logging

from twisted.internet.defer import DeferredList, fail
from twisted.internet.error import TCPTimedOutError, ConnectionRefusedError
from twisted.internet.error import ConnectError

from pulse2.network import NetUtils
from pulse2.scheduler.config import SchedulerConfig
from pulse2.scheduler.network import chooseClientIP
from pulse2.scheduler.checks import getCheck, getAnnounceCheck
from pulse2.scheduler.xmlrpc import getProxy


class Stats :
    """
    Transforms the launchers statistics dictionnary to a struct.

    Example of slice of imported dictionnary :

    {'slots': {'slottotal': 300, 'slotused': 0},
    'memory': {'total': 2074884, 'swapused': 512, 'free': 1396152}}

    Result :
    self.slots.slottotal = 300
    self.slots.slotused = 0
    self.memory.total = 2074884
    self.memory.swapused = 512
    self.memory.free = 1396152
    """
    def __init__(self, stats):
        """
        @param stats: statistics of checked launcher
        @type stats: dict
        """
        for cont_attr_name, values in stats.items():
            cont_attr = type('Statistics', (object,), values)
            setattr(self, cont_attr_name, cont_attr)

def getClientCheck(target):
    return getCheck(SchedulerConfig().client_check, target);

def getServerCheck(target):
    return getCheck(SchedulerConfig().server_check, target);

class NoLauncherError(Exception):
    def __repr__(self):
        return "No launcher to use"

class LauncherCallError(Exception):

    def __init__(self, launcher):
        self.launcher = launcher

    def __repr__(self):
        return "Unable to contact the launcher %s" % self.launcher


class LauncherCallingProvider(type):
    """
    Provides a optimal choice of launcher and the remote calls.

    The choice is primarily based on the "geographic" detection
    (preferred_network parameter), but in the case of insufficients
    resources is selected a launcher with the lowest load.

    This provider can be implemented as a metaclass.
    """
    # All launchers URLs identified by name of launcher
    launchers = {}
    # A launcher evaulated as the nearest
    default_launcher = None
    # No need the launcher detection
    #single_mode = len(launchers) == 1
    @property
    def single_mode(self):
        return len(self.launchers) == 1

    def __new__(cls, name, bases, attrs):
        """
        A metaclass stuff to implement.

        @param name: name of new instance
        @type name: str

        @param bases: types to inherit
        @type bases: tuple

        @param attrs: dictionnary of attributtes
        @type attrs: dict
        """
        my_dict = dict((k, v) for (k, v) in cls.__dict__.items()
                if not k.startswith("__"))
        attrs.update(my_dict)
        return type.__new__(cls,name, bases, attrs)


    def _call(self, launcher, method, *args):
        """
        Calls a remote method on selected launcher.

        @param launcher: name of launcher
        @type launcher: str

        @param method: method name to call
        @type method: str

        @param args: arguments of called method
        @type args: list

        @return: result of remote method
        @rtype: Deferred
        """
        if launcher :
            logging.getLogger().debug("Calling on launcher: method %s(%s)" % (method, str(args)))
            uri = self.launchers[launcher]
            proxy = getProxy(uri)
            d = proxy.callRemote(method, *args)
            d.addErrback(self._call_error, launcher, method)
            return d
        else :
            return fail(NoLauncherError)

    def _call_error(self, failure, launcher, method):
        """
        An errorback attached on remote method call.

        @param failure: reason of fail
        @type failure: callback failure

        @param launcher: name of launcher
        @type launcher: str

        @param method: method name to call
        @type method: str
        """
        err = failure.trap(TCPTimedOutError)
        if err == TCPTimedOutError :
            logging.getLogger().warn("Timeout raised on launcher '%s' when calling method '%s'" % (launcher, method))
            logging.getLogger().warn("Call aborted")
        else :
            logging.getLogger().error("An error occured when calling method %s on launcher %s: %s" %
                (method, launcher, failure))
        return failure

    def get_stats(self, launcher):
        """
        Gets the load balancing statistics of launcher.

        @param launcher: name of launcher
        @type launcher: str

        @return: launchers statistics
        @rtype: Deferred
        """
        d = self._call(launcher, "get_health")
        d.addCallback(self._stats_extract, launcher)
        d.addErrback(self._eb_stats, launcher)

        return d

    def _stats_extract(self, stats_dict, launcher):
        """
        Converts the statistics dictionnary on a struct.

        @param stats_dict: launchers statistics
        @type stats_dict: dict

        @param launcher: name of launcher
        @type launcher: str

        @return: statistics on a structured format
        @rtype: list
        """
        if stats_dict :
            return Stats(stats_dict), launcher
        else :
            return fail(LauncherCallError(launcher))


    def _eb_stats(self, failure, launcher):
        """
        An errorback attached on stats getting.

        @param failure: reason of fail
        @type failure: callback failure

        @param launcher: name of launcher
        @type launcher: str
        """
        err = failure.trap(TCPTimedOutError)
        if err == TCPTimedOutError :
            logging.getLogger().warn("Timeout raised on launcher '%s' when getting the stats" % launcher)
        else :
            logging.getLogger().error("An error occured when extract the stats from launcher %s: %s" %
                (launcher, failure))
        return failure

    def is_default_free(self):
        """
        Checks the default launcher for the slots disponibility.

        @return: True if one or more slots free
        @rtype: Deferred
        """
        d = self.get_stats(self.default_launcher)
        @d.addCallback
        def cb(result):
            if result and isinstance(result, tuple):
                stats, launcher = result
                if stats.slots.slottotal - stats.slots.slotused > 0 :
                    return True
            return False
        return d

    def get_all_slots(self):
        """
        Gets the total of slots from all launchers.

        @return: total of slots per launcher
        @rtype: dict
        """
        d = self._get_all_stats()
        d.addCallback(self._extract_total_slots)
        @d.addErrback
        def _eb(failure):
            err = failure.trap(ConnectError)
            if err == ConnectError:
                logging.getLogger().warn("Unable to get the slots from launcher")
            else :
                logging.getLogger().error("An error occured when getting the slots from launcher: %s" % failure)
        return d


    def _get_all_stats(self):
        """
        Collects the statistics.

        @return: list of statistics
        @rtype: DeferredList
        """
        dl = []
        for launcher in self.launchers.keys() :
            d = self.get_stats(launcher)
            dl.append(d)

        return DeferredList(dl)

    def _extract_total_slots(self, results):
        """
        Gets the total of slots from all launchers.

        @param results: list of statistics
        @type results: list

        @return: total of slots per launcher
        @rtype: dict
        """
        for success, result in results :
            if success :
                stats, launcher = result
                self.slots[launcher] = stats.slots.slottotal
            else :
                if hasattr(result, "trap"):
                    err = result.trap(ConnectionRefusedError, ConnectError)
                    if err in (ConnectionRefusedError, ConnectError) :
                        logging.getLogger().warn("Cannot contact a launcher from list to detect the slots !")
                    else :
                        logging.getLogger().warn("Getting the slots number failed: %s" % result)
                else :
                     logging.getLogger().error("Getting the slots number failed: %s" % result)

                logging.getLogger().info("Set slots to default value from scheduler's config file")



        return self.slots

    def _extract_best_candidate(self, results):
        """
        Based on statistics, selects the best launcher.

        @param results: list of statistics
        @type results: list

        @return: selected launcher
        @rtype: str
        """
        final_launcher = None
        best_score = 0
        for success, result in results :
            if success :
                stats, launcher = result
                score = stats.slots.slottotal - stats.slots.slotused
                if score > best_score:
                    best_score = score
                    final_launcher = launcher
        if best_score > 0 :
            return final_launcher
        else :
            logging.getLogger().warn("No free slots on launchers, operation aborted")
            return None

    def _eb_select(self, failure):
        """
        A launcher select errorback.

        @param failure: reason of fail
        @type failure: callback failure
        """
        err = failure.trap(TCPTimedOutError)
        if err == TCPTimedOutError :
            logging.getLogger().warn("Timeout raised when selecting a launcher")
        else :
            logging.getLogger().error("An error occured when selecting a launcher: %s" % failure)
        return failure

    def _dispatch_launchers(self, method, *args):
        """
        Extract the balance statistics and select of a launcher

        @param method: method name to call
        @type method: str

        @param args: arguments of called method
        @type args: list
        """
        d = self._get_all_stats()
        d.addCallback(self._extract_best_candidate)
        d.addCallback(self._call, method, *args)
        d.addErrback(self._eb_select)
        return d

        #@d.addErrback
        #def _eb(failure):
        #    err = failure.trap(TCPTimedOutError)
        #    if err == TCPTimedOutError :
        #        logging.getLogger().warn("Timeout raised when dispatching the launchers")
        #    else :
        #        logging.getLogger().error("An error occured when dispatch the launchers: %s" % failure)


        # TODO - create a parameter to switch between standard launchers
        #        balancing and this 'forcing' of default launcher bellow
        #        (based on preferred_network in launchers section)
        #d_main = self.is_default_free()
        #
        #@d_main.addCallback
        #def _cb(is_free):
        #    if is_free :
        #        d = self._call(self.default_launcher, method, *args)
        #        d.addErrback(self._eb_select)
        #    else :
        #        d = self._get_all_stats()
        #        d.addCallback(self._extract_best_candidate)
        #        d.addCallback(self._call, method, *args)
        #        d.addErrback(self._eb_select)
        #
        #    return d
        #
        #return d_main

    def call_method_on_launcher(self, launcher, method, *args):
        """
        forced call method on given launcher.

        @param launcher: called launcher
        @type method: str

        @param method: method name to call
        @type method: str

        @param args: arguments of called method
        @type args: list

        @return: result of remote method
        @rtype: Deferred
        """
        return self._call(launcher, method, *args)


    def call_method(self, method, *args):
        """
        Selects a launcher and calls a remote method.

        @param method: method name to call
        @type method: str

        @param args: arguments of called method
        @type args: list

        @return: result of remote method
        @rtype: Deferred
        """
        if not self.single_mode :
            return self._dispatch_launchers(method, *args)
        else :
            return self._call(self.default_launcher,
                              method,
                              *args)

def same_call(method):
    """
    Decorates a method to be call having the same call name and arguments

    @param method: decorated method
    @type method: callable

    @return: xmlrpc calling provider
    @rtype: Deferred
    """
    # Example of use :
    #
    # declaration like this
    #
    # @same_call
    # def method_name(self, id, client, command)
    #     pass
    #
    # is equaled to
    #
    # def method_name(self, id, client, command):
    #     return self.call_method("method_name", id, client, command)

    def wrapped(self, *args, **kwargs):
        return self.call_method(method.__name__, *args, **kwargs)
    return wrapped



class RemoteCallProxy :
    """
    Provides the remote calls to launchers.

    Each launcher method must be declared here and must return
    the implemented providing method call_method which ensures
    a optimal choice of launcher.
    To avoid repeating declarations (same method name and arguments),
    it's possible to use @same_call decorator.

    Instance of this class can be created on start of scheduler
    and reused for all calls.
    """
    # implements the remote calls with a optimal choice of launcher
    __metaclass__ = LauncherCallingProvider

    def __init__(self, launchers, slots, default_launcher=None):
        """
        @param launchers: a dictionnary of all URL addresses of used launchers
        @type launchers: dict
        """
        self.launchers = launchers
        self.default_launcher = default_launcher
        self.slots = slots


    @same_call
    def sync_remote_push(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote copy on target, sync mode """
        pass
    @same_call
    def async_remote_push(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote copy on target, async mode """
        pass
    @same_call
    def sync_remote_pull(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote copy on target, sync mode """
        pass
    @same_call
    def async_remote_pull(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote copy on target, async mode """
        pass
    @same_call
    def sync_remote_delete(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote delete on target, sync mode """
        pass
    @same_call
    def async_remote_delete(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote delete on target, async mode """
        pass
    @same_call
    def sync_remote_exec(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote exec on target, sync mode """
        pass
    @same_call
    def async_remote_exec(self, command_id, client,  files_list, wrapper_timeout):
        """ Handle remote exec on target, async mode """
        pass
    @same_call
    def sync_remote_quickaction(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote quick action on target, sync mode """
        pass
    @same_call
    def async_remote_quickaction(self, command_id, client, files_list, wrapper_timeout):
        """ Handle remote quick action on target, async mode """
        pass
    @same_call
    def sync_remote_inventory(self, command_id, client, wrapper_timeout):
        """ Handle remote inventory on target, sync mode """
        pass
    @same_call
    def async_remote_inventory(self, command_id, client, wrapper_timeout):
        """ Handle remote inventory on target, async mode """
        pass
    @same_call
    def sync_remote_reboot(self, command_id, client, wrapper_timeout):
        """ Handle remote reboot on target, sync mode """
        pass
    @same_call
    def async_remote_reboot(self, command_id, client,  wrapper_timeout):
        """ Handle remote reboot on target, async mode """
        pass
    @same_call
    def sync_remote_halt(self, command_id, client, wrapper_timeout):
        """ Handle remote halt on target, sync mode """
        pass
    @same_call
    def async_remote_halt(self, command_id, client,  wrapper_timeout):
        """ Handle remote halt on target, async mode """
        pass

    def downloadFile(self,
                     uuid,
                     fqdn,
                     shortname,
                     ips,
                     macs,
                     netmasks,
                     path,
                     bwlimit):
        # choose a way to perform the operation

        ip = chooseClientIP({'uuid': uuid,
                             'fqdn': fqdn,
                             'shortname': shortname,
                             'ips': ips,
                             'macs': macs,
                             'netmasks': netmasks
                           })

        if not ip or not NetUtils.is_ipv4_format(ip):
            logging.getLogger().warn("Ivalid IP address format: '%s'" % str(ip))
            return fail(False)

        client = {'host': ip,
                  'chosen_ip': ip,
                  'uuid': uuid,
                  'shortname': shortname,
                  'ip': ips,
                  'macs': macs,
                  'protocol': 'ssh'
                  }
        client['client_check'] = getClientCheck(client)
        client['server_check'] = getServerCheck(client)
        client['action'] = getAnnounceCheck('download')

        return self.call_method('download_file', client, path, bwlimit)


    def establish_proxy(self,
                       uuid,
                       fqdn,
                       shortname,
                       ips,
                       macs,
                       netmasks,
                       requestor_ip,
                       requested_port):

        def _finalize(result):
            if type(result) == list:  # got expected struct
                (launcher, host, port, key) = result
                if key == '-':
                    # Key not provided => TCP Proxy
                    logging.getLogger().info(
                        'VNC Proxy: launcher "%s" created new TCP Proxy to "%s:%s"'
                        % (launcher, host, str(port)))
                else:
                    # Key provided => Websocket Proxy
                    logging.getLogger().info(
                        'VNC Proxy: launcher "%s" created new WebSocket Proxy to "%s:%s" with key "%s"'
                        % (str(launcher), str(host), str(port), str(key)))
                if host == '':
                    host = SchedulerConfig().launchers[launcher]['host']
                return (host, port, key)
            else:
                return False
        # choose a way to perform the operation
        ip = chooseClientIP({'uuid': uuid,
                             'fqdn': fqdn,
                             'shortname': shortname,
                             'ips': ips,
                             'macs': macs,
                             'netmasks': netmasks
                           })

        if not ip or not NetUtils.is_ipv4_format(ip):
            logging.getLogger().warn("Ivalid IP address format: '%s'" % str(ip))
            return fail(False)

        client = {'host': ip,
                  'chosen_ip': ip,
                  'uuid': uuid,
                  'shortname': shortname,
                  'ip': ips,
                  'macs': macs,
                  'protocol': 'tcpsproxy'
                 }
        client['client_check'] = getClientCheck(client)
        client['server_check'] = getServerCheck(client)
        client['action'] = getAnnounceCheck('vnc')

        d = self.call_method('tcp_sproxy', client, requestor_ip, requested_port)
        d.addCallback(_finalize)
        @d.addErrback
        def _eb(failure):
            logging.getLogger().warn("VNC proxy open failed: %s" % str(failure))


        return d

    @same_call
    def wol(self, mac_addrs, target_bcast):
        pass


    def ping_client(self, client):
        return self.call_method("icmp", client)

    def probe_client(self, client):
        return self.call_method("probe", client)

    def ping_and_probe_client(self, client):
        """
        returns :
            0 => ping NOK
            1 => ping OK, ssh NOK
            2 => ping OK, ssh OK
        """
        def _pingcb(result, client=client):
            def _probecb(result, client=client):
                if not result == "Not available":
                    return 2
                return 1
            if result:
                d = self.probe_client(client)
                d.addCallback(_probecb)
                return d
            return 0
        d = self.ping_client(client)
        d.addCallback(_pingcb)
        return d

    #TODO
    def getLaunchersBalance(self) : pass

    @same_call
    def get_zombie_ids(self):
        pass









