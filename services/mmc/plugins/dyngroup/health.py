#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id: health.py 897 2012-06-14 17:08:46Z nrueff $
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


