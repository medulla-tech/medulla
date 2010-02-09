# -*- coding: utf-8; -*-
#
# (c) 2010 Nicolas Rueff / Mandriva, http://www.mandriva.com/
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

"""
Configuration class for the Pulse 2 Imaging Service.
"""

# Misc
import pulse2.utils
import os.path

class ImagingConfig(pulse2.utils.Singleton):
    """
        Class which hold an imaging service configuration.
    """

    # imaging section
    base_folder = '/var/lib/pulse2/imaging'
    bootloader_folder = os.path.join(base_folder, 'bootloader')
    bootmenus_folder = os.path.join(base_folder, 'bootmenus')
    diskless_folder = os.path.join(base_folder, 'diskless')
    inventories_folder = os.path.join(base_folder, 'inventories')
    masters_folder = os.path.join(base_folder, 'masters')

    options = {}

    def setup(self, config_file):
        """
           Setup config object according to config_file content.
        """

        self.cp = pulse2.utils.Pulse2ConfigParser()
        self.cp.read(config_file)

        if self.cp.has_option('imaging', 'base_folder'):
            self.base_folder = self.cp.get('imaging', 'base_folder')
        if self.cp.has_option('imaging', 'bootloader_folder'):
            self.bootloader_folder = os.path.join(self.base_folder, self.cp.get('imaging', 'bootloader_folder'))
        if self.cp.has_option('imaging', 'bootmenus_folder'):
            self.bootmenus_folder = os.path.join(self.base_folder, self.cp.get('imaging', 'bootmenus_folder'))
        if self.cp.has_option('imaging', 'diskless_folder'):
            self.diskless_folder = os.path.join(self.base_folder, self.cp.get('imaging', 'diskless_folder'))
        if self.cp.has_option('imaging', 'inventories_folder'):
            self.inventories_folder = os.path.join(self.base_folder, self.cp.get('imaging', 'inventories_folder'))
        if self.cp.has_option('imaging', 'masters_folder'):
            self.masters_folder = os.path.join(self.base_folder, self.cp.get('imaging', 'masters_folder'))
