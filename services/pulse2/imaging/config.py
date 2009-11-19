# -*- coding: utf-8; -*-
#
# (c) 2009 Nicolas Rueff / Mandriva, http://www.mandriva.com/
#
# $Id: config.py 4167 2009-05-19 10:15:00Z oroussy $
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


# Misc
import pulse2.utils

class ImagingConfig(pulse2.utils.Singleton):
    """
    Singleton Class to hold configuration directives
    """

    # imaging section
    base_folder = '/var/lib/pulse2/imaging'
    netboot_folder = '/var/lib/tftpboot/pulse2'

    options = {}


    def setup(self, config_file):

        self.cp = pulse2.utils.Pulse2ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option('imaging', 'base_folder'):
            self.base_folder = self.cp.get('imaging', 'base_folder')
        if self.cp.has_option('imaging', 'netboot_folder'):
            self.netboot_folder = self.cp.get('imaging', 'netboot_folder')
