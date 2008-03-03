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
import re
import shutil
import fileinput

import mmc.plugins.imaging

MMC_IMAGING_IMG_CONFFILE = 'conf.txt'
MMC_IMAGING_IMG_SIZEFILE = 'size.txt'

class Image:
    def __init__(self, name = None, parent = None):
        self.logger = logging.getLogger()

        self.config = mmc.plugins.imaging.ImagingConfig("imaging")
        if not name:
            raise
        
        # not parent => "public image"
        if not parent:
            self.logger.info("attempt to read public image %s" % (name))
            self.parentdir = os.path.join(self.config.revopath, self.config.publicdir)
            self.path = os.path.join(self.parentdir, name)
        else:
            self.logger.info("attempt to read private image %s (parent = %s)" % (name, parent))
            self.parentdir = os.path.join(self.config.revopath, parent)
            self.path = os.path.join(self.parentdir, name)
            
        if not self.hasImagingData():
            raise "%s do not contain valid imaging data" % self.path
        
        fd_grub_file = open(os.path.join(self.path, MMC_IMAGING_IMG_CONFFILE))
        
        self.disks = {}
        
        # iterate over conf file
        for line_grub_file in fd_grub_file:
            
            # try to parse image title or image desc
            for word in ['title', 'desc']:
                line_grub_file_part = re.search("^%s (.*)$" % word, line_grub_file)
                if line_grub_file_part != None:
                    if word == 'title':
                        self.title = line_grub_file_part.group(1)
                    if word == 'desc':
                        self.desc = line_grub_file_part.group(1)
                    
            # try to parse full disk
            line_grub_file_part = re.search("^#?ptabs \(hd([0-9]+)\) ", line_grub_file)
            if line_grub_file_part != None: # got one disk
                hd_number = int(line_grub_file_part.group(1))
                self.disks[hd_number] = {}
                self.disks[hd_number]['line'] = line_grub_file.rstrip("\n").lstrip("#")
                
            # try to parse partition ?
            line_grub_file_part = re.search("^ # \(hd([0-9]+),([0-9]+)\) ([0-9]+) ([0-9]+) ([0-9]+)$", line_grub_file)
            if line_grub_file_part != None: # got one part (first line ?)
                hd_number = int(line_grub_file_part.group(1))
                part_number = int(line_grub_file_part.group(2))
                start = int(line_grub_file_part.group(3)) * 512
                end = int(line_grub_file_part.group(4)) * 512
                len = end - start
                kind = line_grub_file_part.group(5)
                try:
                    self.disks[hd_number][part_number] = {}
                except KeyError:
                    self.disks[hd_number] = {}
                    self.disks[hd_number][part_number] = {}
                self.disks[hd_number][part_number]['start'] = start
                self.disks[hd_number][part_number]['size'] = len
                self.disks[hd_number][part_number]['kind'] = kind
            
            # try to parse partition restoration line ?
            line_grub_file_part = re.search("^#? partcopy \(hd([0-9]+),([0-9]+)\) ([0-9]+) PATH/", line_grub_file)
            if line_grub_file_part != None: # got one part (second line)
                hd_number = int(line_grub_file_part.group(1))
                part_number = int(line_grub_file_part.group(2))
                self.disks[hd_number][part_number]['line'] = line_grub_file.rstrip("\n").lstrip("#")

        fd_grub_file.close()
        
        # gather image size
        fd_size_file = open(os.path.join(self.path,MMC_IMAGING_IMG_SIZEFILE))
        for line_size_file in fd_size_file:
            line_size_file_part = re.search("^([0-9]+)", line_size_file)
            if not line_size_file_part == None:
                self.size = int(line_size_file_part.group(1)) * 1024
        fd_size_file.close()
        
        self.name = name
        self.logger.info("image %s loaded" % (name))

    def __repr__(self):
        buffer = \
"""name: %s
title: %s
desc: %s
path: %s
size: %s
disks: %s
"""\
        % (self.name, self.title, self.desc, self.path, self.size, self.disks)
        return buffer
    
    def getRawInfo(self):
        myarray = {
            'name': self.name,
            'title': self.title,
            'desc': self.desc,
            'path': self.path,
            'size': self.size,
            'disks': self.disks
        }
        return myarray;
        
    def hasImagingData(self):
        """ Return true if directory is an "imaging" image
            
            FIXME: for now only tests if target is directory
        """
        
        return hasImagingData(self.path)
    
    def copy(self, newname = None, newdir = None):
        if not newname:
            return

        if not newdir:
            dst = self.parentdir
        else:    
            dst = newdir
            
        # copy from src to dst, preserv sym
        self.logger.info("attempt to copy image %s from %s to %s" % (self.name, self.path, os.path.join(dst, newname)))
        try:
            shutil.copytree(self.path, os.path.join(dst, newname), True)
        except OSError, (errno, strerror):
            self.logger.error("image %s could not be copied to %s (c=%s: %s)" % (self.name, os.path.join(dst, newname), errno, strerror))
            return
        self.logger.info("image %s successfuly copied to %s" % (self.name, os.path.join(dst, newname)))
        
        return Image(newname, dst)

    def move(self, newname = None, newdir = None):
        if not newname:
            return

        if not newdir:
            dst = self.parentdir
        else:
            dst = newdir
            
        # move from src to dst
        self.logger.info("attempt to move image %s from %s to %s" % (self.name, self.path, os.path.join(dst, newname)))
        try:
            shutil.move(self.path, os.path.join(dst, newname))
        except OSError, (errno, strerror):
            self.logger.error("image %s could not be moved to %s (c=%s: %s)" % (self.name, os.path.join(dst, newname), errno, strerror))
            return
        self.logger.info("image %s successfuly moved to %s" % (self.name, os.path.join(dst, newname)))
        
        return Image(newname, dst)
        
    def delete(self):

        self.logger.info("attempt to delete image %s from %s" % (self.name, self.path))
        try:
            shutil.rmtree(self.path)
        except OSError, (errno, strerror):
            self.logger.error("image %s could not be removed from  %s (c=%s: %s)" % (self.name, self.path, errno, strerror))
            return
        self.logger.info("image %s successfuly removed from %s" % (self.name, self.path))
        return
        
    def getConfFile(self):
        self.logger.info("getting configuration from %s" % self.name)
        f = open(os.path.join(self.path, MMC_IMAGING_IMG_CONFFILE))
        buffer = "".join(f)
        f.close()
        return buffer

    def setKey(self, key, val):
        self.logger.info("setting %s for %s" % (key, self.name))

        buffer = []
        f = open(os.path.join(self.path, MMC_IMAGING_IMG_CONFFILE))
        for line in f:
            if line.startswith("%s " % key):
                buffer.append("%s %s\n" % (key, val))
            else:
                buffer.append(line)
        f.close()

        f = open(os.path.join(self.path, MMC_IMAGING_IMG_CONFFILE), 'w')
        f.writelines(buffer)
        f.close()        

    def setTitle(self, val):
        self.setKey('title', val)

    def setDesc(self, val):
        self.setKey('desc', val)
        
def hasImagingData(path):
        if not os.path.isdir(path):
            return False
        if not os.path.isfile(os.path.join(path, MMC_IMAGING_IMG_CONFFILE)):
            return False
        if not os.path.isfile(os.path.join(path, MMC_IMAGING_IMG_SIZEFILE)):
            return False
        return True
    
def getPublicImages():
    configImaging = mmc.plugins.imaging.ImagingConfig("imaging")
    parentdir = os.path.join(configImaging.revopath, configImaging.publicdir)
    mylist = {}
    for dir in os.listdir(parentdir):
        if hasImagingData(os.path.join(parentdir, dir)):
            mylist[len(mylist)] = Image(dir)

    return mylist
