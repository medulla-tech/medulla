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

# logging stuff
import logging

# randomization
import random

# semaphore handling
import threading

# Others Pulse2 Stuff
import pulse2.utils

class Pulse2Preempt(pulse2.utils.Singleton):

    semaphore = threading.Semaphore(1)
    content = list()

    def __lock(self):
        self.semaphore.acquire(True)

    def __unlock(self):
        self.semaphore.release()

    def put(self, elements):
        self.__lock()
        try:
            for k in elements:
                if k not in self.content:
                    self.content.append(k)
        except Exception, e:
            logging.getLogger().error("PREEMPT : in put() : elements = %s, content = %s, error = %s" % (elements, self.content, e))
        self.__unlock()

    def members(self):
        result = list()
        self.__lock()
        try:
            result = self.content
        except Exception, e:
            logging.getLogger().error("PREEMPT : in members() : content = %s, error = %s" % (self.content, e))
        self.__unlock()
        return result

    def get(self, number):
        result = list()
        self.__lock()
        try:
            random.shuffle(self.content) # shuffle internal list
            i = min(number, len(self.content))
            result = self.content[:i] # will return the i (0 to i not included) first elements
            self.content = self.content[i:] # and keep the remaining
        except Exception, e:
            logging.getLogger().error("PREEMPT : in get() : number = %s, content = %s, error = %s" % (number, self.content, e))
        self.__unlock()
        return result

