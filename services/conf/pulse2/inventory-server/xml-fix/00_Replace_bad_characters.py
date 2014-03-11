# -*- coding: utf-8 -*-
def xml_fix(xml):
    bad_map = {
        "&#160;":  " ",
    }

    for key, value in bad_map.items():
        xml = xml.replace(key, value)

    return xml
