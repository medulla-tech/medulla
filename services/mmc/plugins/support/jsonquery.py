# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2014 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

""" JSON querying on License server """

import os
import json
import logging

from twisted.internet import reactor
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol

from twisted.web._newclient import ResponseDone
from twisted.internet.error import ConnectionRefusedError


class QueryProtocol(Protocol):
    """Protocol providing returned request """

    def __init__(self, finished):
        """
        @param finished: deferred fired when protocol is finishing
        @type finished: Deferred
        """
        self.finished = finished
        self._data = []
        self.logger = logging.getLogger()

    def dataReceived(self, data):
        """
        Handler fired when reciving the data.

        @param data: received data
        @type data: str
        """
        self._data.append(data)
        self.logger.debug("License server check - received data: %s" % str(data))


    def connectionLost(self, reason):
        """ Protocol terminated """

        if reason.check(ResponseDone):
            self.logger.debug("License server check - connection successfully closed")
            self.finished.callback(b"".join(self._data))
        else:
            self.logger.warn("License server check - connection lost: %s" % str(reason))
            self.finished.errback(reason)



class Query(object):
    """
    Provides a HTTP/JSON request to service place.

    Based on URL composed from base URL and UUID of partner,
    we get a complet customer info.
    """

    headers = {'User-Agent': ['Twisted Web Client Example'],
               'Content-type': ['text/json'],
              }

    def __init__(self, url, client_uuid, license_tmp_file, clock=reactor):
        """
        @param url: Service Place URL
        @type url: str

        @param client_uuid: customer id
        @type client_uuid: str

        @param license_tmp_file: path for caching license info
        @type license_tmp_file: str

        @param clock: used reactor (for utittests)
        @type clock: reactor
        """
        self.url = "%s/%s/" % (url, client_uuid)
        self.clock = clock
        self.license_tmp_file = license_tmp_file
        self.logger = logging.getLogger()


    def get(self, offline=False):
        """
        Gets a dictionnary containing complete customer licensing info.

        @param offline: temp file check only
        @type offline: bool

        @return: customer info
        @rtype: Deferred
        """
        if not offline:
            agent = Agent(self.clock)

            d = agent.request("GET",
                              self.url,
                              Headers(self.headers),
                              None)

            d.addCallback(self.cb_request)
            d.addErrback(self.eb_response)
            d.addCallback(self.cb_parse)
            d.addCallback(self.cache_data_into_file)

            return d

        else:
            return maybeDeferred(self.get_cached_data_from_file)



    def cb_request(self, response):
        """
        Parsing the returned content of request.

        @param response: response returned from service place
        @type response: IResponse

        @return: parsed response
        @rtype: Deferred
        """
        if response.code != 200:
            self.logger.warn("License server returns [%d] %s ... skiping" % (response.code, response.phrase))
            return None

        d = Deferred()
        protocol = QueryProtocol(d)
        response.deliverBody(protocol)

        return d

    def cb_parse(self, response):
        """
        Response JSON parsing.

        @param response: returned raw response
        @type response: str

        @return: parsed response
        @rtype: dict
        """
        if not response:
            return self.get_cached_data_from_file()

        try:
            result = json.loads(response)
            return result
        except ValueError:
            self.logger.warn("Corrupted JSON format")
            return None
        except TypeError:
            self.logger.warn("Skipping the JSON parsing")
            return None


    def eb_response(self, failure):
        """ HHTP request error handling """
        if failure.check(ConnectionRefusedError):
            self.logger.warn("Unable to contact license server")
        else :
            self.logger.warn("JSON query on license server failed: %s" % str(failure))


    def cache_data_into_file(self, data):
        """
        Each check will be cached into a temp file to have
        license info when offline.

        @param data: unparsed data to dump
        @type data: dict

        @return: forwards unchanged data
        @rtype: dict
        """
        try:
            with open(self.license_tmp_file, "w") as jsonfile:
                json.dump(data, jsonfile)
        except Exception, e:
            self.logger.warn("JSON file dump failed: %s" % str(e))
        return data


    def get_cached_data_from_file(self):
        """
        Reads the cached license info when offline.

        @return: decoded data
        @rtype: dict
        """
        if not os.path.exists(self.license_tmp_file):
            self.logger.debug("License temp file not found, skipping")
            return None

        try:
            with open(self.license_tmp_file, "r") as jsonfile:
                try:
                    self.logger.debug("Getting license info from temp file")
                    return json.load(jsonfile)

                except ValueError:
                    self.logger.warn("Corrupted JSON format in temp file")
                    return None

                except TypeError:
                    self.logger.warn("Skipping the JSON parsing from file")
                    return None

        except Exception, e:
            self.logger.warn("JSON temp file load failed: %s" % str(e))
            return None

