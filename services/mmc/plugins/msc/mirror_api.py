# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Module to connect to the Mirror API XMLRPC API.
This api provides methods to know which package or mirror API to connect
to know package you can install on a computer.
"""

import logging
import mmc.plugins.msc
import pulse2.apis.clients.mirror_api
from mmc.support.mmctools import Singleton

# need to get a PackageApiManager, it will manage a PackageApi for each mirror
# defined in the conf file.
#class MirrorApi(Singleton):
    #initialized = False
    #def __init__(self):
        #if self.initialized: return
        #self.logger = logging.getLogger()
        #self.logger.debug("Going to initialize MirrorApi")
        #self.config = mmc.plugins.msc.MscConfig()
        #credentials = ''

        #if self.config.ma_enablessl:
            #self.server_addr = 'https://'
        #else:
            #self.server_addr = 'http://'

        #if self.config.ma_username != '':
            #self.server_addr += self.config.ma_username
            #credentials = self.config.ma_username
            #if self.config.ma_password != '':
                #self.server_addr += ":"+self.config.ma_password
                #credentials += ":"+self.config.ma_password
            #self.server_addr += "@"

        #self.server_addr += self.config.ma_server+':'+str(self.config.ma_port) + self.config.ma_mountpoint

        #if self.config.ma_verifypeer:
            #self.internal = pulse2.apis.clients.mirror_api.MirrorApi(credentials, self.server_addr, self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert)
        #else:
            #self.internal = pulse2.apis.clients.mirror_api.MirrorApi(credentials, self.server_addr)

        #for method in ('getMirror', 'getMirrors', 'getFallbackMirror', 'getFallbackMirrors', 'getApiPackage', 'getApiPackages', ):
            #setattr(self, method, getattr(self.internal, method))

        #self.initialized = True
