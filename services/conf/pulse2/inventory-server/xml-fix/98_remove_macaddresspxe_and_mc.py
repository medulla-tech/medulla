import logging
import re
def xml_fix(content):
    tmp = re.sub("</QUERY>.*<REQUEST>", "</QUERY></REQUEST>", content)
    tmp = re.sub("<MACADDRPXE>.*</MACADDRPXE>", "", tmp)

    return tmp
