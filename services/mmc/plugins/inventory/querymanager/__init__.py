import os
import re
import logging
from mmc.plugins.inventory import getValues, getValuesFuzzy, getValuesWhere, getValueFuzzyWhere, getMachinesBy, activate
from mmc.plugins.inventory.tables_def import PossibleQueries

activate() # erk...

def queryPossibilities():
    ret = {}
    p1 = re.compile('/')
    for type in ['list', 'double', 'halfstatic']:
        for possible in PossibleQueries().possibleQueries(type):
            ret[possible] = [type, funcGet(possible, type)]
    return ret
    
def query(criterion, value):
    p1 = re.compile('/')
    table, field = p1.split(criterion)
    return [getMachinesBy(table, field, value), True]

def funcGet(couple, type = 'list'):
    if type == 'list':
        table, col = re.compile('/').split(couple)
        def getListValue(ctx, value = '', table = table, col = col):
            if value != '':
                return getValuesFuzzy(table, col, value)
            return getValues(table, col)
        return getListValue
    elif type == 'double':
        table, col = re.compile('/').split('Software/ProductName')
        def getListValue(ctx, value = '', table = table, col = col):
            if value != '':
                return getValuesFuzzy(table, col, value)
            return getValues(table, col)
        return getListValue
    elif type == 'halfstatic':
        table, col, val = re.compile('/').split(couple)
        logging.getLogger().info('funcGet halfstatic:')
        dummy, f, v = PossibleQueries().possibleQueries('halfstatic')[couple]
        logging.getLogger().info("%s - %s" % (f,v))
        def getListValue(ctx, value = '', table = table, col = col, f = f, v = v):
            if value != '':
                return getValueFuzzyWhere(table, f, v, col, value)
            return getValuesWhere(table, f, v, col)
        return getListValue
  
