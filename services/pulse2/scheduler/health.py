#!/usr/bin/python
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
"""
    Give stats on-the-fly
"""

import logging

from pulse2.health import basicHealth
from pulse2.database.msc import MscDatabase
from pulse2.scheduler.config import SchedulerConfig

def getHealth():
    # take basic informations
    health = basicHealth()
    try:
        # add data about the current database connections pool
        pool = MscDatabase().db.pool
        health['db'] = { 'poolsize' : str(pool.size()),
                         'checkedinconns' : str(pool.checkedin()),
                         'overflow' : str(pool.overflow()),
                         'checkedoutconns': str(pool.checkedout()),
                         'recycle' : str(pool._recycle) }
    except Exception, e:
        logging.getLogger().warn('scheduler %s: HEALTH: got the following error : %s' % (SchedulerConfig().name, e))
        pass
    return health

def checkPool():
    health = getHealth()
    try :
        pool = MscDatabase().db.pool
        if pool._max_overflow > -1 and pool._overflow >= pool._max_overflow :
            logging.getLogger().warn('scheduler %s: CHECK: overflow detected in SQL pool (current = %d, max = %d), disposing and recreating pool' % (SchedulerConfig().name, pool._overflow, pool._max_overflow))
            pool.dispose()
            pool = pool.recreate()
    except Exception, e:
        logging.getLogger().warn('scheduler %s: CHECK: got the following error : %s' % (SchedulerConfig().name, e))
        pass

def checkStatus():
    checkPool()
