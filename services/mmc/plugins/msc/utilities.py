import re
from mmc.support.mmctools import shLaunch
import os

def addslashes(str):
    # need to check if it doesn't already exists
    p1 = re.compile("'")
    return p1.sub("\\'", str)

def escapeshellcmd(str):
    p1 = re.compile(" ")
    return str #p1.sub("\\ ", str)

def escapeshellarg(str):
    p1 = re.compile('"')
    str = p1.sub('\"', str)
    return '"'+str+'"'

def clean_path(str):
    return os.path.realpath(str)

