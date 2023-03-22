# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
import exceptions

from twisted.internet.error import ConnectionRefusedError, ConnectionLost
from twisted.internet.error import TimeoutError

from pulse2.apis.clients import Pulse2Api
from pulse2.apis.consts import PULSE2_ERR_404, PULSE2_ERR_CONN_REF, PULSE2_ERR_UNKNOWN
from pulse2.apis.consts import PULSE2_ERR_LOST, PULSE2_ERR_TIMEOUT

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
class Mirror(Pulse2Api):

    errorback = None

    def __init__(self, base_mirror, fb_mirror=None):
        self.name = "Mirror"
        credentials, mirror = self.extractCredentials(base_mirror)
        if fb_mirror :
            Pulse2Api.__init__(self, credentials, fb_mirror)
        else :
            Pulse2Api.__init__(self, credentials, mirror)


    def extractCredentials(self, mirror):
        if not '@' in mirror:
            return ('', mirror)
        mirror = mirror.replace('http://', '')
        credentials, mirror = mirror.split("@")
        return (credentials, 'http://%s'%mirror)

    def convertMachineIntoH(self, machine):
        if type(machine) != dict:
            machine = {'uuid':machine}
        return machine

    def isAvailable(self, pid):
        """ Is my package (identified by pid) available ? """
        d = self.callRemote("isAvailable", pid)
        if self.errorback :
            d.addErrback(self.errorback)
        d.addErrback(self.ebDefault, "Mirror:isAvailable", pid)
        return d

    def getFileURI(self, fid):
        """ convert from a fid (File ID) to a file URI """
        d = self.callRemote("getFileURI", fid)
        if self.errorback :
            d.addErrback(self.errorback)
        d.addErrback(self.ebDefault, "Mirror:getFileURI", fid)
        return d

    def getFilesURI(self, fids):
        """ convert from a list of fids (File ID) to a list of files URI """
        d = self.callRemote("getFilesURI", fids)
        if self.errorback :
            d.addErrback(self.errorback)
        d.addErrback(self.ebDefault, "Mirror:getFilesURI", fids)
        return d

    def ebDefault(self, error, funcname, args, default_return = []):
        """
        To use as a deferred error back

        @returns: a list containing error informations
        @rtype: list
        """
        if error.type == ConnectionRefusedError:
            self.logger.error("%s %s has failed: connection refused" % (funcname, args))
            ret = ['PULSE2_ERR', PULSE2_ERR_CONN_REF,
                   self.server_addr, default_return]
        elif error.type == ConnectionLost:
            self.logger.error("%s %s has failed: connection lost" % (funcname, args))
            ret = ['PULSE2_ERR', PULSE2_ERR_LOST,
                   self.server_addr, default_return]
        elif error.type == TimeoutError:
            self.logger.error("%s %s has failed: timeout" % (funcname, args))
            ret = ['PULSE2_ERR', PULSE2_ERR_TIMEOUT,
                   self.server_addr, default_return]
        elif error.type == exceptions.ValueError:
            self.logger.error("%s %s has failed: the mountpoint don't exists" % (funcname, args))
            ret = ['PULSE2_ERR', PULSE2_ERR_404,
                   self.server_addr, default_return]
        else:
            self.logger.error("%s %s has failed: %s" % (funcname, args, error))
            ret = ['PULSE2_ERR', PULSE2_ERR_UNKNOWN,
                   self.server_addr, default_return]
        return ret
