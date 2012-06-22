from configuration import *

VERSION = "3.0.4.90"
APIVERSION = "4:1:3"
REVISION = int("$Rev: 0$".split(':')[1].strip(' $'))

def getVersion():
    return VERSION
def getApiVersion():
    return APIVERSION
def getRevision():
    return REVISION

def activate():
    return True
