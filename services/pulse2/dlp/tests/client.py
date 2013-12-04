# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com
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
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.
"""
Mock xmlrpc client for unit tests
"""

from time import time


class TestClient:
    def __init__(self, *args, **kwargs):
        pass

    def pull_target_awake(self, hostname, mac_list):
        if hostname in ('test1', 'test2', 'test3'):
            return hostname.replace("test", "UUID")
        return False

    def get_available_commands(self, uuid):
        if uuid == "UUID1":
            return [{'id': 1,
                     'created': time(),
                     'steps': ["upload", "execute", "delete"],
                     'non_fatal_steps': ["delete", "inventory", "reboot", "halt"],
                     'urls': [''],
                     'files': ["file:///usr/bin/base64",
                               "https://www.mandriva.com/fr/static/img/mandriva-baseline-fr-FR.png",
                               "http://www.mandriva.com/en/media/uploads/logo-produit-page/pulse2-pdt-page.jpg"],
                     'package_uuid': 'd13d3eaa-587a-11e3-adfa-080027fd96ca'}]
        else:
            return [{'id': 2,
                     'created': time(),
                     'steps': ["upload", "execute", "delete"],
                     'non_fatal_steps': ["delete", "inventory", "reboot", "halt"],
                     'urls': [''],
                     'files': ["file:///usr/bin/base64",
                               "https://www.mandriva.com/fr/static/img/mandriva-baseline-fr-FR.png",
                               "http://www.mandriva.com/en/media/uploads/logo-produit-page/pulse2-pdt-page.jpg"],
                     'package_uuid': 'fbcc96e2-58fd-11e3-877e-080027fd96ca'}]

    def completed_step(self, coh_id, step_id, stdout, stderr, return_code):
        # fake server failure
        if coh_id == 2:
            return False
        return True
