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
Classes and methods to handle archiving of computers imaging data
"""

import logging
import os.path
import shutil

from twisted.internet.threads import deferToThread

from pulse2.utils import reduceMACAddress
from pulse2.imaging.image import isPulse2Image
from pulse2.package_server.imaging.cache import UUIDCache

class Archiver:

    """
    Class for objects that archives computer imaging data.
    Also handles the case when archiving is not wanted !
    """

    ARCHIVING = '.archiving'

    def __init__(self, config, archive, computerUUID, macAddress, imageList):
        self.logger = logging.getLogger('imaging')
        self.config = config
        self.archive = archive
        self.computerUUID = computerUUID
        self.macAddress = macAddress
        self.imageList = imageList
        self.images = []
        self.archivedir = None

    def check(self):
        """
        @return: True if the computer can be archived, else False
        @rtype: bool
        """
        # Get computer folder and boot menu
        self.cfolder = os.path.join(self.config.imaging_api['base_folder'],
                               self.config.imaging_api['computers_folder'],
                               self.computerUUID)
        self.bootmenu = os.path.join(self.config.imaging_api['base_folder'],
                                self.config.imaging_api['bootmenus_folder'],
                                reduceMACAddress(self.macAddress))
        if not os.path.exists(self.cfolder):
            self.logger.error("Looks like computer %s is not registered, so it can't be archived" % self.computerUUID)
            return False
        # Build valid image list
        for image in self.imageList:
            ifolder = os.path.join(self.config.imaging_api['base_folder'],
                                   self.config.imaging_api['masters_folder'],
                                   image)
            if isPulse2Image(ifolder):
                self.images.append(ifolder)
            else:
                self.logger.error("Invalid image, won't be archived: %s" % image)
        return True

    def prepare(self):
        """
        Prepare archive creation
        """
        try:
            self.archivedir = self._prepareArchiveDirectory()
        except Exception, e:
            self.logger.error("Can't create archive directory '%s': %s"
                              % (self.archivedir, e))
            return False
        try:
            self._prepareComputerDirectories()
        except Exception, e:
            self.logger.error("Can't prepare directories to archive: %s" % e)
            return False
        try:
            self._removeComputerFromCache()
        except Exception, e:
            self.logger.error("Can't remove computer from UUID cache:" % e)
            return False
        return True

    def _prepareArchiveDirectory(self):
        """
        Prepare the directory that will be used to archive the computer data
        """
        if self.archive:
            archivedir = os.path.join(self.config.imaging_api['base_folder'],
                                      self.config.imaging_api['archives_folder'],
                                      self.computerUUID)
            i = 1
            while True:
                if not os.path.exists('%s-%d' % (archivedir, i)):
                    archivedir = '%s-%d' % (archivedir, i)
                    break
                i += 1
            self.logger.debug('Creating archive directory: %s' % archivedir)
            os.mkdir(archivedir)
            self.logger.debug('Done')
            return archivedir

    def _prepareComputerDirectories(self):
        """
        Mark the directories that will be archived, so that they can't no more
        be used by the imaging server. We append '.archiving' to the file /
        folders name.
        """
        self.logger.debug('Renaming directories')
        os.rename(self.cfolder, self.cfolder + self.ARCHIVING)
        if os.path.exists(self.bootmenu):
            os.rename(self.bootmenu, self.bootmenu + self.ARCHIVING)
        for ifolder in self.images:
            os.rename(ifolder, ifolder + self.ARCHIVING)
        self.logger.debug('Done')

    def _removeComputerFromCache(self):
        """
        Remove the computer from the UUID cache
        """
        self.logger.debug('Removing computer from cache')
        UUIDCache().delete(self.computerUUID)
        self.logger.debug('Done')

    def run(self):
        """
        Start the archiving process in another thread.

        @return: Return a deferred object resulting to True if all was fine
        @rtype: Deferred
        """
        def _run_success(result):
            self.logger.debug('Successfully archived data from UUID %s'
                              % self.computerUUID)
            return True

        def _run_error(error):
            self.logger.error('Error while archiving data from UUID %s: %s' %
                              (self.computerUUID, error))
            return False

        d = deferToThread(self._run)
        d.addCallbacks(_run_success, _run_error)
        return d

    def _run(self):
        """
        Perform computer data deletion or archival
        """
        if not self.archive:
            # No archival, delete anything
            self.logger.debug('Removing computer data')
            if os.path.exists(self.bootmenu + self.ARCHIVING):
                os.unlink(self.bootmenu + self.ARCHIVING)
            shutil.rmtree(self.cfolder + self.ARCHIVING)
            for ifolder in self.images:
                shutil.rmtree(ifolder + self.ARCHIVING)
        else:
            # Archival, move everything to the archive directory
            self.logger.debug('Moving computer data to archive directory')
            # Moving boot menu if we have one
            if os.path.exists(self.bootmenu + self.ARCHIVING):
                dst = os.path.join(self.archivedir,
                                   os.path.basename(self.bootmenu))
                shutil.move(self.bootmenu + self.ARCHIVING, dst)
            # Moving computer home
            dst = os.path.join(self.archivedir, os.path.basename(self.cfolder))
            shutil.move(self.cfolder + self.ARCHIVING, dst)
            # Moving Pulse 2 image
            for ifolder in self.images:
                dst = os.path.join(self.archivedir, os.path.basename(ifolder))
                shutil.move(ifolder + self.ARCHIVING, dst)
        self.logger.debug('Done')
