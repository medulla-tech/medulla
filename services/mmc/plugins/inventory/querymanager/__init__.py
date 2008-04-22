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
        ret[possible] = ['list', funcGet(possible)]
    return ret
    
def query(criterion, value):
    p1 = re.compile('/')
    table, field = p1.split(criterion)
    return [getMachinesBy(table, field, value), True]

def funcGet(couple):
    if couple == 'Software/ProductName':
        def getSoftwareProductName(value = ''):
            return getValues('Software', 'ProductName')
        return getSoftwareProductName
    elif couple == 'Hardware/ProcessorType':
        def getHardwareProcessorType(value = ''):
            return getValues('Hardware', 'ProcessorType')
        return getHardwareProcessorType
    elif couple == 'Hardware/OperatingSystem':
        def getHardwareOperatingSystem(value = ''):
            return getValues('Hardware', 'OperatingSystem')
        return getHardwareOperatingSystem
