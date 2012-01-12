# -*- coding: utf-8; -*-
#
# (c) 2010 Mandriva, http://www.mandriva.com
#
# $Id$
#
# This file is part of Pulse 2.
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
Classes and methods related to the build of Pulse 2 ISO images.
"""

import logging
import os
import shutil
import tempfile

from twisted.internet.utils import getProcessOutputAndValue

from pulse2.imaging.image import PULSE2_IMAGING_GRUB_FNAME, PULSE2_IMAGING_SIZE_FNAME, isPulse2Image

PULSE2_IMAGING_ISO_MENUFILE = 'menu.lst'
PULSE2_IMAGING_ISO_INITRDFILE = 'initrd.gz'


class ISOImage:

    """
    Allows to prepare and create an ISO image
    """

    def __init__(self, config, imageUUID, size, title):
        """
        @param imageUUID: UUID of the Pulse 2 image to convert to an ISO
        @type imageUUID: str
        @param size: media size, in bytes
        @type size: int
        @param title: title of the image, in UTF-8
        @type title: str
        """
        self.logger = logging.getLogger('imaging')
        self.config = config
        self.source = os.path.join(self.config.imaging_api['base_folder'], self.config.imaging_api['masters_folder'], imageUUID)
        if not isPulse2Image(self.source):
            raise ValueError('Image %s is not a valid image' % imageUUID)
        self.imageUUID = imageUUID
        if not title:
            raise ValueError('Image ISO title is empty')
        self.title = title
        targetdir = self.config.imaging_api['isos_folder']
        if not os.path.isdir(targetdir):
            raise Exception("Target directory %s for ISO image doesn't exist" % targetdir)
        self.target = os.path.join(targetdir, title)
        if os.path.exists('%s-1.iso' % self.target):
            # ISO file already exists, find another file name.
            i = 1
            while True:
                if not os.path.exists('%s-%d-1.iso' % (self.target, i)):
                    self.target += '-' + str(i)
                    break
                i += 1
        self.size = int(size) # size is given as string, and we need it in B
        self.tempdir = tempfile.mkdtemp('pulse2-iso')
        self.medialist = {}

    def _makeGRUBMenu(self, medialist):
        """
        Build GRUB menu file
        FIXME: we should use menu.py to build the menu content
        """
        buf = []
        buf.append("color 6/0\n")
        buf.append("default 0\n")
        buf.append("title Local Hard Disk / Disque Dur Local\n")
        buf.append("desc Boot on the 1st local HD\n")
        buf.append("root (hd0)\n")
        buf.append("chainloader +1\n")
        buf.append("title %s\n" % self.title)
        buf.append("desc %s\n" % 'FIXME')
        buf.append("kernel (cd)/bzImage revorestorenfs revosavedir=/cdrom quiet revonospc\n")
        buf.append("initrd (cd)/initrd\n")
        menufile = os.path.join(self.tempdir, PULSE2_IMAGING_ISO_MENUFILE)
        self.logger.debug("Writing boot CD menu %s" % (menufile))
        try:
            fid = open(menufile, 'w')
            fid.writelines(buf)
            fid.close()
            self.logger.info("boot CD menu %s successfuly created" % (menufile))
        except OSError, (errno, strerror):
            self.logger.error("failed to create boot CD menu %s (c=%s: %s)" % (menufile, errno, strerror))
            raise

        medialist[0]['mediasize'] += os.stat(menufile).st_size
        medialist[0]['files'][len(medialist[0]['files'])] = {
            'src' : menufile,
            'dst' : "boot/grub/" + PULSE2_IMAGING_ISO_MENUFILE
            }

    def _makeInitrd(self, medialist):
        """
        Make the CD initrd file
        """
        initrdfile = os.path.join(self.tempdir, PULSE2_IMAGING_ISO_INITRDFILE)
        initrd = os.path.join(self.config.imaging_api['base_folder'],
                                self.config.imaging_api['diskless_folder'],
                                self.config.imaging_api['diskless_initrd'])
        initrdcd = os.path.join(self.config.imaging_api['base_folder'],
                                self.config.imaging_api['diskless_folder'],
                                self.config.imaging_api['diskless_initrdcd'])
        shutil.copy(initrd, initrdfile)
        # Read initrdcd content
        fid = file(initrdcd)
        data = fid.read()
        fid.close()
        # Append content to the initrdfile
        fid = file(initrdfile, 'ab')
        fid.write(data)
        fid.close()

        medialist[0]['mediasize'] += os.stat(initrdfile).st_size
        medialist[0]['files'][len(medialist[0]['files'])] = { 'src': initrdfile, 'dst': 'initrd'}

    def _finishMediaList(self, medialist, medianumber):
        """
        Fill the medialist dict with needed value to build the ISO image
        """

        logging.getLogger('imaging').info("Iso image : starting volumes generation, max size is %s" % (self.size))

        grubfile = os.path.join(self.config.imaging_api['base_folder'],
                                self.config.imaging_api['bootloader_folder'],
                                self.config.imaging_api['cdrom_bootloader'])
        medialist[medianumber]['mediasize'] += os.stat(grubfile).st_size
        medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': grubfile, 'dst': 'grub.cdrom'}

        bzimagefile = os.path.join(self.config.imaging_api['base_folder'],
                                   self.config.imaging_api['diskless_folder'],
                                   self.config.imaging_api['diskless_kernel'])
        medialist[medianumber]['mediasize'] += os.stat(bzimagefile).st_size
        medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': bzimagefile, 'dst': 'bzImage'}

        priofiles = [PULSE2_IMAGING_GRUB_FNAME,
                     PULSE2_IMAGING_SIZE_FNAME,
                     'PTABS',
                     'CONF']
        for fname in priofiles:
            filepath = os.path.join(self.source, fname)
            medialist[medianumber]['mediasize'] += os.stat(filepath).st_size
            medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': filepath, 'dst': fname}

        for name in os.listdir(self.source):
            filepath = os.path.join(self.source, name)
            if os.path.isfile(filepath) and name not in priofiles:
                filesize = os.stat(filepath).st_size
                if medialist[medianumber]['mediasize'] + filesize > self.size:
                    medianumber += 1
                    logging.getLogger('imaging').info("Iso image : max size of %s reached, stopping at %s and switching to volume %s" % \
                                                      (self.size, medialist[medianumber-1]['mediasize'], medianumber))
                    medialist[medianumber] = {'mediasize': 0, 'files': {}, 'opts': ''}
                medialist[medianumber]['mediasize'] += filesize
                medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': filepath, 'dst': name }
        self.medialist = medialist

    def prepare(self):
        """
        Prepare the needed files to generate the ISO file
        """
        medianumber = 0
        medialist = {}
        medialist[medianumber] = {
            'mediasize': 0,
            'files': {},
            'opts': "-b grub.cdrom -no-emul-boot -boot-load-size 4 -boot-info-table"
            }

        try:
            self._makeGRUBMenu(medialist)
            self._makeInitrd(medialist)
            self._finishMediaList(medialist, medianumber)
        except:
            # Whatever happened, remove the temporary directory
            self.removeTempDir()
            raise

    def create(self):
        """
        Generates the final ISO files.
        For now, the image are generated in background.
        """

        def _cbSuccess(result):
            out, err, code = result
            if code:
                self.logger.error('Error while generating ISO image: error code = %d' % code)
                self.logger.error('stderr: %s' % err)
                ret = False
            else:
                self.logger.debug('ISO generation succeeded')
                ret = True
            return ret

        def _cbError(result):
            out, err, signalNum = result
            self.logger.error('Signal %d received while generating ISO image' % signalNum)
            return False

        for medianumber in self.medialist:
            args = ['-f', '-v', '-v', '-R']
            # Volume ID
            args = args + ['-V', 'FIXME TITLE']
            # Application ID
            args = args + ['-A', 'Pulse 2 Imaging Server']
            # Output file
            args = args + ['-o', '%s-%d.iso' % (self.target, medianumber+1)]
            # Other options
            args = args + self.medialist[medianumber]['opts'].split()
            # Use graft points
            args = args + ['-graft-points']
            for fname in self.medialist[medianumber]['files']:
                args.append(
                    self.medialist[medianumber]['files'][fname]['dst']
                    + "="
                    + self.medialist[medianumber]['files'][fname]['src'])
            d = getProcessOutputAndValue(
                self.config.imaging_api['isogen_tool'],
                args)
            d.addCallbacks(_cbSuccess, _cbError)
            self.logger.debug("Creating ISO image %s-%d.iso from image %s" % (self.target, medianumber+1, self.imageUUID))

    def removeTempDir(self):
        """
        Remove temporary directory for ISO file generation
        """
        shutil.rmtree(self.tempdir)
