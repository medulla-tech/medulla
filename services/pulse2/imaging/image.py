# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com/
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
Used to read facts about an image
"""

import os
import re
import logging

# some useful constants
PULSE2_IMAGING_EXCLUDE_FNAME = 'exclude'
PULSE2_IMAGING_GRUB_FNAME = 'conf.txt'
PULSE2_IMAGING_CONF_FNAME = 'CONF'
PULSE2_IMAGING_SIZE_FNAME = 'size.txt'
PULSE2_IMAGING_LOG_FNAME = 'log.txt'
PULSE2_IMAGING_PROGRESS_FNAME = 'progress.txt'


class Pulse2Image:
    """
    This is a Pulse 2 Image
    """

    def __init__(self, directory):
        """
        Return Image stats (from conf.txt and others)
        """
        if not isPulse2Image(directory):
            return None

        self.size = 0
        self.disks = {}
        self.title = ''
        self.desc = ''
        self.logs = []
        self.has_error = False
        self.progress = 0
        self.current_part = None

        # open grub file
        try:
            fd_grub_file = open(os.path.join(directory, PULSE2_IMAGING_GRUB_FNAME))
        except Exception, e:
            logging.getLogger().error("Pulse2Image : can't read %s : %s" % (fd_grub_file, e))
            return None

        # read grub file
        for line_grub_file in fd_grub_file:
            # title line
            line_grub_file_part = re.search("^title (.*)$", line_grub_file)
            if line_grub_file_part != None:
                self.title = line_grub_file_part.group(1)

            # desc line
            line_grub_file_part = re.search("^desc (.*)$", line_grub_file)
            if line_grub_file_part != None:
                self.desc = line_grub_file_part.group(1)

            # ptabs line ?
            line_grub_file_part = re.search("^#?ptabs \(hd([0-9]+)\) ", line_grub_file)
            if line_grub_file_part != None:  # got one disk
                hd_number = int(line_grub_file_part.group(1))
                self.disks[hd_number] = {}
                self.disks[hd_number]['line'] = line_grub_file.rstrip("\n").lstrip("#")

            # hd line ?
            line_grub_file_part = re.search("^ # \(hd([0-9]+),([0-9]+)\) ([0-9]+) ([0-9]+) ([0-9]+)$", line_grub_file)
            if line_grub_file_part != None:  # got one part (first line ?)
                hd_number = int(line_grub_file_part.group(1))
                part_number = int(line_grub_file_part.group(2))
                start = int(line_grub_file_part.group(3)) * 512
                end = int(line_grub_file_part.group(4)) * 512
                l = end - start
                kind = line_grub_file_part.group(5)
                try:
                    self.disks[hd_number][part_number] = {}
                except KeyError:
                    self.disks[hd_number] = {}
                    self.disks[hd_number][part_number] = {}
                self.disks[hd_number][part_number]['start'] = start
                self.disks[hd_number][part_number]['size'] = l
                self.disks[hd_number][part_number]['kind'] = kind

            # part line ?
            line_grub_file_part = re.search("^#? partcopy \(hd([0-9]+),([0-9]+)\) ([0-9]+) PATH/", line_grub_file)
            if line_grub_file_part != None:  # got one part (second line)
                hd_number = int(line_grub_file_part.group(1))
                part_number = int(line_grub_file_part.group(2))
                self.disks[hd_number][part_number]['line'] = \
                    line_grub_file.rstrip("\n").lstrip("#")
        fd_grub_file.close()

        # open size file
        try:
            fd_size_file = open(os.path.join(directory, PULSE2_IMAGING_SIZE_FNAME))
        except Exception, e:
            logging.getLogger().error("Pulse2Image : can't read %s : %s" % (fd_size_file, e))
            return None

        for line_size_file in fd_size_file:
            line_size_file_part = re.search("^([0-9]+)", line_size_file)
            if not line_size_file_part == None:
                self.size = int(line_size_file_part.group(1)) * 1024
        fd_size_file.close()

        # open log file
        try:
            fd_log_file = open(os.path.join(directory, PULSE2_IMAGING_LOG_FNAME))
            for line_log_file in fd_log_file:
                self.logs.append(line_log_file)
                line_log_file_error = re.search("^ERROR: ", line_log_file)
                if not line_log_file_error == None:
                    self.has_error = True
            fd_log_file.close()
        except Exception, e:
            pass  # harmless

        # open progress file
        try:
            fd_prog_file = open(os.path.join(directory, PULSE2_IMAGING_PROGRESS_FNAME))
            for line_prog_file in fd_prog_file:
                line_prog_file_split = re.search("^([0-9]+): ([0-9]+)%", line_prog_file)
                if line_prog_file_split != None:
                    self.current_part = int(line_prog_file_split.group(1))
                    self.progress = int(line_prog_file_split.group(2))
            fd_prog_file.close()
        except Exception, e:
            pass  # harmless

def isPulse2Image(folder):
    """
    Return true if directory is an LRS image
    """

    if os.path.isdir(folder):
        should_contain = [
            'log.txt',
            'progress.txt',
            'CONF',
            'conf.txt',
            'size.txt']
        intersect = []
        try:
            for item in os.listdir(folder):
                if item in should_contain:
                    intersect.append(item)
            if len(intersect) == len(should_contain):
                return True
        except OSError:
            return False
    return False
