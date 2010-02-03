# -*- coding: utf-8; -*-
#
# (c) 2007-2010 Mandriva, http://www.mandriva.com
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
# along with Pulse 2.  If not, see <http://www.gnu.org/licenses/>.

"""
Contains needed classes to build and to compute boolean operation on list of
objects.
"""

import re
import logging
from random import randint
from pulse2.utils import unique
from xml.dom import minidom
from sets import Set

p1 = re.compile(' ')
p2 = re.compile(',')
p3 = re.compile('((?:AND|OR|NOT|ET|OU|NON)\([^\)\(]*\))', re.I)
p4 = re.compile('^[^\(\)]*(?=\()')
p5 = re.compile('^\(')
p6 = re.compile('\)$')
p7 = re.compile('\(')
p8 = re.compile('\)')
p9 = re.compile('^<BEID:(\d+)>$')
p10 = re.compile('(?<!^)((?:AND|OR|ET|OU)\((?P<val>[^\)\(,]*)\))', re.I)
p11 = re.compile('\n')


s2x1 = re.compile('(AND|ET)\(', re.I)
s2x2 = re.compile('(OR|OU)\(', re.I)
s2x3 = re.compile('(NOT|NON)\(', re.I)
s2x4 = re.compile(',')
s2x5 = re.compile('\)')
s2x6 = re.compile('</p>$')

class BoolRequest(object):
    def __init__(self):
        self.equ = None

    def parse(self, str):
        self.equ = BoolEquation(self.clean(str))
        logging.getLogger().debug(self.equ.toXML())

    def parseXML(self, str):
        self.equ = BoolEquation(self.clean(str), True)
        logging.getLogger().debug(self.equ.toXML())

    def clean(self, str):
        # remove ' ' for an easier parsing
        str = p1.sub('', str)
        # remove useless AND or OR
        str = p10.sub("\g<val>", str)
        # remove userless \n
        str = p11.sub('', str)
        return str

    def isValid(self):
        if self.equ == None:
            self.logger.debug("isValid: no equation")
            return False
        return self.equ.check()

    def merge(self, lists):
        logging.getLogger().debug(lists)
        return self.equ.merge(lists)

    def getTree(self, lists):
        logging.getLogger().debug(lists)
        return self.equ.getTree(lists)

    def countOps(self):
        return self.equ.count()

    def toH(self):
        return self.equ.toH()
    def toS(self):
        return self.equ.toS()
    def toXML(self):
        return "<BoolRequest>"+self.equ.toXML()+"</BoolRequest>"

# Operators ####################################
class BoolOperator(object): # abstract
    def toH(self, list):
        pass
    def toS(self, list):
        pass
    def toXML(self, list):
        pass
    def merge(self, lists):
        pass
    def getTree(self, lists):
        pass

class BoolOperatorAnd(BoolOperator):
    def toH(self, list):
        return ["AND", map(to_h, list.values())]
    def toS(self, list):
        return "AND ("+(', '.join(map(to_s, list.values())))+")"
    def toXML(self, list):
        return "<b t='AND'><p>"+('</p><p>'.join(map(to_xml, list.values())))+"</p></b>"
    def merge(self, lists):
        retour = []
        # lists = [[[entrees, 2, 3], NEG], [[entrees, 2, 3], NEG], ...]
        if len(lists) > 0:
            pos = map(lambda a:a[0], filter(lambda a:a[1], lists))
            neg = map(lambda a:a[0], filter(lambda a:not a[1], lists))

            retour = pos.pop() # TODO : pb if pos is empty ...
            for list in pos:
                retour = filter(lambda a,l=list:a in l, retour)
            for list in neg:
                retour = filter(lambda a,l=list:a not in l, retour)
        return [retour, True]
    def getTree(self, lists):
        return ['AND', lists]

class BoolOperatorOr(BoolOperator):
    def toH(self, list):
        return ["OR", map(to_h, list.values())]
    def toS(self, list):
        return "OR ("+(', '.join(map(to_s, list.values())))+")"
    def toXML(self, list):
        return "<b t='OR'><p>"+('</p><p>'.join(map(to_xml, list.values())))+"</p></b>"
    def merge(self, lists):
        retour = []
        if len(lists) > 0:
            pos = map(lambda a:a[0], filter(lambda a:a[1], lists))
            neg = map(lambda a:a[0], filter(lambda a:not a[1], lists))
            retour = pos.pop()

            for list in pos:
                for x in list:
                    retour.append(x)
            retour = unique(retour)

            for list in neg: # don't know what to do with neg values...
                pass

        return [retour, True]
    def getTree(self, lists):
        return ['OR', lists]

class BoolOperatorNot(BoolOperator):
    def toH(self, list):
        return ["NOT", map(to_h, list.values())]
    def toS(self, list):
        return "NOT ("+(', '.join(map(to_s, list.values())))+")"
    def toXML(self, list):
        return "<b t='NOT'><p>"+('</p><p>'.join(map(to_xml, list.values())))+"</p></b>"
    def merge(self, lists):
        list = lists[0]
        list[1] = not list[1]
        return list
    def getTree(self, lists):
        return ['NOT', lists]

def to_h(obj):
    return obj.toH()
def to_xml(obj):
    return obj.toXML()
def to_s(obj):
    return obj.toS()
# Elements #####################################
class BoolElement(object): # abstract
    def toH(self):
        pass
    def toS(self):
        pass
    def toXML(self):
        pass
    def merge(self, lists):
        pass
    def getTree(self, lists):
        pass

class BoolEquation(BoolElement):
    def __init__(self, str, is_xml = False):
        self.h_op = {
            'AND':BoolOperatorAnd,
            'OR':BoolOperatorOr,
            'NOT':BoolOperatorNot
        }
        self.id = randint(0, 100000)
        self.op = None
        self.list = {}
        if is_xml:
            self.parseXML(str)
        else:
            self.parse(str)

    def check(self): # ids are always in a range from 1 to count
        try:
            return Set(map(lambda x:int(x), self.getVals())) == Set(range(1,1+self.count()))
        except:
            return False

    def count(self):
        return len(self.getVals())

    def getVals(self):
        return Set(self._getVals())

    def _getVals(self):
        vals = []
        for k in self.list:
            b = self.list[k]
            if type(b) == BoolValue:
                vals.append(b.getValue())
            elif type(b) == int:
                vals.append(b)
            elif type(b) == BoolEquation:
                vals.extend(b._getVals())
            else:
                vals.extend(b._count())
        return vals

    def parseXML(self, xml):
        if type(xml) == str:
            dom = minidom.parseString(xml)
            dom = dom.firstChild
        else:
            dom = xml

        if self.h_op[dom.getAttribute('t')]: # should be a node AND/OR/NOT
            self.op = self.h_op[dom.getAttribute('t')]()
            for child in dom.childNodes: # node p
                if child.firstChild.nodeType == dom.TEXT_NODE:
                    bv = BoolValue(child.firstChild.nodeValue)
                    self.list[bv.id] = bv
                else:
                    be = BoolEquation(child.firstChild, True)
                    self.list[be.id] = be
        else:
            raise "unknown"


    def parse(self, str):
        # as XML parse better, and convertion from STR to XML is quite easy, we use the XML parser
        xml = s2x6.sub('', s2x5.sub('</p></b>', s2x4.sub('</p><p>', s2x3.sub('<b t="NOT"><p>', s2x2.sub('<b t="OR"><p>', s2x1.sub('<b t="AND"><p>', str))))))
        return self.parseXML(xml)

    def merge(self, lists):
        retour = []
        for beid in self.list:
            retour.append(self.list[beid].merge(lists))
        retour = self.op.merge(retour)
        logging.getLogger().debug('>>>> new one')
        return retour

    def getTree(self, lists):
        retour = []
        for beid in self.list:
            retour.append(self.list[beid].getTree(lists))
        retour = self.op.getTree(retour)
        return retour

    def toH(self):
        func = getattr(self.op, 'toH')
        return func(self.list)
    def toS(self):
        func = getattr(self.op, 'toS')
        return func(self.list)
    def toXML(self):
        func = getattr(self.op, 'toXML')
        return func(self.list)

class BoolValue(BoolElement):
    def __init__(self, value):
        self.setValue(value)
        self.id = randint(0, 100000)
    def toH(self):
        return self.getValue()
    def toS(self):
        return self.getValue()
    def toXML(self):
        return self.val
    def setValue(self, value):
        self.val = value
    def getValue(self):
        return self.val
    def merge(self, lists):
        return lists[self.getValue()]
    def getTree(self, lists):
        return lists[self.getValue()]



