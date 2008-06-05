import os
import re
import logging
from mmc.plugins.inventory import getValues, getValuesFuzzy, getValuesWhere, getMachinesBy, activate
from mmc.plugins.inventory.tables_def import possibleQueries

activate() # erk...

def queryPossibilities():
    ret = {}
    p1 = re.compile('/')
    for type in ['list', 'double']:
        for possible in possibleQueries()[type]:
            ret[possible] = [type, funcGet(possible, type)]
    return ret
    
def query(criterion, value):
    p1 = re.compile('/')
    table, field = p1.split(criterion)
    return [getMachinesBy(table, field, value), True]

def funcGet(couple, type = 'list'):
    if type == 'list':
        table, col = re.compile('/').split(couple)
        def getListValue(value = '', table = table, col = col):
            if value != '':
                return getValuesFuzzy(table, col, value)
            return getValues(table, col)
        return getListValue
    elif type == 'double':
        table, col = re.compile('/').split('Software/ProductName')
        def getListValue(value = '', table = table, col = col):
            if value != '':
                return getValuesFuzzy(table, col, value)
            return getValues(table, col)
        return getListValue
   
