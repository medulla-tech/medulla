# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
#
# $Id: config.py 4808 2009-11-23 16:04:04Z oroussy $
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
Configuration class for the imaging API
"""

import os.path
import pulse2.utils

class ImagingConfig(pulse2.utils.Singleton):

    """
    Class that reads and holds all the configuration directives for the imaging
    API.
    """

    mount_point = '/imaging'
    
    imaging_root_dir = '/var/lib/pulse2/imaging'
    mmc_agent = None
    mmc_agent_verify_peer = False
    mmc_agent_cacert = None
    mmc_agent_localcert = None
    
    def read(self, cp):
        """
        @param cp: ConfigParser object from P2PServerCP
        @type cp: ConfigParser
        """
        self.cp = cp
        if self.cp.has_option('imaging', 'mount_point'):
            self.mount_point = self.cp.get('imaging', 'mount_point')
        if self.cp.has_option('imaging', 'imaging_root_dir'):
            self.imaging_root_dir = self.cp.get('imaging', 'imaging_root_dir')
        if self.cp.has_option('imaging', 'mmc_agent'):
            self.mmc_agent = self.cp.get('imaging', 'mmc_agent')
        if self.cp.has_option('imaging', 'mmc_agent_verify_peer'):
            self.mmc_agent_verify_peer = self.cp.getbool('imaging', 'mmc_agent_verify_peer')
        if self.cp.has_option('imaging', 'mmc_agent_cacert'):
            self.mmc_agent_cacert = self.cp.get('imaging', 'mmc_agent_cacert')
        if self.cp.has_option('imaging', 'mmc_agent_localcert'):
            self.mmc_agent_localcert = self.cp.get('imaging', 'mmc_agent_localcert')

    def validate(self):
        """
        @return: True if the imaging configuration seems valid
        @rtype: bool
        """
        if not os.path.exists(self.imaging_root_dir):
            raise Exception('Path %s does not exist' % self.imaging_root_dir)
        # FIXME: More checks to add
        return True
