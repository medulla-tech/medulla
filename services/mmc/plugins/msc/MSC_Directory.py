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
from actions import msc_exec
from mmc.plugins.msc.errors import *

class MSC_Directory(object):
    def __init__(self, directory_path, mime_types_data = {'':''}):

        self.current_directory = ""     #/**< Full path of directory */
        self.array_files = []           #/**< This array content all element of directory (files and subdirectory) */
        self.ctime = ''
        self.error_code = 0
        self.name = ""
        self.directory_exist = False    #/**< is the directory exist ? */
        self.current_directory = directory_path
        self.logger = logging.getLogger()
        self.mime_types_data = mime_types_data
        
        #* Test if directory_path value is empty
        if not directory_path:
            self.logger.debug("ERROR : directory path name is empty")
            self.error_code = ERROR_DIRECTORY_NAME_IS_EMPTY
            return
        
        #* Test if directory exist
        if not os.path.exists(directory_path):
            self.logger.debug("Directory path not exist")
            self.directory_exist = False
        else:
            self.logger.debug("Directory path exist")
            self.directory_exist = True
        
        #* Test if file is a directory
        if self.directory_exist and not os.path.isdir(directory_path):
            self.logger.debug("Error : directory_path name isn't a directory ! It's a file")
            self.errcode = ERROR_IS_NOT_DIRECTORY
            return

        #* Scan the directory
        if self.directory_exist:
            stats = os.stat(self.current_directory)
            self.ctime = stats[9]
            self.scan()

    def scan(self):
        self.logger.debug("Start scan this directory : %s..." % (self.current_directory))
        self.array_files = []
        if not os.path.exists(self.current_directory):
            return 
            
        files = os.listdir(self.current_directory)
        files.sort()
        if files == None:
            return

        for file in files:
            # do not treat '.' and '..' files
            if file == '.' or file == '..':
                continue

            # Get the full path
            full_path_filename = os.path.realpath("%s/%s" % (self.current_directory, file))

            if os.path.isdir(full_path_filename):
                # Treat directory
                stats = os.stat(full_path_filename)
                self.array_files.append({
                    'name':file,
                    'ctime':stats[9],
                    'size':stats[6],
                    'is_directory':True
                })
            elif os.path.isfile(full_path_filename):
                # Get extension
                p1 = re.compile('\.')
                if p1.search(file):
                    filepatharray = p1.split(file)
                    extension = filepatharray[-1]
                else:
                    extension = ''
                    
                if self.mime_types_data.has_key(extension):
                    mime = self.mime_types_data[extension]
                else:
                    mime = ''

                # Treat file
                stats = os.stat(full_path_filename)
                self.array_files.append({
                    'name':file,
                    'ctime':stats[9],
                    'size':stats[6],
                    'is_directory':False,
                    'mimetype':mime,
                    'extension':extension
                })

        # Debuging informations
        self.logger.debug("Scanning finish")

    def get_parent(self):
        parent = os.dirname(self.distant_directory)
        self.logger.debug("The parent of %s directory is %" % (self.distant_directory, parent))
        return parent

    def make_directory(self):
        self.logger.debug("Start make directory")
        # Test if directory already exist
        if self.directory_exist:
            self.logger.debug("Error : Directory already exist then I can't create it")
            self.error_code = ERROR_I_CAN_NOT_CREATE_DIRECTORY_IT_ALREADY_EXIST
            return False
        
        # Make mkdir command
        mkdir_command = "mkdir -p --mode=0775 \"%s\"" % (self.current_directory)

        # Execute command
        self.logger.debug("Mkdir command is %s" % (mkdir_command))

        ret = msc_exec(mkdir_command)
        output = ret[0]
        return_val = ret[1]
        stdout = ret[2]
        stderr = ret[3]

        # Treat error
        if return_val != 0:
            self.logger.debug("Error when I create the directory\n Ouput is : %s\n Return_val is : %s" % (output, return_val))

            self.error_code = ERROR_CREATE_DIRECTORY
            return False
        else:
            self.logger.debug("Directory created with success")
        
        # No error
        return True
     
    def delete_directory(self):
        self.logger.debug("Delete directory")
        # Test if directory not exist
        if not self.directory_exist:
            self.logger.debug("Error : Directory not exist then I can't delete it")
            self.error_code = ERROR_I_CAN_NOT_REMOVE_DIRECTORY_IT_DO_NOT_EXIST
            return False
        
        # Make rm command
        rm_command = "rm -Rf \"%s\"" % (self.current_directory)

        # Execute command
        self.logger.debug("rm command is %s" % (mkdir_command))

        ret = msc_exec(rm_command)
        output = ret[0]
        return_val = ret[1]
        stdout = ret[2]
        stderr = ret[3]

        # * Treat error
        if return_val != 0:
            self.logger.debug("Error when I delete the directory\n Ouput is : %s\n Return_val is : %s" % (output, return_val))

            self.error_code = ERROR_REMOVE_DIRECTORY
            return False
        else:
            self.logger.debug("Directory deleted with success")
        
        # No error
        return True
     
    def get_directory_only(self):
        buffer = []
        for directory in self.array_files:
            if directory["is_directory"]:
                buffer.append(directory)
        return buffer
    
    def get_file_only(self):
        buffer = []
        for file in self.array_files:
            if not file["is_directory"]:
                buffer.append(file)
        return buffer
    
    def show_in_ascii(self):
        self.logger.info("File list of %s directory :" % (self.current_directory))
        for file in self.array_files:
            if file["is_directory"]:
                type = "[DIR]"
            else:
                type = "[FILE]"
        self.logger.info("%s\t%s\t\t\t%s\t%s\t%s\n" % (type, file['name'], file['ctime'], file['size'], file['mimetype']))
     
class MSC_Distant_Directory(MSC_Directory):
    def __init__(self, session, directory_path):
        self.session = session
        self.distant_directory = directory_path

        MSC_Directory.__init__(self, clean_path("%s/%s/%s" % (session.sshfs_mount, session.root_path, directory_path)))
        
