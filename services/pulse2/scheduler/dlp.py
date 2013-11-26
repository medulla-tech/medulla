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

import logging

from twisted.internet.defer import DeferredList

from pulse2.apis.clients.mirror import Mirror
from pulse2.scheduler.queries import get_available_downloads

class DownloadQuery :
    """ Provides the remote queries from a DLP to the msc database """

    def __init__(self, config):
        self.logger = logging.getLogger()
        self.config = config

    def get_available_downloads(self, hostname, mac):
        """
        Checks for available packages to deploy.

        @param hostname: hostname of computer
        @type hostname: str

        @param mac: MAC address of computer
        @type mac: str

        @return: list of available download URLs
        @rtype: DeferredList
        """
        d = self._get_available_downloads(hostname, mac)
        d.addCallback(self._parse_list_result, hostname)
        return d


    def _get_available_downloads(self, hostname, mac):
        """
        Checks for available packages to deploy.

        @param hostname: hostname of computer
        @type hostname: str

        @param mac: MAC address of computer
        @type mac: str

        @return: list of available download URLs
        @rtype: DeferredList
        """
        dl = []

        for rec in get_available_downloads(self.config.name, hostname, mac):
            (coh_id, 
             target_mirrors,
             start_file,
             files,
             parameters,
             package_id) = rec

            mirrors = target_mirrors.split('||')
            # TODO - control the fallback mirrors
            ma = Mirror(mirrors[0])
            d = ma.isAvailable(package_id)
            d.addCallback(self._cb_uri_check, ma, files)
            d.addCallback(self._cb_uri_get, coh_id)
            d.addErrback(self._eb_uri)
            dl.append(d)
            
        return DeferredList(dl)

    def _parse_list_result(self, list_result, hostname):
        """
        Parsing the results from the list of deffereds.

        @param list_result: results from a list of deferreds
        @type list_result: DeferredList

        @param hostname: hostname of computer
        @type hostname: str
        """
        urls = []
        for success, result in list_result :
            if success :
                urls.append(result)
            else :
                self.logger.warn("An error occured when getting the URL of package for computer %s: %s" %
                        (hostname, result))
        return urls



    def _cb_uri_check(self, result, ma, files):
        """
        Checks the availability of a mirror.

        @param result: True if available, otherwise a error container
        @type result: bool or list

        @param ma: Mirror Api instance
        @type ma: Mirror

        @param files: list of files to deploy
        @type files: str

        @return: list of URLs to download
        @rtype: Deferred
        """
        if isinstance(result,list) and result[0] == 'PULSE2_ERR':
            self.logger.error("Mirror not available: %s" % result[3])
        else :
            fids = []
            for line in files.split("\n"):
                fids.append(line.split('##')[0])
            return ma.getFilesURI(fids)

    def _cb_uri_get(self, result, coh_id):
        """
        Receives a list of download URLs.

        @param result: list of URLs 
        @type result: list

        @param coh_id: id of circuit
        @type coh_id: int

        @return: list of URLs to download
        @rtype: Deferred
        """
 
        if isinstance(result,list) and result[0] == 'PULSE2_ERR':
            self.logger.error("URI get failed: %s" % result[3])
        else :
            urls = result
            return coh_id, urls

    def _eb_uri(self, failure):
        """ Errorback attached to get the available downloads """
        self.logger.error("Available downloads get failed: %s" % failure)
        return failure




