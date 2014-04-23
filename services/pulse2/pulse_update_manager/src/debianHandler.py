#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2011-2012 Mandriva, http://www.mandriva.com/
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

from linuxHandler import linuxUpdateHandler

class debianUpdateHandler(linuxUpdateHandler):
    
    def disableNativeUpdates(self):
        # No need to disable
        return True
    
    def showUpdateInfo(self, uuid, online=True):
        # uuid is pkgname/version
        pkg_name = uuid.split('/')[0]
        out, err, ec = self.runInShell("apt-cache show %s" % pkg_name)
        print out
   
    def getCandidateVersion(self, pkg):
        cmd = "LANG=C apt-cache policy %s|awk '/Candidate/ { print $2 }'" % pkg
        version, err, ec = self.runInShell(cmd)
        return version
        
    def getAvaiableUpdates(self, online=True, returnResultList=False):
    
        # Init updates dict
        header = 'uuid,KB_Number,type,is_installed'.split(',')
        header_verbose = 'uuid,title,KB_Number,type,need_reboot,request_user_input,info_url,is_installed'.split(',')
        content = []
        content_verbose = []
        result = {'header' : header, 'content' : content}
        result_verbose = {'header' : header_verbose, 'content' : content_verbose}
    
        # Return OS class (debian based)
        # cat /etc/*-release|grep 'Debian\|debian' to check
        if 'debian' in self.platform:
            result_verbose['os_class'] = 4 # 4 = DEBIAN, 5 = UBUNTU ...
        elif 'ubuntu' in self.platform:
            result_verbose['os_class'] = 5 # 4 = DEBIAN, 5 = UBUNTU ...
        # TODO: Implement all debian derivatives
    
        # ===============================================================================
        # Running apt-get update
        self.runInShell("apt-get update")
        # ===============================================================================
        
        # Running Update searching command
        cmd = "LANG=C apt-get -s dist-upgrade | awk '/^Inst/ { print $2 }'"
        out, err, ec = self.runInShell(cmd)
        
        if out:
            new_packages = out.strip().split('\n')
        else:
            new_packages = []
        
        if returnResultList:
            return new_packages
    
        # Formatting output dict
        for pkg in new_packages:
            
            # Get repository package version
            version = self.getCandidateVersion(pkg)
                
            # If no version got, skipping
            if not version:
                continue
    
            # Setting package infos
            update_uuid = pkg + "/" + version
            
            _item = []
            _item_verbose = []
    
            # UUID (for debian based distros it is pkg_name/version)
            _item.append(update_uuid)
            _item_verbose.append(update_uuid)
    
            # Title
            cmd = "apt-cache show %s|awk '/^Description/ {first = $1; $1 = \"\"; print $0;}' | sed 's/^[[:space:]]*//'" % pkg
            title, err, ec = self.runInShell(cmd, False, pkg)
            _item_verbose.append('%s (update %s)' % (title.split('\n')[0], version)) #.encode('utf-8').decode('ascii', 'ignore')
    
            # Description
            #_item.append(update.Description) #.encode('utf-8').decode('ascii', 'ignore')
            #_item_verbose.append(update.Description) #.encode('utf-8').decode('ascii', 'ignore')
    
            #_item.append(update.EulaText)
            #_item_verbose.append(update.EulaText)
    
            # Kb_number (package name)
            _item.append(pkg)
            _item_verbose.append(pkg)
    
            # Type (type = 1)
            _item.append(1)
            _item_verbose.append(1)
    
            # Need reboot (doesnt need reboot)
            _item_verbose.append(False)
    
            # Request user input (False)
            _item_verbose.append(False)
    
            # Info URL
            #_item.append(fetchW32ComArray(update.MoreInfoUrls)[0])
            cmd = "apt-cache show %s|awk '/^Homepage/ {first = $1; $1 = \"\"; print $0;}' | sed 's/^[[:space:]]*//'" % pkg
            url, err, ec = self.runInShell(cmd, False, "")
            _item_verbose.append(url.split('\n')[0])
    
            # Is_installed
            _item.append(False)
            _item_verbose.append(False)
    
            content.append(_item)
            content_verbose.append(_item_verbose)
    
        return (result, result_verbose)
    
    
    def installUpdates(self, uuid_list):
        # Building package list
        pkg_list = [x.split('/') for x in uuid_list if '/' in x]
        print pkg_list
        packages_to_install = []
    
        for pkg, version in pkg_list:
            
            # Checking if package version (in repo) is the same
            if self.getCandidateVersion(pkg) != version:
                print "Skipping %s, candidate version doesn't match" % pkg
                continue
            
            # Adding update to updatesToInstall list
            print 'Adding "%s/%s" to install list' % (pkg, version)
            packages_to_install.append(pkg)
    
        if not packages_to_install:
            print "No updates to install, leaving."
            return
        
        print "Installing updates ..."
        
        # Running apt-get install
        install_cmd = "DEBIAN_FRONTEND=noninteractive UCF_FORCE_CONFFOLD=yes apt-get -y -o Dpkg::Options::=\"--force-confdef\" -o Dpkg::Options::=\"--force-confold\" install %s" % ' '.join(packages_to_install)
        print install_cmd
        out, err, ec = self.runInShell(install_cmd)
        print out
    
        return 0
