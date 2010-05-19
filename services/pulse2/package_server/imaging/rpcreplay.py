# -*- coding: utf-8; -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Pulse 2.
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Module to keep imaging API internal state. We store RPC commands that were not
send successfully to the MMC agent.
"""

import pickle
import os
import logging
import time

from twisted.internet import reactor, task, defer

from pulse2.utils import Singleton
from pulse2.apis import makeURL
from pulse2.package_server.config import P2PServerCP as PackageServerConfig
from pulse2.package_server.imaging.api.client import ImagingXMLRPCClient

class RPCStore(Singleton):

    """
    Singleton class that stores RPC into a state file.
    """

    PENDING = 0
    INPROGRESS = 1

    def init(self):
        """
        Initialize object.
        """
        self.logger = logging.getLogger('imaging')
        self.logger.debug('Initializing imaging RPC replay file')
        self.filename = PackageServerConfig().imaging_api['rpc_replay_file']
        self._initStateFile()

    def _initStateFile(self):
        """
        Create an empty state file if it doesn't exist, or reset all RPC states
        to PENDING.
        """
        data = self.get()
        for key in data:
            data[key][0] = self.PENDING
        self._updateStateFile(data)

    def _updateStateFile(self, data):
        """
        Update the RPC state file content.
        """
        assert(type(data) == dict)
        self.logger.debug('Updating RPC replay file: %s' % self.filename)
        fobj = file(self.filename, 'w')
        self.logger.debug('Dumping and writing data')
        pickle.dump(data, fobj)
        fobj.close()
        self.logger.debug('RPC replay file successfully updated with %d items'
                          % len(data))

    def get(self):
        """
        Returns data contained in the RPC state file.
        """
        if not os.path.exists(self.filename):
            ret = {}
        else:
            fobj = file(self.filename, 'r')
            ret = pickle.load(fobj)
            fobj.close()
        assert(type(ret) == dict)
        return ret

    def add(self, function, args, timestamp = None):
        """
        Add a new function with its arguments to the RPC replay file.

        @param first: if True, put the RPC function first
        @type first: bool
        """
        data = self.get()
        if not timestamp:
            timestamp = time.time()
        data[timestamp] = [self.PENDING, function, args]
        self._updateStateFile(data)

    def pop(self, count):
        """
        Get count items from the RPC replay file. The file will be updated !

        @rtype: tuple
        @returns: a tuple with the RPC to replay, or None if the store is empty
        """
        items = []
        try:
            self.logger.debug('Taking at most %d items from the RPC replay file' % count)
            data = self.get()
            if data:
                timestamps = data.keys()
                timestamps.sort()
                found = 0
                i = 0
                while found != count and i < len(timestamps):
                    tstamp = timestamps[i]
                    # Is this item still valid ?
                    if time.time() - tstamp < 7 * 24 * 3600:
                        if data[tstamp][0] == self.PENDING:
                            item = [tstamp] + data[tstamp][1:]
                            items.append(item)
                            data[tstamp][0] = self.INPROGRESS
                            found += 1
                    else:
                        # Discard entry
                        self.logger.debug('Removing old entry: %s'
                                          % str(data[tstamp]))
                        del data[tstamp]
                    i += 1
                self._updateStateFile(data)
                self.logger.debug('Done, found %d items' % len(items))
            else:
                self.logger.debug('RPC replay file is empty')
        except Exception, e:
            self.logger.exception(e)
        return items

    def discardRPCs(self, timestamps):
        """
        Remove from the RPC state file the RPCs with the given timestamp
        """
        if timestamps:
            self.logger.debug('Removing the RPCs with these timestamps: %s'
                              % str(timestamps))
            try:
                data = self.get()
                for timestamp in timestamps:
                    del data[timestamp]
                self._updateStateFile(data)
                self.logger.debug('Removal done')
            except Exception, e:
                self.logger.error(e)

    def check(self):
        """
        Check if the RPCStore is valid
        """
        try:
            self.get()
            ret = True
        except Exception, e:
            self.logger.error('Invalid RPC replay file %s: %s'
                              % (self.filename, e))
            ret = False
        return ret

    def debug(self):
        """
        Write RPC store content in log file
        """
        self.logger.debug('RPC store content:')
        self.logger.debug(self.get())

class RPCReplay(Singleton):

    """
    This singleton class tries periodically to re-play the RPCs that were not
    sent to the MMC agent and saved into the RPCStore object.

    The RPCs replay is scheduled every self.timer seconds.
    self.count RPCs are replayed according to their timestamp order, with an
    interval of self.interval seconds between each RPC so that we don't
    overload the RPC server (the MMC agent).
    """

    def init(self):
        """
        Initialize object, and the RPCStore object.
        """
        self.logger = logging.getLogger('imaging')
        self.logger.debug('Initializing imaging RPC replay manager')
        self.timer = PackageServerConfig().imaging_api['rpc_loop_timer']
        self.count = PackageServerConfig().imaging_api['rpc_count']
        self.interval = PackageServerConfig().imaging_api['rpc_interval']
        self._replaying = False
        self.store = RPCStore()
        self.store.init()

    def check(self):
        """
        Check if the RPCManager object will work
        """
        return self.store.check()

    def firstRun(self):
        """
        First run by the RPC replay manager
        """
        self._run()

    def startLoop(self):
        """
        Schedule the next RPC replay
        """
        self.logger.debug('Scheduling next RPC replay in %d seconds'
                          % self.timer)
        reactor.callLater(self.timer, self._run)

    def onError(self, error, funcname, args, default_return = [], timestamp = None):
        """
        Error back to be called when a XML-RPC call fails.
        The RPC is saved so that it can be replayed later.
        """
        self.logger.warn('%s %s has failed: %s' % (funcname, args, error))
        self.logger.info('Storing RPC, it will be replayed later')
        self.store.add(funcname, args, timestamp)
        return default_return

    def _getXMLRPCClient(self):
        """
        @return: a XML-RPC client allowing to connect to the agent
        @rtype: ImagingXMLRPCClient
        """
        url, _ = makeURL(PackageServerConfig().mmc_agent)
        return ImagingXMLRPCClient(
            '',
            url,
            PackageServerConfig().mmc_agent['verifypeer'],
            PackageServerConfig().mmc_agent['cacert'],
            PackageServerConfig().mmc_agent['localcert'])

    def _run(self):
        """
        Schedule RPCs replay
        """
        def _rpcReplayCb(result):
            self.logger.debug('All scheduled RPCs have been replayed')
            self.store.discardRPCs(self._success)
            self._replaying = False

        if self._replaying:
            self.logger.debug('RPC replay already in progress')
        else:
            self.logger.debug('Starting scheduling of RPCs to replay')
            self._replaying = True
            self._success = []
            try:
                self.store.debug()
                items = self.store.pop(self.count)
                deferreds = []
                interval = 0
                for item in items:
                    timestamp, func, args = item
                    interval += self.interval
                    d = task.deferLater(reactor, interval,
                                        self._replayRPC, *item)
                    deferreds.append(d)
                dl = defer.DeferredList(deferreds)
                dl.addCallback(_rpcReplayCb)
            except Exception, e:
                self.logger.exception('Error during RPC replay: %s', e)
            self.logger.debug('End scheduling of RPCs to replay')
        self.startLoop()

    def _replayRPC(self, timestamp, func, args):
        """
        Replay one RPC. If it succeed, the RPC timestamp is appended to
        self._success list, which means the RPC will be removed from the state
        file.
        """
        client = self._getXMLRPCClient()
        d = client.callRemote(func, *args)
        d.addCallbacks(lambda x : self._success.append(timestamp),
                       self.onError, errbackArgs = (func, args, 0, timestamp))
        return d
