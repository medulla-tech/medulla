# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
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
