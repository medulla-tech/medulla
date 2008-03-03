# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007 Mandriva, http://www.mandriva.com/
#
# $Id$
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import logging
import os

import mmc.plugins.imaging
from mmc.support import mmctools

MMC_IMAGING_ISO_GRUBFILE = 'grub.cdrom'
MMC_IMAGING_ISO_MENUFILE = 'menu.lst'
MMC_IMAGING_ISO_BZIMAGEFILE = 'bzImage.initrd'
MMC_IMAGING_ISO_INITRDFILE = 'initrd.gz'
MMC_IMAGING_ISO_INITCDFILE = 'initrdcd.gz'
    
class Iso:
    def __init__(self, source, target, size):
        
        self.logger = logging.getLogger()
        self.config = mmc.plugins.imaging.ImagingConfig("imaging")
        self.source = os.path.join(self.config.publicpath, source)
        self.target = os.path.join(self.config.isopath, target)
        self.image = mmc.plugins.imaging.images.Image(source)
        self.size = size
    
    def prepareImage(self):
        if not os.path.isdir(self.config.tmppath):
            self.logger.warn("iso dir %s doesn't exist" % (self.config.tmppath))
            try:
                os.makedirs(self.config.tmppath)
            except OSError, (errno, strerror):
                self.logger.error("failed to create directory %s (c=%s: %s)" % (self.config.tmppath, errno, strerror))
                return
            self.logger.info("directory %s successfuly created" % (self.config.tmppath))

        medianumber = 0
        medialist = {}
        medialist[medianumber] = {'mediasize': 0, 'files': {}, 'opts': "-b grub.cdrom -no-emul-boot -boot-load-size 4 -boot-info-table"}

        buffer = []        
        buffer.append("color 6/0\n")
        buffer.append("default 0\n")
        buffer.append("title Local Hard Disk / Disque Dur Local\n")
        buffer.append("desc Boot on the 1st local HD\n")
        buffer.append("root (hd0)\n")
        buffer.append("chainloader +1\n")
        buffer.append("title %s\n" % self.image.title)
        buffer.append("desc %s\n" % self.image.desc)
        buffer.append("kernel (cd)/bzImage revorestorenfs revosavedir=/cdrom quiet revonospc\n")
        buffer.append("initrd (cd)/initrd\n")
        menufile = os.path.join(self.config.tmppath, MMC_IMAGING_ISO_MENUFILE)
        self.logger.info("writting boot cd menu %s" % (menufile))
        try:
            f = open(menufile, 'w')
            f.writelines(buffer)
            f.close()        
        except OSError, (errno, strerror):
            self.logger.error("failed to create boot cd menu %s (c=%s: %s)" % (menufile, errno, strerror))
            return
        self.logger.info("boot cd menu %s successfuly created" % (menufile))
        medialist[medianumber]['mediasize'] += os.stat(menufile).st_size
        medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': menufile, 'dst': "boot/grub/" + MMC_IMAGING_ISO_MENUFILE};

        grubfile = os.path.join(self.config.binpath, MMC_IMAGING_ISO_GRUBFILE)
        medialist[medianumber]['mediasize'] += os.stat(grubfile).st_size
        medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': grubfile, 'dst': 'grub.cdrom'};

        initrdfile = os.path.join(self.config.tmppath, MMC_IMAGING_ISO_INITRDFILE)
        os.system("cat %s %s > %s" % (os.path.join(self.config.binpath, MMC_IMAGING_ISO_INITRDFILE), os.path.join(self.config.binpath, MMC_IMAGING_ISO_INITCDFILE), initrdfile))
        medialist[medianumber]['mediasize'] += os.stat(initrdfile).st_size
        medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': initrdfile, 'dst': 'initrd'};

        bzimagefile = os.path.join(self.config.binpath, MMC_IMAGING_ISO_BZIMAGEFILE)
        medialist[medianumber]['mediasize'] += os.stat(bzimagefile).st_size
        medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': bzimagefile, 'dst': 'bzImage'};

        priofiles = [mmc.plugins.imaging.images.MMC_IMAGING_IMG_CONFFILE, mmc.plugins.imaging.images.MMC_IMAGING_IMG_SIZEFILE, 'PTABS', 'CONF']
        for file in priofiles:
            filepath = os.path.join(self.source, file)
            medialist[medianumber]['mediasize'] += os.stat(filepath).st_size
            medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': filepath, 'dst': file};

        for name in os.listdir(self.source):
            filepath = os.path.join(self.source, name)
            if os.path.isfile(filepath) and name not in priofiles:
                filesize = os.stat(filepath).st_size
                if medialist[medianumber]['mediasize'] + filesize > self.size:
                    medianumber += 1
                    medialist[medianumber] = {'mediasize': 0, 'files': {}, 'opts': ''}
                medialist[medianumber]['mediasize'] += filesize
                medialist[medianumber]['files'][len(medialist[medianumber]['files'])] = { 'src': filepath, 'dst': name };
        self.medialist = medialist;
        
    def createImage(self):
        if not os.path.isdir(self.config.isopath):
            self.logger.warn("iso dir %s doesn't exist" % (self.config.isopath))
            try:
                os.makedirs(self.config.isopath)
            except OSError, (errno, strerror):
                self.logger.error("failed to create directory %s (c=%s: %s)" % (self.config.isopath, errno, strerror))
                return
            self.logger.info("directory %s successfuly created" % (self.config.isopath))
        for medianumber in self.medialist:
            command = "mkisofs -f -v -v -R -V '%s' -A MMC -o '%s-%d.iso' %s -graft-points " % (self.image.title, self.target, medianumber+1, self.medialist[medianumber]['opts']);
            for file in self.medialist[medianumber]['files']:
                command += "%s=%s " % (self.medialist[medianumber]['files'][file]['dst'], self.medialist[medianumber]['files'][file]['src']);
            mmctools.shlaunchBackground(command, "Creating ISO image %s-%d.iso from image %s" % (self.target, medianumber+1, self.image.title), mmctools.progressBackup)
