# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
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
import re
import os
import time
import json

from twisted.internet import defer, reactor
from twisted.internet.task import deferLater
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectionLost

from pulse2.scheduler.queries import CoHQuery, get_history_stdout

from pulse2.scheduler.types import Phase, DIRECTIVE
from pulse2.scheduler.utils import launcher_proxymethod

from pulse2.apis.consts import PULSE2_ERR_CONN_REF, PULSE2_ERR_404, PULSE2_ERR_LOST
from pulse2.apis.consts import PULSE2_ERR_TIMEOUT

from pulse2.scheduler.tracking.proxy import LocalProxiesUsageTracking
from pulse2.apis.clients.mirror import Mirror
from pulse2.scheduler.utils import getClientCheck, getServerCheck
from pulse2.scheduler.utils import chooseClientInfo, WUInjectDB
from pulse2.scheduler.checks import getAnnounceCheck


from pulse2.consts import PULSE2_PROXY_WAITINGFORDEAD_ERROR, PULSE2_PSERVER_FMIRRORFAILED_404_ERROR
from pulse2.consts import PULSE2_PSERVER_FMIRRORFAILED_CONNREF_ERROR, PULSE2_PSERVER_GETFILEURIFROMPACKAGE_ERROR
from pulse2.consts import PULSE2_PSERVER_GETFILEURIFROMPACKAGE_F_ERROR, PULSE2_PSERVER_ISAVAILABLE_FALLBACK
from pulse2.consts import PULSE2_PSERVER_ISAVAILABLE_MIRROR, PULSE2_PSERVER_MIRRORFAILED_404_ERROR
from pulse2.consts import PULSE2_PSERVER_MIRRORFAILED_CONNREF_ERROR, PULSE2_PSERVER_PACKAGEISUNAVAILABLE_ERROR
from pulse2.consts import PULSE2_SUCCESS_ERROR, PULSE2_TARGET_NOTENOUGHINFO_ERROR
from pulse2.consts import PULSE2_UNKNOWN_ERROR


re_file_prot = re.compile('^file://')
re_http_prot = re.compile('^http://')
re_https_prot = re.compile('^https://')
re_smb_prot = re.compile('^smb://')
re_ftp_prot = re.compile('^ftp://')
re_nfs_prot = re.compile('^nfs://')
re_ssh_prot = re.compile('^ssh://')
re_rsync_prot = re.compile('^rsync://')

re_abs_path = re.compile('^/')
re_basename = re.compile('^/[^/]*/(.*)$')
re_rel_path = re.compile('^/(.*)$')
re_file_prot_path = re.compile('^file://(.*)$')


class RemoteControlPhase(Phase):
    """
    A common frame for the phases using the remote calls trough launcher.

    Remote command is resolved by the 'name' attribut, otherwise method
    get_remote_command() can be overriden to return a correct value.
    """
    def get_remote_command(self):
        """
        Returns the command to execute on launcher. Can be overriden.

        @return: command to execute
        @rtype: str
        """
        if self.config.mode == "sync":
            method_name = "sync_remote_%s" % self.name

        elif self.config.mode == 'async':
            method_name = "async_remote_%s" % self.name
        return method_name

    def get_remote_method(self, *args, **kwargs):
        """
        Returns a method to be call on launcher.

        @return: remote method to execute
        @rtype: callable
        """
        method_name = self.get_remote_command()
        method = getattr(self.launchers_provider, method_name)

        return method(*args, **kwargs)



    def get_filelist(self):
        """
        Method to override when a filelist needed as argument.

        @return: list of filenames
        @rtype: list
        """
        return None

    def perform(self):
        """ Perform the phase action """
        return self._perform()

    def _perform(self):
        """ Perform the phase action """
        client = self.get_client(self.name)

        if not client['host']: # We couldn't get an IP address for the target host
            fd = defer.fail(Exception("Not enough information about client to perform %s" % self.name))
            fd.addErrback(self.parse_remote_phase_error,
                          decrement_attempts_left = True,
                          error_code = PULSE2_TARGET_NOTENOUGHINFO_ERROR)
            fd.addErrback(self.got_error_in_error)

            return fd

        if self.config.mode == "sync":
            cb = self.parse_remote_phase_result

        elif self.config.mode == 'async':
            cb = self.parse_remote_phase_order
        else :
            return self.give_up()

        filelist = self.get_filelist()
        if filelist :
            args = [self.coh.id,
                    client,
                    filelist,
                    self.config.max_command_time,
                   ]
        else :
            args = [self.coh.id,
                    client,
                    self.config.max_command_time,
                   ]

        d = self.get_remote_method(*args)

        d.addCallback(cb)
        d.addErrback(self.parse_remote_phase_error)
        d.addErrback(self.got_error_in_error)

        return d

    def parse_remote_phase_error (self,
                               reason,
                               decrement_attempts_left = False,
                               error_code = PULSE2_UNKNOWN_ERROR):
        """
        decrement_attempts_left : by default do not decrement tries as the error
        has most likeley be produced by an internal condition
        error_code : by default we consider un unknwo error was raised (PULSE2_UNKNOWN_ERROR)
        """
        # something goes really wrong: immediately give up
        self.logger.warn("Circuit #%s: %s failed, unattented reason: %s" % (self.coh.id, self.name, reason))
        self.update_history_failed(error_code, '', reason.getErrorMessage())
        return self.switch_phase_failed(decrement_attempts_left)


    def parse_remote_phase_result(self,(exitcode, stdout, stderr)):

        if exitcode == PULSE2_SUCCESS_ERROR: # success
            self.logger.info("Circuit #%s: %s done (exitcode == 0)" % (self.coh.id, self.name))
            self.update_history_done(exitcode, stdout, stderr)
            if self.coh.isStateStopped():
                return DIRECTIVE.KILLED

            if self.phase.switch_to_done():
                return self.next()
            return self.give_up()

        elif self.name in self.config.non_fatal_steps:
            self.logger.info("Circuit #%s: %s failed (exitcode != 0), but non fatal according to scheduler config file" % (self.coh.id, self.name))
            self.update_history_failed(exitcode, stdout, stderr)
            #self.switch_phase_failed()
            self.phase.set_done()
            return self.next()

        else: # failure: immediately give up
            self.logger.info("Circuit #%s: %s failed (exitcode != 0)" % (self.coh.id, self.name))
            self.update_history_failed(exitcode, stdout, stderr)
            return self.switch_phase_failed()


    def parse_remote_phase_order(self, taken_in_account):
        return self.parse_order(self.name, taken_in_account)




class WOLPhase(Phase):
    name = "wol"
    last_wol_attempt = None



    def _apply_initial_rules(self):

        if self.phase.is_done() :
            self.logger.info("Circuit #%s: wol done" % self.coh.id)
            return self.next()

        if not self.target.hasEnoughInfoToWOL() or not self.host:
            # not enough information to perform WOL: ignoring phase but writting this in DB
            self.logger.warn("Circuit #%s: wol couldn't be performed; not enough information in target table" % self.coh.getId())
            self.update_history_failed(PULSE2_TARGET_NOTENOUGHINFO_ERROR,
                               " skipped : not enough information in target table")
            if not self.coh.isStateStopped():
                self.coh.setStateScheduled()
            return self.next()

        if not self.last_wol_attempt and self.phase.is_ready():
            self.phase.set_running()
            return DIRECTIVE.PERFORM


    def perform(self):

        def _cb(result):
            """ results
                0 => ping NOK => do WOL
                1 => ping OK, ssh NOK  => do WOL (computer may just have awoken)
                2 => ping OK, ssh OK => don't do WOL
            """
            if result == 2:
                self.logger.info("Circuit #%s: do not wol (target already up)" % \
                             self.coh.id)
                # FIXME: state will be 'wol_ignored' when implemented in database
                self.update_history_done(PULSE2_SUCCESS_ERROR, "skipped: host already up")

                self.phase.set_done()
                if not self.coh.isStateStopped():
                    self.coh.setStateScheduled()
                return self.next()
            self.logger.info("Circuit #%s: do wol (target not up)" % self.coh.id)
            return self._performWOLPhase()

        def _eb(reason):
            self.logger.warn("Circuit #%s: while probing: %s" % (self.coh.id, reason))
            self.logger.info("Circuit #%s: do wol (target not up)" % self.coh.id)
            return self._performWOLPhase()


        d = self.launchers_provider.ping_and_probe_client(self.host)
        d.addCallback(_cb)
        d.addErrback(_eb)
        return d

    def _performWOLPhase(self):
        # perform call
        mac_addrs = self.target.target_macaddr.split('||')
        target_bcast = self.target.target_bcast.split('||')

        d = self.launchers_provider.wol(mac_addrs, target_bcast)
        d.addCallback(self.parseWOLAttempt)
        d.addErrback(self.parseWOLError)
        d.addErrback(self.got_error_in_error)

        return d

    def parseWOLAttempt(self, attempt_result):

        def setstate(stdout, stderr):
            self.logger.info("Circuit #%s: WOL done and done waiting" % (self.coh.id))
            self.update_history_done(PULSE2_SUCCESS_ERROR, stdout, stderr)

            if self.phase.switch_to_done():
                return self.next()
            else:
                return self.give_up()

        try:
            (exitcode, stdout, stderr) = attempt_result
        except TypeError: # xmlrpc call failed
            self.logger.error("Circuit #%s: WOL request seems to have failed ?!" % (self.coh.id))
            if not self.coh.isStateStopped():
                self.coh.setStateScheduled()
                self.phase.set_ready()
            return self.give_up()
        self.last_wol_attempt = time.time()
        self.logger.info("Circuit #%s: WOL done, now waiting %s seconds for the computer to wake up" % (self.coh.id,self.config.max_wol_time))
        d = deferLater(reactor, self.config.max_wol_time, setstate, stdout, stderr)
        return d

    def parseWOLError(self, reason, decrement_attempts_left = False, error_code = PULSE2_UNKNOWN_ERROR):
        """
           decrement_attempts_left : by default do not decrement tries as the error has most likeley be produced by an internal condition
           error_code : by default we consider un unknwo error was raised (PULSE2_UNKNOWN_ERROR)
        """
        self.logger.warn("Circuit #%s: WOL failed" % self.coh.id)
        self.update_history_failed(error_code, '', reason.getErrorMessage())
        return self.switch_phase_failed(decrement_attempts_left)
# ---------------------------------- UPLOAD -------------------------------------
class UploadPhase(RemoteControlPhase):
    name = "upload"

    def apply_initial_rules(self):
        if not self.cmd.hasSomethingToUpload():
            self.logger.info("Circuit #%s: Nothing to upload" % self.coh.id)
            return self.next()
        ret = self._apply_initial_rules()
        if ret not in (DIRECTIVE.NEXT,
                       DIRECTIVE.GIVE_UP,
                       DIRECTIVE.OVER_TIMED,
                       DIRECTIVE.STOPPED,
                       DIRECTIVE.KILLED,
                       ) :
            return self._switch_on()
        return ret



    def perform(self):
        """
            Handle first Phase: upload time
        """
        # fullfil used proxy (if we can)
        if self.cmd.hasToUseProxy():
            cohq = CoHQuery(self.coh.id)
            #d = defer.maybeDeferred(Analyses().localProxyUploadStatus, cohq)
            d = defer.maybeDeferred(self.dispatcher.local_proxy_upload_status, cohq)
            d.addCallback(self._cbChooseUploadMode)
            return d

        return self._chooseUploadMode()

    def _cbChooseUploadMode(self, result):
        if result == 'waiting':
            self.logger.info("Circuit #%s: waiting for a local proxy" % self.coh.getId())
            #TODO
            if not self.coh.isStateStopped():
                self.coh.setStateScheduled()
            return self.give_up()
        elif result == 'dead':
            self.logger.warn("Circuit #%s: waiting for a local proxy which will never be ready !" % self.coh.getId())
            #self.updateHistory('upload_failed',
            self.update_history_failed(PULSE2_PROXY_WAITINGFORDEAD_ERROR,
                                       '',
                                       'Waiting for a local proxy which will never be ready')
            return self.switch_phase_failed(True)
        elif result == 'server':
            self.logger.info("Circuit #%s: becoming local proxy server" % self.coh.getId())
            self.coh.setUsedProxy(self.coh.getId()) # special case: this way we know we were server
        elif result == 'keeping':
            self.logger.info("Circuit #%s: keeping previously acquiered local proxy settings" % self.coh.getId())
        else:
            self.logger.info("Circuit #%s: becoming local proxy client" % self.coh.getId())
            self.coh.setUsedProxy(result)
        return self._chooseUploadMode()

    def _chooseUploadMode(self):
        # check if we have enough informations to reach the client
        client = self.get_client("transfert")

        if not client['host']: # We couldn't get an IP address for the target host
            err = defer.fail(Exception("Not enough information about client to perform upload"))
            err.addErrback(self.parsePushError,
                           decrement_attempts_left = True,
                           error_code = PULSE2_TARGET_NOTENOUGHINFO_ERROR)
            err.addErrback(self.got_error_in_error)
            return err

        # first attempt to guess is mirror is local (push) or remove (pull) or through a proxy
        if self.coh.isProxyClient():
            # proxy client
            d = self._runProxyClientPhase(client)
        elif re_file_prot.match(self.target.mirrors):
            # local mirror starts by "file://" : prepare a remote_push
            d = self._runPushPhase(client)
        else: # remote push/pull

            try:
                # mirror is formated like this:
                # https://localhost:9990/mirror1||https://localhost:9990/mirror1
                mirrors = self.target.mirrors.split('||')
            except:
                self.logger.warn("Circuit #%s: target.mirror do not seems to be as expected, got '%s', skipping command" % (self.coh.getId(), self.target.mirrors))
                err = defer.fail(Exception("Mirror uri %s is not well-formed" % self.target.mirrors))
                err.addErrback(self.parsePushError, decrement_attempts_left = True)
                err.addErrback(self.got_error_in_error)
                return err

            # Check mirrors
            if len(mirrors) != 2:
                self.logger.warn("Circuit #%s: we need two mirrors ! '%s'" % (self.coh.getId(), self.target.mirrors))
                err = defer.fail(Exception("Mirror uri %s do not contains two mirrors" % self.target.mirrors))
                err.addErrback(self.parsePushError, decrement_attempts_left = True)
                err.addErrback(self.got_error_in_error)
                return err
            mirror = mirrors[0]
            fbmirror = mirrors[1]

            try:
                ma = Mirror(mirror)
                ma.errorback = self._eb_mirror_check
                d = ma.isAvailable(self.cmd.package_id)
                d.addCallback(self._cbRunPushPullPhaseTestMainMirror, mirror, fbmirror, client)
            except Exception, e:
                self.logger.error("Circuit #%s: exception while gathering information about %s on primary mirror %s : %s" % (self.coh.getId(), self.cmd.package_id, mirror, e))
                return self._cbRunPushPullPhaseTestMainMirror(False, mirror, fbmirror, client)

        return d

    def _eb_mirror_check(self, failure):
        if hasattr(failure, "trap"):
            err = failure.trap(TimeoutError,
                               ConnectionRefusedError,
                               ConnectionLost)
            if err == TimeoutError :
                self.logger.warn("Timeout raised during mirror check")
            elif err == ConnectionRefusedError :
                self.logger.warn("Connection refused during mirror check")
            elif err == ConnectionLost :
                self.logger.warn("Connection lost during mirror check")
            else :
                self.logger.warn("An error occurred during mirror check: %s" % str(err))
        return failure



    def _cbRunPushPullPhaseTestMainMirror(self, result, mirror, fbmirror, client):
        if result:
            if type(result) == list and result[0] == 'PULSE2_ERR':
                if result[1] == PULSE2_ERR_CONN_REF:
                    self.update_history_failed(PULSE2_PSERVER_MIRRORFAILED_CONNREF_ERROR,
                                               'Connection refused',
                                               result[2])
                elif result[1] == PULSE2_ERR_404:
                    self.update_history_failed(PULSE2_PSERVER_MIRRORFAILED_404_ERROR, '', result[2])
                elif result[1] == PULSE2_ERR_LOST:
                    self.update_history_failed(PULSE2_PSERVER_MIRRORFAILED_404_ERROR,
                                               'Connection Lost',
                                               result[2])
                elif result[1] == PULSE2_ERR_TIMEOUT:
                    self.update_history_failed(PULSE2_PSERVER_MIRRORFAILED_404_ERROR,
                                               'Timeout',
                                               result[2])
                elif result[1] == PULSE2_UNKNOWN_ERROR:
                    self.update_history_failed(PULSE2_PSERVER_MIRRORFAILED_404_ERROR, '', result[2])
                return self._cbRunPushPullPhaseTestFallbackMirror(result, mirror, fbmirror, client)
            else:
                return self._runPushPullPhase(mirror, fbmirror, client)
        else:
            # Test the fallback mirror
            return self._cbRunPushPullPhaseTestFallbackMirror(result, mirror, fbmirror, client)

    def _cbRunPushPullPhaseTestFallbackMirror(self, result, mirror, fbmirror, client):
        if fbmirror != mirror:
            # Test the fallback mirror only if the URL is the different than the
            # primary mirror
            try:
                ma = Mirror(mirror, fbmirror)
                ma.errorback = self._eb_mirror_check
                d = ma.isAvailable(self.cmd.package_id)
                d.addCallback(self._cbRunPushPullPhase, mirror, fbmirror, client, True)
                return d
            except Exception, e:
                self.logger.error("Circuit #%s: exception while gathering information about %s on fallback mirror %s : %s" % (self.coh.getId(), self.cmd.package_id, fbmirror, e))
        else:
            # Go to upload phase, but pass False to tell that the package is not
            # available on the fallback mirror too
            return self._cbRunPushPullPhase(False, mirror, fbmirror, client)

    def _cbRunPushPullPhase(self, result, mirror, fbmirror, client, useFallback = False):
        if result:
            if type(result) == list and result[0] == 'PULSE2_ERR':
                if result[1] == PULSE2_ERR_CONN_REF:
                    #self.updateHistory('upload_failed',
                    self.update_history_failed(PULSE2_PSERVER_FMIRRORFAILED_CONNREF_ERROR, '', result[2])
                elif result[1] == PULSE2_ERR_404:
                    #self.updateHistory('upload_failed',
                    self.update_history_failed(PULSE2_PSERVER_FMIRRORFAILED_404_ERROR, '', result[2])
                self.logger.warn("Circuit #%s: Package '%s' is not available on any mirror" % (self.coh.getId(), self.cmd.package_id))
                self.update_history_failed(PULSE2_PSERVER_PACKAGEISUNAVAILABLE_ERROR, '', self.cmd.package_id)
                return self.switch_phase_failed(True) # better decrement attemps, as package can't be found
            else:
                # The package is available on a mirror, start upload phase
                return self._runPushPullPhase(mirror, fbmirror, client, useFallback)
        else:
            self.logger.warn("Circuit #%s: Package '%s' is not available on any mirror" % (self.coh.getId(), self.cmd.package_id))
            self.update_history_failed(PULSE2_PSERVER_PACKAGEISUNAVAILABLE_ERROR, '', self.cmd.package_id)
            return self.switch_phase_failed(True) # better decrement attemps, as package can't be found

    def _runProxyClientPhase(self, client):
        # fulfill protocol
        client['protocol'] = 'rsyncproxy'

        proxyCoH = CoHQuery(self.coh.getUsedProxy())
        # get informations about our proxy
        if proxyCoH == None:
            return defer.fail(Exception("Cant access to CoH")).addErrback(self.parsePushError, decrement_attempts_left = True).addErrback(self.got_error_in_error)

        #proxy = self.get_client("transfert")

        proxy = {'host': chooseClientInfo(proxyCoH.target),
                 'uuid': proxyCoH.target.getUUID(),
                 'maxbw': proxyCoH.cmd.maxbw,
                 'client_check': getClientCheck(proxyCoH.target),
                 'server_check': getServerCheck(proxyCoH.target),
                 'action': getAnnounceCheck('transfert'),
                 #'group': getClientGroup(proxyCoH.target)} # TODO - get correct network address
                 'group': ""} # TODO - get from launchers select


        if not proxy['host']: # We couldn't get an IP address for the target host
            return defer.fail(Exception("Can't get proxy IP address")).addErrback(self.parsePushError, decrement_attempts_left = True).addErrback(self.got_error_in_error)
        # and fill struct
        # only proxy['host'] used until now
        client['proxy'] = {'command_id': self.coh.getUsedProxy(),
                           'host': proxy['host'],
                           'uuid': proxy['uuid']
        }

        # build file list
        files_list = []
        for file in self.cmd.files.split("\n"):
            fname = file.split('##')[1]
            if re_abs_path.search(fname):
                fname = re_basename.search(fname).group(1) # keeps last compontent of path
            files_list.append(fname)

        # prepare deffereds
        if self.config.mode == 'sync':
            self.update_history_in_progress()
            mydeffered = self.launchers_provider.sync_remote_pull(self.coh.getId(),
                                                             client,
                                                             files_list,
                                                             self.config.max_upload_time
                                                            )
            mydeffered.\
                addCallback(self.parsePushResult).\
                addErrback(self.parsePushError).\
                addErrback(self.got_error_in_error)
        elif self.config.mode == 'async':
            # 'server_check': {'IP': '192.168.0.16', 'MAC': 'abbcd'}
            mydeffered = self.launchers_provider.async_remote_pull(self.coh.getId(),
                                                              client,
                                                              files_list,
                                                              self.config.max_upload_time
                                                             )

            mydeffered.\
                addCallback(self.parsePushOrder).\
                addErrback(self.parsePushError).\
                addErrback(self.got_error_in_error)
        else:
            mydeffered = None

        return mydeffered

    def _runPushPhase(self, client):
        # fulfill protocol
        client['protocol'] = 'rsyncssh'

        # build file list
        files_list = list()
        for file in self.cmd.files.split("\n"):
            fname = file.split('##')[1]
            if re_abs_path.search(fname):
                fname = re_rel_path.search(fname).group(1)
            files_list.append(os.path.join(re_file_prot_path.search(self.target.mirrors).group(1), fname)) # get folder on mirror

        # prepare deffereds
        if self.config.mode == 'sync':
            #self.updateHistory('upload_in_progress')
            self.update_history_in_progress()
            mydeffered = self.launchers_provider.sync_remote_push(self.coh.getId(),
                                                             client,
                                                             files_list,
                                                             self.config.max_upload_time
                                                             )


            mydeffered.\
                addCallback(self.parsePushResult).\
                addErrback(self.parsePushError).\
                addErrback(self.got_error_in_error)
        elif self.config.mode == 'async':
            # 'server_check': {'IP': '192.168.0.16', 'MAC': 'abbcd'}
            mydeffered = self.launchers_provider.async_remote_push(self.coh.getId(),
                                                              client,
                                                              files_list,
                                                              self.config.max_upload_time
                                                             )

            mydeffered.\
                addCallback(self.parsePushOrder).\
                addErrback(self.parsePushError).\
                addErrback(self.got_error_in_error)
        else:
            mydeffered = None

        # run deffereds
        return mydeffered

    def _runPushPullPhase(self, mirror, fbmirror, client, useFallback = False):
        if useFallback:
            self.update_history_in_progress(PULSE2_PSERVER_ISAVAILABLE_FALLBACK,
                                            '%s\n%s\n%s\n%s' % (self.cmd.package_id,
                                                                mirror,
                                                                self.cmd.package_id,
                                                                fbmirror))
            mirror = fbmirror
        else:
            self.update_history_in_progress(PULSE2_PSERVER_ISAVAILABLE_MIRROR,
                                            '%s\n%s' % (self.cmd.package_id, mirror))
        self.logger.debug("Circuit #%s: Package '%s' is available on %s" % (self.coh.getId(), self.cmd.package_id, mirror))

        ma = Mirror(mirror)
        ma.errorback = self._eb_mirror_check
        fids = []
        for line in self.cmd.files.split("\n"):
            fids.append(line.split('##')[0])
        d = ma.getFilesURI(fids)
        d.addCallback(self._cbRunPushPullPhasePushPull, mirror, fbmirror, client, useFallback)

        return d

    def _cbRunPushPullPhasePushPull(self, result, mirror, fbmirror, client, useFallback):
        if type(result) == list and result[0] == 'PULSE2_ERR':
            if result[1] == PULSE2_ERR_CONN_REF:
                self.update_history_failed(PULSE2_PSERVER_MIRRORFAILED_CONNREF_ERROR, '', result[2])
            elif result[1] == PULSE2_ERR_404:
                self.update_history_failed(PULSE2_PSERVER_MIRRORFAILED_404_ERROR, '', result[2])
            return self.switch_phase_failed(True)

        files_list = result
        file_uris = {}
        choosen_mirror = mirror
        if not False in files_list and not '' in files_list:
            # build a dict with the protocol and the files uris
            if re_http_prot.match(choosen_mirror) or re_https_prot.match(choosen_mirror): # HTTP download
                file_uris = {'protocol': 'wget', 'files': files_list}
            elif re_smb_prot.match(choosen_mirror): # TODO: NET download
                pass
            elif re_ftp_prot.match(choosen_mirror): # FIXME: check that wget may handle FTP as HTTP
                file_uris = {'protocol': 'wget', 'files': files_list}
            elif re_nfs_prot.match(choosen_mirror): # TODO: NFS download
                pass
            elif re_ssh_prot.match(choosen_mirror): # TODO: SSH download
                pass
            elif re_rsync_prot.match(choosen_mirror): # TODO: RSYNC download
                pass
            else: # do nothing
                pass

        # from here, either file_uris is a dict with a bunch of uris, or it is void in which case we give up
        if (not file_uris) or (len(file_uris['files']) == 0):
            if useFallback:
                self.logger.warn("Circuit #%s: can't get files URI from fallback mirror, skipping command" % (self.coh.getId()))
                #self.updateHistory('upload_failed',
                self.update_history_failed(PULSE2_PSERVER_GETFILEURIFROMPACKAGE_F_ERROR,
                                           '',
                                           "%s\n%s" % (self.cmd.package_id, fbmirror))
                # the getFilesURI call failed on the fallback. We have a serious
                # problem and we better decrement attempts
                return self.switch_phase_failed(True)
            elif not fbmirror or fbmirror == mirror:
                self.logger.warn("Circuit #%s: can't get files URI from mirror %s, and not fallback mirror to try" % (self.coh.getId(), mirror))
                self.update_history_failed(PULSE2_PSERVER_GETFILEURIFROMPACKAGE_ERROR,
                                           '',
                                           "%s\n%s" % (self.cmd.package_id, mirror))
                # the getFilesURI call failed on the only mirror we have. We have a serious
                # problem and we better decrement attempts
                return self.switch_phase_failed(True)
            else:
                # Use the fallback mirror
                self.logger.warn("Circuit #%s: can't get files URI from mirror %s, trying with fallback mirror %s" % (self.coh.getId(), mirror, fbmirror))
                return self._cbRunPushPullPhaseTestFallbackMirror(None, mirror, fbmirror, client)
            return

        client['protocol'] = file_uris['protocol']
        files_list = file_uris['files']

        # upload starts here
        if self.config.mode == 'sync':
            self.update_history_in_progress()
            mydeffered = self.launchers_provider.sync_remote_pull(self.coh.getId(),
                                                             client,
                                                             files_list,
                                                             self.config.max_upload_time
                                                             )

            mydeffered.\
                addCallback(self.parsePullResult).\
                addErrback(self.parsePullError).\
                addErrback(self.got_error_in_error)
        elif self.config.mode == 'async':
            mydeffered = self.launchers_provider.async_remote_pull(self.coh.getId(),
                                                              client,
                                                              files_list,
                                                              self.config.max_upload_time
                                                              )


            mydeffered.\
                addCallback(self.parsePullOrder).\
                addErrback(self.parsePullError).\
                addErrback(self.got_error_in_error)
        else:
            return self.give_up()
        return mydeffered

    @launcher_proxymethod("completed_push")
    def parsePushResult(self, (exitcode, stdout, stderr)):

        if exitcode == PULSE2_SUCCESS_ERROR: # success
            self.logger.info("Circuit #%s: push done (exitcode == 0)" % self.coh.id)
            self.update_history_done(exitcode, stdout, stderr)
            if self.phase.switch_to_done():
                return self.next()
            return self.give_up()
        else: # failure: immediately give up
            self.logger.info("Circuit #%s: push failed (exitcode != 0)" % self.coh.id)
            self.update_history_failed(exitcode, stdout, stderr)
            return self.switch_phase_failed()


    @launcher_proxymethod("completed_pull")
    def parsePullResult(self, (exitcode, stdout, stderr), id=None):

        proxy_coh_id = self.coh.getUsedProxy()
        if proxy_coh_id:
            proxy = CoHQuery(proxy_coh_id)
            proxy_uuid = proxy.target.getUUID()
            # see if we can unload a proxy
            # no ret val
            LocalProxiesUsageTracking().untake(proxy_uuid, self.cmd.getId())
            self.logger.debug("scheduler %s: coh #%s used coh #%s as local proxy, releasing one slot (%d left)" % (self.config.name,
                    self.coh.id, proxy_coh_id, LocalProxiesUsageTracking().how_much_left_for(proxy_uuid, self.cmd.getId())))

        if exitcode == PULSE2_SUCCESS_ERROR: # success
            self.logger.info("Circuit #%s: pull done (exitcode == 0)" % self.coh.id)
            self.update_history_done(exitcode, stdout, stderr)
            if self.phase.switch_to_done():
                return self.next()
            return self.give_up()
        else: # failure: immediately give up
            self.logger.info("Circuit #%s: pull failed (exitcode != 0)" % self.coh.id)
            self.update_history_failed(exitcode, stdout, stderr)
            return self.switch_phase_failed()


    def parsePushOrder(self, taken_in_account):
        return self.parse_order("push", taken_in_account)

    def parsePullOrder(self, taken_in_account):
        return self.parse_order("pull", taken_in_account)


    def parsePushError(self, reason, decrement_attempts_left = False, error_code = PULSE2_UNKNOWN_ERROR):
        """
        decrement_attempts_left : by default do not decrement tries as the error
        has most likeley be produced by an internal condition
        error_code : by default we consider un unknwo error was raised (PULSE2_UNKNOWN_ERROR)
        """
        self.logger.warn("Circuit #%s: push failed, unattented reason: %s" % (self.coh.id, reason.getErrorMessage()))
        if self.coh == None:
            return self.give_up()
        self.update_history_failed(error_code, '', reason.getErrorMessage())
        return self.switch_phase_failed(decrement_attempts_left)

    def parsePullError(self, reason, decrement_attempts_left = False, error_code = PULSE2_UNKNOWN_ERROR):
        """
           decrement_attempts_left : by default do not decrement tries as the error has most likeley be produced by an internal condition
           error_code : by default we consider un unknwo error was raised (PULSE2_UNKNOWN_ERROR)
        """
        # something goes really wrong: immediately give up
        self.logger.warn("Circuit #%s: pull failed, unattented reason: %s" %
                (self.coh.id, reason.getErrorMessage()))

        proxy_coh_id = self.coh.getUsedProxy()
        if proxy_coh_id:
            proxy = CoHQuery(proxy_coh_id)
            proxy_uuid = proxy.target.getUUID()
            # see if we can unload a proxy
            # no ret val
            LocalProxiesUsageTracking().untake(proxy_uuid, self.cmd.getId())
            self.logger.debug("scheduler %s: coh #%s used coh #%s as local proxy, releasing one slot (%d left)" % (self.config.name,
                    self.coh.id, proxy_coh_id,
                    LocalProxiesUsageTracking().how_much_left_for(proxy_uuid,
                        self.cmd.getId())))

        self.update_history_failed(error_code, '', reason.getErrorMessage())
        return self.switch_phase_failed(decrement_attempts_left)



# ---------------------------- EXECUTE ------------------------------
class ExecutionPhase(RemoteControlPhase):
    name = "execute"

    def get_filelist(self):
        ret = ' '.join([self.cmd.start_file, self.cmd.parameters]).strip()
        return ret or " "

    def apply_initial_rules(self):
        ret = self._apply_initial_rules()
        if not self.cmd.hasSomethingToExecute():
            self.logger.info("Circuit #%s: Nothing to execute" % self.coh.id)
            self.phase.set_done()
            return self.next()
        if self.cmd.hasToUseProxy():
            cohq = CoHQuery(self.coh.id)
            if not self.dispatcher.local_proxy_may_continue(cohq):
                self.logger.info("Circuit #%s: execution postponed, waiting for some clients" % self.coh.id)
                if not self.isStateStopped():
                    self.coh.setStateScheduled()
        if ret not in (DIRECTIVE.NEXT,
                       DIRECTIVE.GIVE_UP,
                       DIRECTIVE.KILLED,
                       DIRECTIVE.STOPPED,
                       DIRECTIVE.OVER_TIMED) :
            return self._switch_on()
        return ret

    def get_remote_command(self):

        if self.config.mode == "sync":
            if self.cmd.isQuickAction():
                return "sync_remote_quickaction"
            else :
                return "sync_remote_exec"

        elif self.config.mode == 'async':
            if self.cmd.isQuickAction():
                return "async_remote_quickaction"
            else :
                return "async_remote_exec"


    @launcher_proxymethod("completed_execution")
    def parseExecutionResult(self, (exitcode, stdout, stderr)):
        return self.parse_remote_phase_result((exitcode, stdout, stderr))

    @launcher_proxymethod("completed_quick_action")
    def parseQuickActionResult(self, (exitcode, stdout, stderr)):
        return self.parse_remote_phase_result((exitcode, stdout, stderr))


# ---------------------------- DELETE ---------------------------------
class DeletePhase(RemoteControlPhase):
    name = "delete"

    def get_filelist(self):
        return self.cmd.getFilesList()

    def apply_initial_rules(self):
        ret = self._apply_initial_rules()
        if not self.cmd.hasSomethingToDelete():
            self.logger.info("Circuit #%s: Nothing to delete" % self.coh.id)
            self.phase.set_done()
            return self.next()

        if ret not in (DIRECTIVE.NEXT,
                       DIRECTIVE.GIVE_UP,
                       DIRECTIVE.KILLED,
                       DIRECTIVE.STOPPED,
                       DIRECTIVE.OVER_TIMED) :
            return self._switch_on()
        return ret


    def perform(self):
        if self.target.hasFileMirror() or self.target.hasHTTPMirror():
            return self._perform()
        else :
            pass
            # TODO - control also NET, FTP, NFS, SSH, RSYNC protocols



    @launcher_proxymethod("completed_deletion")
    def parseDeleteResult(self, (exitcode, stdout, stderr)):
        return self.parse_remote_phase_result((exitcode, stdout, stderr))

# --------------------------- INVENTORY --------------------------------
class InventoryPhase(RemoteControlPhase):
    name = "inventory"

    @launcher_proxymethod("completed_inventory")
    def parseInventoryResult(self, (exitcode, stdout, stderr)):#, id=None):
        return self.parse_remote_phase_result((exitcode, stdout, stderr))

#  -------------------------- REBOOT ----------------------------------
class RebootPhase(RemoteControlPhase):
    name = "reboot"

    def apply_initial_rules(self):
        ret = self._apply_initial_rules()

        if self.cmd.isPartOfABundle() and not self.dispatcher.bundles.is_last(self.coh.id):
            # there is still a coh in the same bundle that has to reboot, jump to next stage
            self.logger.info("Circuit #%s: another circuit from the same bundle will launch the reboot" % self.coh.id)
            if not self.coh.isStateStopped():
                self.coh.setStateScheduled()
            else :
                return self.give_up()

            return self.next()

        if ret not in (DIRECTIVE.NEXT,
                       DIRECTIVE.GIVE_UP,
                       DIRECTIVE.KILLED,
                       DIRECTIVE.STOPPED,
                       DIRECTIVE.OVER_TIMED) :
            return self._switch_on()
        return ret


    @launcher_proxymethod("completed_reboot")
    def parseRebootResult(self, (exitcode, stdout, stderr)):
        return self.parse_remote_phase_result((exitcode, stdout, stderr))


#  ---------------------------- HALT ----------------------------------
class HaltPhase(RemoteControlPhase):
    name = "halt"


    def apply_initial_rules(self):
        ret = self._apply_initial_rules()
        if self.cmd.isPartOfABundle() and not self.dispatcher.bundles.is_last(self.coh.id):
            # there is still a coh in the same bundle that has to halt, jump to next stage
            self.logger.info("Circuit #%s: another circuit from the same bundle will do the halt" % self.coh.id)
            return self.next()
        if ret == DIRECTIVE.PERFORM :
            return self._switch_on()
        return ret


    @launcher_proxymethod("completed_halt")
    def parseHaltResult(self, (exitcode, stdout, stderr)):
        return self.parse_remote_phase_result((exitcode, stdout, stderr))

class WUParsePhase(Phase):
    """
    Windows Update output parser

    This phase parses the stdout of Windows Update agent which looks
    for KB's to install.
    """
    name = "wu_parse"

    timestamp_pattern = "\d+.\d+\sO:\s"
    json_pattern = "===JSON_BEGIN===(.*?)===JSON_END==="

    def perform(self):
        self.logger.info("Circuit #%s: WU Parse phase" % (self.coh.id))
        stdout = get_history_stdout(self.coh.id, "execute")
        output = ""
        for line in stdout.split("\n"):
            match = re.search(self.timestamp_pattern, line)
            if match :
                output += line[match.end():]

        if len(output) > 0:
            re_slice = re.findall(self.json_pattern, output, re.DOTALL|re.MULTILINE)
            output = "".join(re_slice)
            self.logger.debug("WU output: %s" % output)
            try:
                parsed = json.loads(output)
            except ValueError, e:
                self.logger.warn("Circuit #%s: Cannot parse WU output: %s" % (self.coh.id, str(e)))
                self.update_history_failed(1, 'Cannot parse WU output', str(e))
                self.logger.warn("Circuit #%s: WU Parse phase failed and skipped" % (self.coh.id))
                self.update_history_failed(1, "", str(e))
                self.switch_phase_failed()
                return self.next()

            # Set OS Class id from response JSON
            if "os_class" in parsed:
                os_class = parsed['os_class']
            else:
                os_class = -1

            if "content" in parsed:
                content = parsed["content"]
                for line in content:
                    try :
                        (uuid,
                         title,
                         kb_number,
                         kb_type,
                         need_reboot,
                         request_user_input,
                         info_url,
                         is_installed) = line

                        wu = WUInjectDB()
                        wu.inject(self.target.target_uuid.replace('UUID', ''),
                                     uuid,
                                     title.encode('utf-8','replace'),
                                     kb_number.encode('utf-8','replace'),
                                     kb_type,
                                     need_reboot,
                                     request_user_input,
                                     os_class,
                                     info_url.encode('utf-8','replace'),
                                     is_installed)

                    except ValueError:
                        self.logger.warn("Incompatible format ")
                    except Exception, e:
                        self.logger.warn("WU update failed: %s" % str(e))

        self.logger.info("Circuit #%s: WU Parse phase successfully processed" % (self.coh.id))
        self.update_history_done(stdout="successfully processed")
        self.phase.set_done()
        return self.next()




# ----------------------------- DONE ------------------------------------
class DonePhase(Phase):
    name = "done"
    def run(self): return self.perform()

    def perform(self):
       self.phase.set_done()
       self.coh.setStateDone()
       self.dispatcher.bundles.finish(self.coh.id)
       return self.next()


