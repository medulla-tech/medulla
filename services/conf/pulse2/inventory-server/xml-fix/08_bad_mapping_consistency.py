# -*- coding: utf-8 -*-
def xml_fix(xml):
    bad_map = {
        "\xc2\xa0":  " ",
    }

    for key, value in bad_map.items():
        xml = xml.replace(key, value)

    return xml
