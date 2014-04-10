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

import sys
import subprocess
from abc import ABCMeta, abstractmethod

class linuxUpdateHandler(object):
    __metaclass__ = ABCMeta
    
    platform = None
    
    def __init__(self, platform):
        self.platform = platform
    
    def runInShell(self, cmd, fatal=True, out_when_error=None):
        process = subprocess.Popen([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        
        # Check if errors or not
        if fatal and process.returncode != 0:
            sys.stdout.write(out)
            sys.stderr.write(out)
            sys.exit(process.returncode)
            
        # If out_when_error is defined, return it in case of error
        if out_when_error is not None and process.returncode != 0:
            out = out_when_error
            
        out = out.strip()
        return out, err, process.returncode
    
    @abstractmethod
    def disableNativeUpdates(self):
        pass
    
    @abstractmethod
    def showUpdateInfo(self, uuid, online=True):
        pass
    
    @abstractmethod
    def getAvaiableUpdates(self, online=True, returnResultList=False):
        pass
    
    @abstractmethod
    def installUpdates(self, uuid_list):
        pass
    
