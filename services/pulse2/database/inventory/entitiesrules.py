# -*- coding: utf-8; -*-
#
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
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

import logging
import re
import os
from mmc.site import mmcconfdir
from pulse2.utils import checkEntityName

class EntitiesRules:

    """
    Class for object that computes an inventory entity list according to a
    computer inventory and rules.
    
plugins/inventory/provisioning_plugins/network_to_entity/__init__.py:44:class NetworkRules(EntitiesRules):


    It allows the inventory server to assign a computer to an entity.
    """

    def __init__(self, conffile = mmcconfdir + '/pulse2/inventory-server/entities-rules'):
        self.logger = logging.getLogger()
        self.conf = conffile
        self.rules = []
        #self.operators = ['match']
        self.operators =["match","equal","noequal","contains","nocontains","starts","finishes"]
        self._readRulesFile()

    def _readRulesFile(self):
        """
        Read the rules configuration file
        """
        self.logger.debug("Reading inventory rules file %s" % self.conf)
        for line in file(self.conf):
            if line.startswith('#') or not line.strip():
                continue
            try:
                # The first column may contain the quoted entity list
                m = re.search('^"(.+)"\W+(.*)$', line)
                if m:
                    entities = m.group(1)
                    rule = m.group(2)
                else:
                    entities, rule = line.split(None, 1)
                entitieslist = entities.split(',')
                for entity in entitieslist:
                    checkEntityName(entity)
                if entitieslist:
                    words = rule.split()
                    prefix = 'none'
                    subexprs = []
                    while words:
                        if words[0] in ['and', 'or']:
                            if prefix == 'none':
                                prefix = words[0].lower()
                                words = words[1:]
                            else:
                                raise Exception('Different operators are not supported for a rule')
                        else:
                            if len(words) < 3:
                                raise Exception('Malformed rule')
                            else:
                                operand1, operator, operand2 = words[0:3]
                                operator = operator.lower()
                                
                                if operator in self.operators:
                                    # TODO: Maybe check operand1 value
                                    if operator == 'match':
                                        # Try to compile the regexp
                                        regexp = re.compile(operand2)
                                        subexprs.append((operand1, operator, regexp))
                                    else:
                                        subexprs.append((operand1, operator, operand2))    
                                else:
                                    self.logger.error("Operator %s is not supported, skipping" % operator)
                                words = words[3:]
                    self.rules.append((entitieslist, prefix, subexprs))
            except Exception:
                self.logger.error("Error while reading this rule: %s" % line)
                raise
   
    def reload_file_rule(self):
        self.rules = []
        self._readRulesFile()

    def printRules(self):
        self.logger.debug(self.rules)

    def _getValues(self, input, parameter):
        """
        Return the values of the given parameter from input, or an empty list
        if no value found.

        In this implementation, input must be the inventory of a computer (i.e.
        a dict with all inventory components)
        """
        ret = []
        section, option = parameter.split('/', 1)
        if section in input:
            items = input[section]
            for item in items:
                if option in item:
                    ret.append(item[option])
        return ret

    def compute(self, input):
        """
        Returns an entity list according to the given input and the current
        rules.
        """
        self.reload_file_rule()
        ret = []
        for entities, mainop, rules in self.rules:
            result = None
            for rule in rules:
                operand1, operator, operand2 = rule
                # Get the values of the first operand
                values = self._getValues(input, operand1)
                #if operand1 network/ip value tab des ips
                if values == []:
                    # No corresponding value found, we break the loop
                    self.logger.debug("No corresponding value found for operand '%s', skipping the line" % operand1)
                    break
                # Loop over all the values, and break the loop if one value
                # makes the expression returns True
                tmpresult = False
                for value in values:
                    if operator == 'match':
                        tmpresult = operand2.match(value) != None
                    elif operator == 'equal':
                        tmpresult = value == operand2
                    elif operator == 'noequal':
                        tmpresult = value != operand2
                    elif operator == 'contains':
                        tmpresult = operand2 in value
                    elif operator == 'nocontains':
                        tmpresult = not (operand2 in value)
                    elif operator == 'starts':
                        tmpresult = value.startswith( operand2 )
                    elif operator == 'finishes':
                        tmpresult = value.endswith( operand2 )
                    else:
                        pass
                    if tmpresult:
                        self.logger.info('operator [%s] %s %s %s' %(operator, values, operand2, tmpresult))
                        break

                if mainop == 'none':
                    result = tmpresult
                elif mainop == 'and':
                    if not tmpresult:
                        result = False
                        # Exit AND because we have a False
                        break
                    else:
                        result = True
                elif mainop == 'or':
                    if result != None:
                        result = result or tmpresult
                    else:
                        result = tmpresult
                else:
                    pass
            if result:
                ret = entities
                # We exit as soon as a line match
                break
        return ret


class DefaultEntityRules:

    """
    This default class assign all computers to the same entity.
    """

    def __init__(self, default_entity):
        self.entity = default_entity

    def compute(self, input):
        return [self.entity]
