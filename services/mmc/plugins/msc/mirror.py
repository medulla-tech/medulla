# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
PULSE2_DEPRECATED
"""

import logging

import mmc.plugins.msc
import medulla.apis.clients.mirror

## need to get a PackageApiManager, it will manage a PackageApi for each mirror
## defined in the conf file.
# class Mirror(medulla.apis.clients.mirror_api.Mirror):
# def __init__(self, url = None):
# self.logger = logging.getLogger()
# credit = ''
# if url:
# self.server_addr = url
## TODO check if that's a possibility... credit will always be empty...
# medulla.apis.clients.mirror_api.Mirror.__init__(self, credit, url)
# else:
# self.config = mmc.plugins.msc.MscConfig()

# if self.config.ma_enablessl:
# self.server_addr = 'https://'
# else:
# self.server_addr = 'http://'

# if self.config.ma_username != '':
# self.server_addr += self.config.ma_username
# credit = self.config.ma_username
# if self.config.ma_password != '':
# self.server_addr += ":"+self.config.ma_password
# credit += ":"+self.config.ma_password
# self.server_addr += "@"

# self.server_addr += self.config.ma_server+':'+str(self.config.ma_port) + self.config.ma_mountpoint

# if self.config.ma_verifypeer:
# medulla.apis.clients.mirror_api.Mirror.__init__(self, credit, self.server_addr, self.config.ma_verifypeer, self.config.ma_cacert, self.config.ma_localcert)
# else:
# medulla.apis.clients.mirror_api.Mirror.__init__(self, credit, self.server_addr)
