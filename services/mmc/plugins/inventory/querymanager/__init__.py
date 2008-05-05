import os
import re
import logging
from mmc.plugins.inventory import getValues, getValuesFuzzy, getValuesWhere, getMachinesBy, activate

activate() # erk...

def possibleQueries():
    return ['Software/ProductName', 'Hardware/ProcessorType', 'Hardware/OperatingSystem', 'Drive/TotalSpace']

def queryPossibilities():
    ret = {}
    p1 = re.compile('/')
    for possible in possibleQueries():
        ret[possible] = ['list', funcGet(possible)]
    ret['Software/Products'] = ['double', funcGet('Software/Products')]
    return ret
    
def query(criterion, value):
    p1 = re.compile('/')
    table, field = p1.split(criterion)
    return [getMachinesBy(table, field, value), True]

def funcGet(couple):
    if couple == 'Software/ProductName':
        def getSoftwareProductName(value = ''):
            if value != '':
                return getValuesFuzzy('Software', 'ProductName', value)
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
    elif couple == 'Software/Products':
        def getSoftwareProduct(value = ''):
            if value != '':
                return getValuesFuzzy('Software', 'ProductName', value)
            return getValues('Software', 'ProductName')
        return getSoftwareProduct
    elif couple == 'Drive/TotalSpace':
        def getDriveTotalSpace(value = 0):
            return getValues('Drive', 'TotalSpace')
        return getDriveTotalSpace
    
