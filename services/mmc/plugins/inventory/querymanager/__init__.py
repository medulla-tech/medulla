#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""
QueryManager APO for inventory
"""

import re
import logging
from mmc.plugins.inventory import getValues, getValuesFuzzy, getValuesWhere, getValueFuzzyWhere, getMachinesBy, getTypeOfAttribute
from mmc.plugins.inventory.tables_def import PossibleQueries

def activate():
    return True

def queryPossibilities():
    ret = {}
    p1 = re.compile('/')
    for type in ['list', 'double', 'halfstatic']:
        for possible in PossibleQueries().possibleQueries(type):
            ret[possible] = [type, funcGet(possible, type)]
    return ret

def extendedPossibilities():
    ret = {}
    p1 = re.compile('/')
    for possible in PossibleQueries().possibleQueries('extended'):
        ret[possible] = ['extended', funcGet(possible, 'extended')]
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
        def getListValue(ctx, table, cols, value1 = '', value2 = None):
            """
            getListValue of "double" type. It's used where you search on 2 fields of a table.
            Example: On table Software, you can search on ProductName and ProductVersion

            @param table: table who will be requested
            @type table: str

            @param cols: the 2 fields of table who will be requested, it's a string separated by ":"
            @type cols: str

            @param value1: ajax search on field 1 (the first field of table)
            @type value1: str

            @param value2: ajax search on field 2 (the second field of table)
            @type value2: str
            """
            if value2 is None: # Search of possibles values of field 1
                if value1 != '':
                    return getValuesFuzzy(table, cols.split(':')[0], value1)
                return getValues(table, col)
            else: # Search of possibles values of field 2 according to field 1
                return getValueFuzzyWhere(table, cols.split(':')[0], value1, cols.split(':')[1], value2)
        return getListValue
    elif type == 'halfstatic':
        try:
            table, col, val = re.compile('/').split(couple)
            logging.getLogger().info('funcGet halfstatic:')
            dummy, f, v = PossibleQueries().possibleQueries('halfstatic')[couple]
            logging.getLogger().info("%s - %s" % (f,v))
            def getListValue(ctx, value = '', table = table, col = col, f = f, v = v):
                if value != '':
                    return getValueFuzzyWhere(table, f, v, col, value)
                return getValuesWhere(table, f, v, col)
            return getListValue
        except ValueError:
            logging.getLogger().warning("%s cant be used as a 'halfstatic' value, please check the syntax of the config file."%(couple))
            pass
    elif type == 'extended':
        # Get the table and column name from the parameter
        table, col = re.compile('/').split(couple)
        # Return the type of this column
        return getTypeOfAttribute(table, col)

