#!/usr/bin/python
# SPDX-FileCopyrightText: 2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later
"""
PULSE2_DEPRECATED
"""


# def checkPool():
# ret = True
# try :
# pool = MscDatabase().db.pool
# if pool._max_overflow > -1 and pool._overflow >= pool._max_overflow :
# logging.getLogger().error('msc plugin: CHECK: NOK: timeout then overflow (%d vs. %d) detected in SQL pool : check your network connectivity !' % (pool._overflow, pool._max_overflow))
# pool.dispose()
# pool = pool.recreate()
# ret = False
# except Exception, e:
# logging.getLogger().warn('msc plugin: CHECK: NOK: got the following error : %s' % (e))
# ret = False
# else:
# logging.getLogger().debug('msc plugin: CHECK: OK, pool is (%d / %d)' % (pool._overflow, pool._max_overflow))
# return ret

# def checkStatus():
# if checkPool():
# logging.getLogger().info('msc plugin: CHECK: OK')

# def scheduleCheckStatus(interval):
# """ periodicaly check our status stats """
# logging.getLogger().debug('msc plugin: CHECK: Sleeping')
# delay = interval # next delay in seconds,
# delay -= time.time() % interval # rounded to the lower (second modulo base)
# twisted.internet.reactor.callLater(delay, awakeCheckStatus, interval)

# def awakeCheckStatus(interval):
# logging.getLogger().debug('msc plugin: CHECK: Starting')
# checkStatus()
# scheduleCheckStatus(interval)
