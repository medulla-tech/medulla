#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import os


class Find:
    def find(self, path, func, attr):
        for p in os.listdir(path):
            file = os.path.join(path, p)
            if os.path.isdir(file):
                self.find(file, func, attr)
            func(file, *attr)
