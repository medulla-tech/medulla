#!/usr/bin/env python
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

import json
import sys
from platform import platform
from utils import pprinttable
from collections import namedtuple

if __name__ == '__main__':
    
    # Get System Platform
    platform = platform().lower()
    
    # Init updateHandler according to system platform
    if 'debian' in platform or 'univention' in platform:
        from debianHandler import debianUpdateHandler
        updateHandler = debianUpdateHandler(platform)
    elif 'window' in platform:
        from windowsHandler import windowsUpdateHandler
        updateHandler = windowsUpdateHandler(platform)
    else:
        print 'Unsupported operating system'
        sys.exit(1)
    
    # Disabling native update service
    # ugly try, except, but not really important to continue
    try:
        if not updateHandler.disableNativeUpdates():
            print "Cannot disable Windows Update Service"
    except:
        print "Cannot disable Windows Update Service"
    
    args = sys.argv
    
    if len(args) < 2:
        print "pulse-update-manager 1.0.1"
        print "Usage : \tpulse-update-manager [options] [update_list]"
        print ""
        print "Options:"
        print "  -l, --list : List all updates available for this machine"
        print "  --offline : List mode, list cached updates (offline mode)"
        print "  --json : List mode, output in JSON format"
        print "  -i, --install : Install specified updates (uuid or kb_number)"
        print ""
        print ""
        print "Examples:"
        print "  pulse-update-manager -l --offline --json"
        print "  pulse-update-manager --install 2791765 2741517"
        sys.exit(0)
    
    command = args[1]
    
    # Specific update info
    if command == '-d' or command == '--detail':
        if (len(args) < 3):
            print "You must specify update UUID"
            sys.exit(0)
        online = not ('--offline' in args)
        updateHandler.showUpdateInfo(args[2], online)
    
    # Update install switches
    if '-i' in args or '--install' in args:
        updateHandler.installUpdates(args[1:])
    
    # Update listing switches
    if '--list' in args or '-l' in args:
        # Search all available updates
        print "Searching for updates ..."
        #
        online = not ('--offline' in args)
    
        (result, result_verbose) = updateHandler.getAvaiableUpdates(online)
    
        if '--json' in args:
            # Printing JSON
            print "===JSON_BEGIN==="
            print json.dumps(result_verbose)
            print "===JSON_END==="
        elif '--otherformat' in args:
            pass
        else:
            # Printing table
            Row = namedtuple('Row', result['header'])
            pprinttable([Row(*item) for item in result['content']])
    sys.exit(0)
