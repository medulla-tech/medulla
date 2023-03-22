#!/usr/bin/python
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
    Give stats on-the-fly
"""

import logging
import time
from pulse2.health import basicHealth
from pulse2.database.msc import MscDatabase
from pulse2.scheduler.config import SchedulerConfig

"""
    global vars to hold past timestamps, used by checkLoops()
"""
class SchedulerTimestamp:
    ts = 0
    def __init__(self):
        self.touch()
    def touch(self):
        self.ts = time.time()
    def delta(self):
        return time.time() - self.ts

startLoopTS = SchedulerTimestamp()
stopLoopTS = SchedulerTimestamp()
logLoopTS = SchedulerTimestamp()
preemptLoopTS = SchedulerTimestamp()

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
    return health

def checkPool():
    ret = True
    try :
        pool = MscDatabase().db.pool
        if pool._max_overflow > -1 and pool._overflow >= pool._max_overflow :
            logging.getLogger().error('scheduler %s: CHECK: NOK: timeout then overflow (%d vs. %d) detected in SQL pool : check your network connectivity !' % (SchedulerConfig().name, pool._overflow, pool._max_overflow))
            pool.dispose()
            pool = pool.recreate()
            ret = False
    except Exception, e:
        logging.getLogger().warn('scheduler %s: CHECK: NOK: got the following error : %s' % (SchedulerConfig().name, e))
        ret = False
    return ret

def checkLoops():
    ret = True
    try :
        if startLoopTS.delta() > 3 * SchedulerConfig().awake_time: # sounds the alarm if more than 3 start iteration were missed
            logging.getLogger().warn('scheduler %s: CHECK: NOK: seems the START loop is running into trouble; this may be due to load / network issue; please check your network environment !' % (SchedulerConfig().name))
            ret = False
        if stopLoopTS.delta() > 3 * SchedulerConfig().awake_time: # sounds the alarm if more than 3 stop iteration were missed
            logging.getLogger().warn('scheduler %s: CHECK: NOK: seems the STOP loop is running into trouble; this may be due to load / network issue; please check your network environment !' % (SchedulerConfig().name))
            ret = False
        if preemptLoopTS.delta() > SchedulerConfig().awake_time: # sounds the alarm if no preempt was done in awake-time interval
            logging.getLogger().warn('scheduler %s: CHECK: NOK: seems the PREEMPT loop is running into trouble; this may be due to load / network issue; please check your network environment !' % (SchedulerConfig().name))
            ret = False
        if logLoopTS.delta() > SchedulerConfig().awake_time: # sounds the alarm if no log was done in awake-time interval
            logging.getLogger().warn('scheduler %s: CHECK: NOK: seems the HEALTH loop is running into trouble; this may be due to load issue; please check your scheduler settings !' % (SchedulerConfig().name))
            ret = False
    except Exception, e:
        logging.getLogger().warn('scheduler %s: CHECK: NOK: got the following error : %s' % (SchedulerConfig().name, e))
        ret = False
    return ret

def checkStatus():
    if checkPool() and checkLoops():
        logging.getLogger().info('scheduler %s: CHECK: OK' % SchedulerConfig().name)
