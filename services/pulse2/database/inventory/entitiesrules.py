#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

class EntitiesRules:

    def __init__(self, conffile = '/etc/mmc/pulse2/inventory-server/entities-rules'):
        self.logger = logging.getLogger()
        self.conf = conffile
        self.rules = []
        self.operators = ['match']
        self._readRulesFile()

    def _readRulesFile(self):
        """
        Read the rules configuration file
        """
        self.logger.debug("Reading inventory rules file %s" % self.conf)
        for line in file(self.conf):
            try:
                entities, rule = line.split(None, 1)
                entitieslist = entities.split(',')
                if entitieslist:
                    words = rule.split()
                    prefix = 'none'
                    subexprs = []
                    while words:
                        self.logger.debug(words)
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
                                operand1 = operand1.lower()
                                if operator in self.operators:
                                    # TODO: Maybe check operand1 value
                                    if operator == 'match':
                                        # Try to compile the regexp
                                        regexp = re.compile(operand2)
                                        subexprs.append((operand1, operator, regexp))
                                    else:
                                        self.logger.error("Operator %s is not supported, skipping" % operator)
                                words = words[3:]
                    self.rules.append((entitieslist, prefix, subexprs))
            except Exception, e:
                self.logger.error("Error while reading this rule: %s" % line)
                self.logger.error(str(e))

    def printRules(self):
        self.logger.debug(self.rules)

    def _getValue(self, input, parameter):
        """
        Return the value of the given parameter from input.

        In this implementation, input must be the inventory of a computer.
        """
        # TODO for inventory server
        return None

    def compute(self, input):
        """
        Returns an entity list according to the given input and the current
        rules.
        """
        ret = []
        for entities, mainop, rules in self.rules:
            result = None
            for rule in rules:
                operand1, operator, operand2 = rule
                # Get the value of the first operand
                value = self._getValue(input, operand1)
                if value == None:
                    # No corresponding value found, we break the loop
                    self.logger.debug("No corresponding value found for operand '%s', skipping the line" % operand1)
                    break
                if operator == 'match':
                    tmpresult = operand2.match(value) != None
                else:
                    pass
                if mainop == 'none':
                    result = tmpresult
                elif mainop == 'and':
                    if not tmpresult:
                        result = False
                        # Exit AND because we have a False
                        break
                elif mainop == 'or':
                    if result != None:
                        result = result or tmpresult
                    else:
                        result = tmpresult
                else:
                    pass
            if result:
                ret.extend(entities)
        return ret
