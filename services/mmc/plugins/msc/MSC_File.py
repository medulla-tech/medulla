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
import re
import os
from config import DEFAULT_MIME, LINUX_SEPARATOR, WINDOWS_SEPARATOR, CYGWIN_WINDOWS_ROOT_PATH
from utilities import escapeshellarg, clean_path
from actions import msc_ssh, msc_exec, msc_scp
import errors

class MSC_File(object):
    def __init__(self, filename, mimetypes = {'':''}):
        self.current_directory = "" #/**< the dir where is the file */
        self.size = 0               #/**< file size in octet */
        self.name = ""              #/**< file name */
        self.file_exist = False     #/**< Is the file exist ?? */
        self.extension = ""         #/**< file extension */
        self.mimetype = ""          #/**< file mime types */
        self.ctime = ""             #/**< file date */
        self.error_code = 0         #/**< Last error code (0 = no error) */

        self.content = ''           #/**< Content data of file */

        self.logger = logging.getLogger()

        self.logger.debug("__init__ - fichier : %s " % (filename))

        # * Test if filename is empty
        if len(filename) == 0:
            self.logger.debug("__init__ - ERROR_INVALIDE_FILENAME : %s" % (filename))
            self.error_code = errors.ERROR_INVALIDE_FILENAME
            return #// No return value because I'm in constructor

        # * Test if file exist
        if os.path.exists(filename):
            self.logger.debug("__init__ - File exist : %s" % (filename))
            self.file_exist = True
        else:
            self.logger.debug("__init__ - File don't exist : %s" % (filename))
            self.file_exist = False

        # * Test if file isn't a directory
        if self.file_exist and not os.path.isfile(filename):
            self.logger.debug("__init__ - It isn't a file : %s" % (filename))
            self.error_code = errors.ERROR_IS_NOT_FILE
            return #; // No return value because I'm in constructor

        # * Set file property (directory, filename ...)
        self.current_directory = os.path.dirname(filename)
        self.name = os.path.basename(filename)
        p1 = re.compile('\.')
        filepatharray = p1.split(self.name)
        self.extension = filepatharray[-1]

        #// Set mime types property
        try:
            self.mimetype = mimetypes[self.extension]
        except KeyError:
            self.mimetype = DEFAULT_MIME

        if self.file_exist:
            fileinfo = os.stat(self.current_directory+"/"+self.name)
            self.size = fileinfo.st_size
            self.ctime = fileinfo.st_ctime
            
    #/**
    # * This function read content of file
    # *
    # * The content is put in self.content member 
    # *
    # * @return False if error
    # */
    def get_content(self):
        # * Test if file exist
        if not self.file_exist:
            self.error_code = errors.ERROR_NOT_EXIST_FILE
            return False

        # * Test if file is readable
        if not os.access(self.current_directory+'/'+self.name, os.R_OK):
            self.error_code = errors.ERROR_PERMISSION
            return False

        # * Open the file
        fd = open(self.current_directory+'/'+self.name, 'r')
        
        # * Read the content
        self.logger.debug("get_content - file size = %s" % (self.size))
        if self.size > 0:
            self.content = fd.read()
        else:
            self.content = ''

        fd.close()

        #// No error
        return self.content

    #/**
    # * Old method name
    # *
    # * @see get_content
    # */
    def MSC_getContent(self):
        return self.get_content()

    #/**
    # * Write $content data in file
    # *
    # * @param $content data to write in file
    # *
    # * @return False if some error
    # */
    def write_content(self, content):
        self.logger.debug("file = %s" % (self.name))
        if not self.file_exist:
            self.create()
        
        # * Test if file is writeable
        if not os.access(self.current_directory+'/'+self.name, os.W_OK):
            self.error_code = errors.ERROR_PERMISSION
            return False

        # * Open the file in write mode
        self.logger.debug("open file %s" % (self.current_directory+'/'+self.name))
        fd = open(self.current_directory+'/'+self.name, 'w')

        # * Write the content
        self.content = content
        self.size = len(content)
        self.logger.debug("write %s in %s" % (self.content, self.name))
        fd.write(self.content)
        fd.close()

        #// No error
        return True

    #/**
    # * Old method name
    # *
    # * @see write_content method
    # */
    def MSC_writeContent(self, content):
        return self.write_content(content)

    #/**
    # * Download file to browser
    # *
    # * @return False if some error else exit the script (use exit() function)
    # */
    def download(self):
        #* Test if file is readable
        if not os.access(self.current_directory+'/'+self.name, os.R_OK):
             self.error_code = errors.ERROR_PERMISSION
             return False

        file = open(self.current_directory+"/"+self.name, 'r')

        return {
            'Content-type:':self.mimetype,
            'Content-length:':self.size,
            'Content-disposition:':'inline; filename="'+self.name+'"',
            'content':file.read()
        }

    #/**
    # * Old method name
    # *
    # * @see download method
    # */
    def MSC_download(self):
        return self.download()

    #/**
    # * Download distant file to local host (server LRS)
    # *
    # * @param $session mmc.plugins.msc.session.Session() class connected to distant host
    # * @param $path_source full filename (path and filename) on distant host to download
    # *
    # * @return False if some errors
    # */
    def download_to_local_host(self, session, path_source):
        # * Test if file exist
        if not self.file_exist:
            self.error_code = errors.ERROR_NOT_EXIST_FILE
            return False

        # * Execute the command
        ret = msc_scp(
            session.user,
            session.ip,
            path_source,
            self.current_directory + '/' + self.name
        )

        scp_command = ret[0]
        output = ret[1]
        return_var = ret[2]
        stdout = ret[3]
        stderr = ret[4]

        # * Test if error
        if return_var != 0:
            self.error_code = errors.ERROR_GET_ON_LOCAL_HOST
            return False

        return True

    #/**
    # * Old method name
    # *
    # * @see get_on_local_host
    # */
    def MSC_getOnLocal(self, session, path_source):
        return self.download_on_local_host(session, path_source)

    #/**
    # * Create a file 
    # *
    # * @return False if some error
    # *
    # * "touch" command is used to create the file.
    # */
    def create(self):
        self.logger.debug("MSC_File - filename : %s/%s" % (self.current_directory, self.name))

        # * Test if file exist
        if self.file_exist:
            self.error_code = errors.ERROR_CREATE_FILE
            return False

        # * Make command
        cmd = "touch "+escapeshellarg("/"+self.current_directory+"/"+self.name)+";"
        cmd+= "chmod ugo+rwx "+escapeshellarg("/"+self.current_directory+"/"+self.name)+""

        # * Execute command
        ret = msc_exec(cmd)
        output = ret[0]
        return_var = ret[1]
        stdout = ret[2]
        stderr = ret[3]

        # * Test error
        if return_var != 0:
            self.error_code = errors.ERROR_UNKNOWN
            return False

        #// No error
        return True

    #/**
    # * Old method name
    # *
    # * @see create
    # */
    def MSC_create(self, session):
        return self.create(session)

    #/**
    # *
    # * @param $session
    # *
    # * @return False if error
    # */
    def remove(self):
        self.logger.debug("MSC_File - %s " % (self.name))
        # * Test if file exist
        if not self.file_exist:
            self.logger.debug("MSC_File - error, I can't remove file    : %s " % (self.name))
            self.error_code = errors.ERROR_CAN_NOT_REMOVE_FILE
            return False

        # * Make command
        remove_command = "rm \"%s/%s\"" % (self.current_directory, self.name)
        self.logger.debug("MSC_File - remove_command = %s " % (remove_command))

        # * Execute command
        ret = msc_exec(remove_command)
        output = ret[0]
        return_var = ret[1]
        stdout = ret[2]
        stderr = ret[3]

        if return_var != 0:
            self.logger.debug("MSC_File - ERROR REMOVE FILE : %s " % (self.name))
            self.error_code = errors.ERROR_REMOVE_FILE
            return False

        #// Set file_exist to False
        self.file_exist = False

        #// No error
        return True

    #/** 
    # * Old method name
    # *
    # * @see MSC_remove
    # */
    def MSC_rm(self, session):
        return self.remove(session)

    #/**
    # * Rename the filename
    # *
    # * @param $new_name is the new file name value
    # *
    # * @return False if some error
    # */
    def rename(self, new_name):
        # * Test if name exist
        if not self.file_exist:
            self.error_code = errors.ERROR_DELETE_FILE
            return False

        # * Make command
        move_command = "mv \"%s/%s\" \"%s/%s\"" % (self.current_directory, self.name, self.current_directory, new_name)

        # * Execute command
        ret = msc_exec(move_command)
        output = ret[0]
        return_var = ret[1]
        stdout = ret[2]
        stderr = ret[3]

        if return_var != 0:
            self.error_code = errors.ERROR_RENAME_FILE
            return False

        # * Update name with new name
        self.name = new_name

        #// No error
        return True

    #/**
    # * Old method name
    # *
    # * @see rename method
    # */
    def MSC_rename(self, session, to):
        return self.rename(to)

    #/**
    # * Execute the file 
    # *
    # * @return array like this :
    # *
    # * <pre>
    # *    array(
    # *        "stdout" => ...,
    # *        "stderr" => ...,
    # *        "exit_code" => ...
    # *    )
    # * </pre>
    # *
    # * @warning : this work only on local host
    # */
    def execute(self):
        # * Test if name exist
        if not self.file_exist:
            self.error_code = errors.ERROR_NOT_EXIST_FILE
            return False

        # * Make command
        execute_file = "%s/%s" % (self.current_directory, self.name)

        # * Execute the file
        ret = msc_exec(execute_file)
        output = ret[0]
        return_var = ret[1]
        stdout = ret[2]
        stderr = ret[3]

        if return_val != 0:
            self.error_code = errors.ERROR_I_CAN_NOT_EXECUTE_FILE
            return { "stdout":"", "stderr":output, "exit_code":return_val }
        else:
            return { "stdout":"", "stderr":output, "exit_code":return_val }

    #/**
    # * Upload to file (Work only on local file)
    # *
    # * @param $file_to_upload
    # *
    # * This is easy, it's cp from $file_to_upload to file of class
    # */
    def upload(self, file_to_upload):
        self.logger.debug("MSC_File - file to upload is : %s" % (file_to_upload))
        # * Test if file to upload exist
        if not os.path.exists(file_to_upload):
            self.error_code = errors.ERROR_FILE_TO_UPLOAD_NOT_EXIST
            return False

        # * Make command
        upload_command = "cp "+escapeshellarg(file_to_upload)+" "+escapeshellarg(clean_path("/"+self.current_directory+"/"+self.name))+";"
        upload_command+= "chmod ugo+rwx "+escapeshellarg(clean_path("/"+self.current_directory+"/"+self.name))
        
        # * Upload the file
        self.logger.debug("MSC_File - command to execute : %s" % (upload_command))
        ret = msc_exec(upload_command)
        output = ret[0]
        return_var = ret[1]
        stdout = ret[2]
        stderr = ret[3]

        if return_var != 0:
            self.logger.debug("MSC_File - ERROR : I can not upload : %s" % (file_to_upload))
            self.error_code = errors.ERROR_I_CAN_NOT_UPLOAD_FILE
            return { "stdout":"", "stderr":output, "exit_code":return_var }
        else:
            self.logger.debug("MSC_File - file upload with success")
            return { "stdout":"", "stderr":output, "exit_code":return_var }

#/**
# * Class to handle distant file
# *
# * @see MSC_File
# */
class MSC_Distant_File(MSC_File):

    #/**
    # * It's the constructor of MSC_Distant_File.
    # *
    # * @param $session (MSC_Session class instance) is connection to host where is the file
    # * @param $filename The filename about to work.
    # *
    # * @warning This class use this global variable : mime_types_data.\n
    # * Use MSC_load_mime_type to get this variable.
    # *
    # * @see MSC_load_mime_type
    # * @see MSC_File
    # */
    def __init__(self, session, filename):
        self.logger = logging.getLogger()
        self.logger.debug("filename = %s" % (filename))
        self.session = session
        self.distant_directory = os.path.dirname(filename)
        self.MSC_File(clean_path("%s/%s/%s" % (session.sshfs_mount, session.root_path, filename)))

    #/**
    # * Execute the file 
    # *
    # * @return array like this :
    # *
    # * <pre>
    # *    array(
    # *        "stdout" => ...,
    # *        "stderr" => ...,
    # *        "exit_code" => ...
    # *    )
    # * </pre>
    # *
    # * @warning : this work only on distant file
    # */
    def execute(self):
        # * Test if name exist
        if not self.file_exist:
            self.error_code = errors.ERROR_NOT_EXIST_FILE
            return False

        execute_file_over_ssh = "%s/%s/%s" % (self.session.root_path, self.distant_directory, self.name)

        self.logger.debug("MSC_File - execute_file_over_ssh = %s" % (execute_file_over_ssh))

        # * Execute the file
        ret = msc_ssh(self.session.user, self.session.ip, execute_file_over_ssh)
        command = ret[0]
        output = ret[1]
        return_var = ret[2]
        stdout = ret[3]
        stderr = ret[4]
        
        if return_val != 0:
            self.error_code = errors.ERROR_I_CAN_NOT_EXECUTE_FILE
            return { "stdout":"", "stderr":"<br />".join(output), "exit_code":return_val }
        else:
            return { "stdout":"<br />".join(output), "stderr":"", "exit_code":return_val }

    # beacuse fucking acl depends other acl...
    # Full controle = Write, Execute, ....
    # perhaps more dependencies later...
    def MSC_setAclDepSimple(self, key, tab):
        if key == "F":
            tab["W"] = 1
            tab["D"] = 1
            tab["X"] = 1
            tab["R"] = 1
        return tab

    #/**
    # * Set all ACLs
    # * $ar_mods is a tab with mods tu set :
    # * array (
    # *        "user" => array (
    # *             "mod",
    # *                "..."),
    # *        "..."
    # *         )
    # *'mod'is the lettre use by fileacl + _ + deny/accept
    # * ex : F_accept, We_deny
    # */
    def set_acls(self, ar_mods):
        if self.session.platform != "Windows":
            return False

        cmd = "cd "+escapeshellarg(clean_path(CYGWIN_WINDOWS_ROOT_PATH+"/"+self.distant_directory+"/"))+";"
        for user in ar_mods:
            mods = ar_mods[user]
            
            cmd += "fileacl.exe "+escapeshellarg(self.name)+" /S "+escapeshellarg(user)+":U"+";"
            cmda = "fileacl.exe "+escapeshellarg(self.name)+" /S "+escapeshellarg(user)+":"
            cmdb = "fileacl.exe "+escapeshellarg(self.name)+" /D "+escapeshellarg(user)+":"
            l = len(cmdb)
            for mod in mods:
                c = mod[0:mod.index('_')]
                d = mod[mod.index('_')+1:-1]+mod[-1]
                if d == "accept":
                    cmda += c
                if d == "deny":
                    cmdb += c
            cmd += cmda + ";" + cmdb + ";"
        
        ret = msc_ssh(self.session.user, self.session.ip, cmd)
        command = ret[0]
        output = ret[1]
        return_var = ret[2]
        stdout = ret[3]
        stderr = ret[4]
        
        if return_var != 0:
            return -1

        return 0

    #/**
    # * This function return acls values the file
    # * 
    # * @param
    # * $opt is /SIMPLE or /ADVANCED (see fileacl)
    # */
    def get_acls(self):
        all_rights = ["Rr", "Ra", "Re", "Wa", "We", "Ww", "D", "Dc", "X", "A", "O", "U", "R", "W", "P", "p", "F"]
        if self.session.platform != "Windows":
            return -1
            
        cmd = "cd "+escapeshellarg(clean_path(CYGWIN_WINDOWS_ROOT_PATH+"/"+self.distant_directory+"/"))+";"
        cmd += "fileacl.exe "+escapeshellarg(self.name)+" /SIMPLE"

        ret = msc_ssh(self.session.user, self.session.ip, cmd)
        command = ret[0]
        output = ret[1]
        return_var = ret[2]
        stdout = ret[3]
        stderr = ret[4]

        for line in output:
            stat = "ACCEPT"
            path = line[0:line.index(';')]

            p1 = re.compile(':')
            ret = p1.split(line[line.index(';')+1:-1]+line[-1])
            usera = ret[0]
            mods = ret[1]
            inherit = ret[2]

            if usera.index('DENY!') >= 0:
                usera = usera[len('DENY!')-1]+usera[-1]
                stat = "DENY"
            
            user = usera[usera.index('\\'):usera.index('\\')+1] # TODO !!!!
            if user == False:
                user = usera

            if not type(tab[user]['ACCEPT']) == list:
                tab[user]['ACCEPT'] = []

            if not type(tab[user]['DENY']) == list:
                tab[user]['DENY'] = []

            for l in range(len(mods)):
                if l < len(mods):
                    cur = mods[l]+mods[l+1]
                    if all_rights.contains(cur):
                        tab[user][stat][cur] = 1
                        tab[user][stat] = self.MSC_setAclDepSimple(cur, tab[user][stat])
                        continue
                cur = mods[l]
                if all_rights.contains(cur):
                    tab[user][stat][cur] = 1
                    tab[user][stat] = self.MSC_setAclDepSimple(cur, tab[user][stat])

        return tab


    #/**
    # * get attrib of the file (A, H, S, R)
    # */
    def get_attribs(self):
        if self.session.platform != "Windows":
            return False
            
        cmd ="cd "+escapeshellarg(clean_path(CYGWIN_WINDOWS_ROOT_PATH+"/"+self.distant_directory+"/"))+";"
        cmd += "attrib.exe "+escapeshellarg(self.name)

        ret = msc_ssh(self.session.user, self.session.ip, cmd)
        command = ret[0]
        output = ret[1]
        return_var = ret[2]
        stdout = ret[3]
        stderr = ret[4]

        if return_var != 0:
            return -1

        attrib = output[0:8]
        ret = {}
        for i in ['A', 'R', 'S', 'H']:
            try:
                attrib.index(i)
                ret[i] = 1
            except ValueError:
                pass

        return ret

    #/**
    # * set attriv of the file
    # * $ar_attribs is :
    # */
    def set_attribs(self, array_attributes):
        # * Make command
        attrib_command = "cd "+escapeshellarg(clean_path(CYGWIN_WINDOWS_ROOT_PATH+"/"+self.distant_directory+"/"))+";"
        attrib_command += "attrib.exe "

        for attribute in array_attributes:
            switch = array_attributes[attribute]
            attrib_command += switch + attribute + " "
        attrib_command += escapeshellarg(self.name)
        # * Execute command
        ret = msc_ssh(self.session.user, self.session.ip, cmd)
        command = ret[0]
        output = ret[1]
        return_var = ret[2]
        stdout = ret[3]
        stderr = ret[4]

        # * Test error
        if return_var != 0:
            self.error_code = errors.ERROR_I_CAN_CHANGE_ATTRIBUTE_OF_FILE
            return -1

        #// No error
        return 0

    #/**
    # * Upload to file (Work on distant file)
    # *
    # * @param $file_to_upload
    # *
    # * This is scp to upload
    # */
    def upload(self, file_to_upload):
        self.logger.debug("MSC_File - file to upload is : %s" % (file_to_upload))
        # * Test if file to upload exist
        if not os.path.exists(file_to_upload):
            self.error_code = errors.ERROR_FILE_TO_UPLOAD_NOT_EXIST
            return False

        # * Upload the file
        ret = msc_scp(
            self.session.user,
            self.session.ip,
            file_to_upload,
            clean_path("/%s/%s/%s" % (self.session.root_path, self.distant_directory, self.name)),
            self.current_directory + '/' + self.name
        )

        scp_command = ret[0]
        output = ret[1]
        return_var = ret[2]
        stdout = ret[3]
        stderr = ret[4]

        if return_val != 0:
            self.logger.debug("MSC_File - ERROR : I can not upload : %s" % (file_to_upload))
            self.error_code = errors.ERROR_I_CAN_NOT_UPLOAD_FILE
            return { "stdout":"", "stderr":output, "exit_code":return_var }
        else:
            self.logger.debug("MSC_File - file upload with success")

            # * Now, I update the lufs cache (it's bad hack but useful)
            touch_command = "touch \"%s/%s\"" % (self.current_directory, self.name)

            self.logger.debug("MSC_File - command to execute : %s (used to update LUFS cache)" % (touch_command))
            ret = msc_exec(touch_command)
            output2 = ret[0]
            return_var2 = ret[1]
            stdout2 = ret[2]
            stderr2 = ret[3]

            return { "stdout":"", "stderr":output, "exit_code":return_var }

#/**
# * to send file via the POST method
# */
def MSC_fileSend(session, path):
    if session.platform == "Windows":
        path = MSC_cygpath(path, "WinToCyg", "", 1)

    p1 = re.compile(' ')
    path = p1.sub('\\ ', path)
    cmd = "scp %s %s@%s:\"%s/%s\"" % (
        _FILES['send_filename']['tmp_name'],
        session.user,
        session.ip,
        path,
        os.path.basename(_FILES['send_filename']['name'])
    )

    session.MSC_cmdAdd(cmd)
    res = session.MSC_cmdFlush("local")
    if len(res[cmd]['STDERR']) != 0:
        self.errcode = ERROR_UNKOWN #FIXME not in object! 
        return False
    return True

#/**
# * return the good separator (/ or \)
# */
def MSC_getSeparator(platform):
    if platform == "Windows":
        return WINDOWS_SEPARATOR
    return LINUX_SEPARATOR

#/**
# *
# */
def MSC_setLocalSeparator(path):
    if path[-1] != LINUX_SEPARATOR:
        path += LINUX_SEPARATOR
    return path

#/**
# * Convert path name (windows path <-> cygwin path <-> linux path)
# *
# * @param $name
# * @param $cmd this command select convertion type\n
# * Value can is :
# * <ul>
# *    <li>WinToCyg</li>
# *    <li>WinToLin</li>
# *    <li>WinToLinArray</li>
# *    <li>LinToWin</li>
# * </ul>
# * @param $mount_point
# * @param $strip
# *
# *
# */
def MSC_cygpath(name, cmd, mount_point = "", strip = 0):
    if cmd == "WinToCyg":
        if strip == 1:
            name = stripslashes(name)
        p1 = re.compile(WINDOWS_SEPARATOR)
        name = p1.sub(LINUX_SEPARATOR, name)
        name = mount_point + "/cygdrive/" + name[0].lower() + name[1:len(name)]
        return name

    if cmd == "WinToLin":
        if type(name) == list:
            name[1] = name[1].lower()
        else:
            if strip == 1:
                name = stripslashes(name)
            name = name[0].lower() + name[1:len(name)]
            p1 = re.compile(':')
            p2 = re.compile(WINDOWS_SEPARATOR)
            
            name = p2.sub(LINUX_SEPARATOR, p1.sub('', name))
            name = mount_point + LINUX_SEPARATOR + name
        return name

    if cmd == "WinToLinArray":
        p1 = re.compile(WINDOWS_SEPARATOR)
        p2 = re.compile(':')
        ar = p1.split(name)
        ar[0] = p2.sub('', ar[0].lower())
        ar.append('')
        return ar
    
    if cmd == "LinToWin":
        if mount_point:
            p1 = re.compile(mount_point + LINUX_SEPARATOR)
            name = p1.sub('', name)
        p2 = re.compile(LINUX_SEPARATOR)
        name = p2.sub(WINDOWS_SEPARATOR, name)
        if name[0] == WINDOWS_SEPARATOR:
            name = name[1:len(name)]
        name = name[0].upper() + ':' + name[1:len(name)]
        return name

#/**
# * Return parent directory ( Private function )
# *
# * @param $directory_path
# * @return parent (String)
# *
# * <strong>Example</strong>
# *
# * get_parent_directory("foo/bar/a/b") => "foo/bar/a/"
# */
def get_parent_directory(directory_path):
    try:
        position = directory_path.index('/')
        return directory_path[0:position]
    except ValueError:
        return ""

