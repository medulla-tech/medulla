#!/usr/bin/python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2010 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import logging
import time
import twisted.internet.reactor
from mmc.plugins.dyngroup.database import DyngroupDatabase

def checkPool():
    ret = True
    try :
        pool = DyngroupDatabase().db.pool
        if pool._max_overflow > -1 and pool._overflow >= pool._max_overflow :
            logging.getLogger().error('dyngroup plugin: CHECK: NOK: timeout then overflow (%d vs. %d) detected in SQL pool : check your network connectivity !' % (pool._overflow, pool._max_overflow))
            pool.dispose()
            pool = pool.recreate()
            ret = False
    except Exception, e:
        logging.getLogger().warn('dyngroup plugin: CHECK: NOK: got the following error : %s' % (e))
        ret = False
    else:
        logging.getLogger().debug('dyngroup plugin: CHECK: OK, pool is (%d / %d)' % (pool._overflow, pool._max_overflow))
    return ret

def checkStatus():
    if checkPool():
        logging.getLogger().info('dyngroup plugin: CHECK: OK')

def scheduleCheckStatus(interval):
    """ periodicaly check our status stats """
    logging.getLogger().debug('dyngroup plugin: CHECK: Sleeping')
    delay = interval # next delay in seconds,
    delay -= time.time() % interval # rounded to the lower (second modulo base)
    twisted.internet.reactor.callLater(delay, awakeCheckStatus, interval)

def awakeCheckStatus(interval):
    logging.getLogger().debug('dyngroup plugin: CHECK: Starting')
    checkStatus()
    scheduleCheckStatus(interval)
