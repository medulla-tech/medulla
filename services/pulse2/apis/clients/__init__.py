# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Class to manage api calls and errors
"""

import logging

from pulse2.xmlrpc import Pulse2XMLRPCProxy
from pulse2.apis.consts import PULSE2_ERR_404, PULSE2_ERR_CONN_REF, PULSE2_ERR_UNKNOWN
from twisted.internet.error import ConnectionRefusedError


class Pulse2Api(Pulse2XMLRPCProxy):
    name = "pulse2API"

    def __init__(
        self,
        credentials,
        url="https://localhost:9990/package_api_get1",
        verifypeer=False,
        cacert=None,
        localcert=None,
    ):
        """
        @param credentials: XML-RPC HTTP BASIC credentials = login:password
        @type credentials: str
        """
        if len(str(url)) < 10:
            url = "https://localhost:9990/package_api_get1"
        else:
            url = str(url)
        url = str(url)
        Pulse2XMLRPCProxy.__init__(
            self, url, verifypeer=verifypeer, cacert=cacert, localcert=localcert
        )
        self.SSLClientContext = None
        self.logger = logging.getLogger()
        self.logger.debug("%s will connect to %s" % (self.name, url))
        self.server_addr = url
        self.credentials = credentials
        # FIXME: still needed ?
        self.initialized_failed = False

    def onError(self, error, funcname, args, default_return=[]):
        self.logger.warn(
            "%s: %s %s has failed: %s" % (self.name, funcname, args, error)
        )
        return default_return

    def onErrorRaise(self, error, funcname, args, default_return=[]):
        """
        To use as a deferred error back

        @returns: a list containing error informations
        @rtype: list
        """
        if error.type == ConnectionRefusedError:
            self.logger.error("%s %s has failed: connection refused" % (funcname, args))
            ret = ["PULSE2_ERR", PULSE2_ERR_CONN_REF, self.server_addr, default_return]
        elif error.type == exceptions.ValueError:
            self.logger.error(
                "%s %s has failed: the mountpoint don't exists" % (funcname, args)
            )
            ret = ["PULSE2_ERR", PULSE2_ERR_404, self.server_addr, default_return]
        else:
            self.logger.error("%s %s has failed: %s" % (funcname, args, error))
            ret = ["PULSE2_ERR", PULSE2_ERR_UNKNOWN, self.server_addr, default_return]
        return ret
