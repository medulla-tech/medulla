import logging
import re


def xml_fix(content):
    tmp = re.sub("<MACADDRPXE>.*</MACADDRPXE>", "", content)

    return tmp
