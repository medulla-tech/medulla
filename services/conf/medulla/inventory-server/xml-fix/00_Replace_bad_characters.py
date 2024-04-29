# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later


def xml_fix(xml):
    bad_map = {
        "\xc2\xa0": " ",
        "\x06": " ",
    }

    for key, value in list(bad_map.items()):
        xml = xml.replace(key, value)

    return xml
