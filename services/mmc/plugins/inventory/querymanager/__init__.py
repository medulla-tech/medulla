import os
import re
import logging
from mmc.plugins.inventory import getValues, getMachinesBy, activate

activate() # erk...

def possibleQueries():
    return ['Software/ProductName', 'Hardware/ProcessorType', 'Hardware/OperatingSystem']

def queryPossibilities():
    ret = {}
    p1 = re.compile('/')
    for possible in possibleQueries():
        table, field = p1.split(possible)
        ret[possible] = ['list', getValues(table, field)]
    return ret
    
def query(criterion, value):
    p1 = re.compile('/')
    table, field = p1.split(criterion)
    return [getMachinesBy(table, field, value), True]

