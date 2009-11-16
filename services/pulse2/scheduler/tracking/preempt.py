#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2009 Nicolas Rueff / Mandriva, http://www.mandriva.com/
#
# $Id: commands.py 478 2009-10-05 16:13:27Z nrueff $
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

# store commands which will be preemtped
# the base structure is a simple persistent set
# with a semaphore

# import set
try: # python 2.4+
    set
except NameError: # python 2.3-
    from sets import Set as set

# logging stuff
import logging

# semaphore handling
import threading

# Others Pulse2 Stuff
import pulse2.utils

class Pulse2Preempt(pulse2.utils.Singleton):

    semaphore = threading.Semaphore(1)
    content = set()

    def __lock(self):
        self.semaphore.acquire(True)

    def __unlock(self):
        self.semaphore.release()

    def put(self, elements):
        self.__lock()
        try:
            self.content.update(elements)
        finally:
            self.__unlock()
        #MDV/NR if len(elements):
            #MDV/NR logging.getLogger().debug("PREEMPT : p(%s) = %d" % (elements, len(elements)))

    def members(self):
        result = list()
        self.__lock()
        try:
            result = list(self.content)
        finally:
            self.__unlock()
        #MDV/NR if len(result):
            #MDV/NR logging.getLogger().debug("PREEMPT : l(%s) = %d" % (result, len(result)))
        return result

    def get(self, number):
        result = list()
        self.__lock()
        try:
            i = min(number, len(self.content))
            while i > 0:
                result.append(self.content.pop())
                i = i-1
        finally:
            self.__unlock()
        #MDV/NR if len(result):
            #MDV/NR logging.getLogger().debug("PREEMPT : g(%s) = %d" % (result, len(result)))
        return result

