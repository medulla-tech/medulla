# -*- coding: utf-8; -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com/
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Write imaging configuration for computers.
Only exclude file are handled.
"""

import logging
import os.path

class ImagingComputerConfiguration:

    """
    Class that handles computer configuration
    """

    EXCLUDE_FILE = 'exclude'
    HOSTNAME_FILE = 'hostname'

    def __init__(self, config, computerUUID, menu, hostname):
        """
        @param config: the package server config
        @param computerUUID: the computer UUID
        @param menu: the computer parameters to apply
        """
        self.logger = logging.getLogger('imaging')
        self.config = config
        self.computerUUID = computerUUID
        self.hostname = hostname
        self.menu = menu
        self.exclude_opts = ''
        if 'exclude_parameters' in self.menu['target']:
            self.setExcludeParameters(self.menu['target']['exclude_parameters'])
        # else if no exclude_parameters is set, do as if there is no exclude
        # set.

    def setExcludeParameters(self, value):
        """
        Set the excluded disk:part list
        @param value: string of disk:part
        @type value: str
        """
        assert(type(value) == str)
        self.exclude_opts = value

    def write(self):
        """
        Write the exclude file
        """
        ret = True
        filename = os.path.join(self.config.imaging_api['base_folder'],
                                self.config.imaging_api['computers_folder'],
                                self.computerUUID,
                                self.EXCLUDE_FILE)
        if self.exclude_opts:
            # File must be updated
            self.logger.debug('Preparing to write exclude file for computer UUID %s into file %s' % (self.computerUUID, filename))
            try:
                fid = open(filename, 'w+b')
                fid.write(self.exclude_opts)
                fid.close()
                self.logger.debug('Succeeded')
            except Exception, e:
                self.logger.error("While writing exclude file for %s : %s" % (self.computerUUID, e))
                ret = False
        else:
            if os.path.exists(filename):
                # File must be removed
                self.logger.debug('Preparing to remove exclude file for computer UUID %s: %s' % (self.computerUUID, filename))
                try:
                    os.unlink(filename)
                    self.logger.debug('Succeeded')
                except Exception, e:
                    self.logger.error("While removing exclude file for %s : %s" % (self.computerUUID, e))
                    ret = False
            else:
                self.logger.debug('Nothing to do for the computer exclude file')

        filename = os.path.join(self.config.imaging_api['base_folder'],
                                self.config.imaging_api['computers_folder'],
                                self.computerUUID,
                                self.HOSTNAME_FILE)

        if ret :
            self.logger.debug('Preparing to write hostname file for computer UUID %s into file %s' % (self.computerUUID, filename))
            try:
                fid = open(filename, 'w+b')
                fid.write(self.exclude_opts)
                fid.close()
                self.logger.debug('Succeeded')
            except Exception, e:
                self.logger.error("While writing hostname file for %s : %s" % (self.computerUUID, e))
                ret = False
        return ret
