# -*- coding: utf-8; -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
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

# big modules
import logging
import pulse2.scheduler.scheduling

def tell_i_am_alive(launcher):
    """ A launcher just contact us, log it """
    logging.getLogger().info("Scheduler: launcher %s tells us it is alive" % launcher)
    return True

def completed_push(launcher, (exitcode, stdout, stderr), id):
    logging.getLogger().info("Scheduler: launcher %s tells us that push of CoH #%s is done" % (launcher, id))
    pulse2.scheduler.scheduling.parsePushResult((exitcode, stdout, stderr), id)
    return True

def completed_pull(launcher, (exitcode, stdout, stderr), id):
    logging.getLogger().info("Scheduler: launcher %s tells us that pull of CoH #%s is done" % (launcher, id))
    pulse2.scheduler.scheduling.parsePullResult((exitcode, stdout, stderr), id)
    return True

def completed_quick_action(launcher, (exitcode, stdout, stderr), id):
    """ A launcher tell us a quick action is finished """
    logging.getLogger().info("Scheduler: launcher %s tells us that execution of CoH #%s is done" % (launcher, id))
    pulse2.scheduler.scheduling.parseExecutionResult((exitcode, stdout, stderr), id)
    return True

def completed_execution(launcher, (exitcode, stdout, stderr), id):
    logging.getLogger().info("Scheduler: launcher %s tells us that execution of CoH #%s is done" % (launcher, id))
    pulse2.scheduler.scheduling.parseExecutionResult((exitcode, stdout, stderr), id)
    return True

def completed_deletion(launcher, (exitcode, stdout, stderr), id):
    logging.getLogger().info("Scheduler: launcher %s tells us that deletion of CoH #%s is done" % (launcher, id))
    pulse2.scheduler.scheduling.parseDeleteResult((exitcode, stdout, stderr), id)
    return True

def completed_inventory(launcher, (exitcode, stdout, stderr), id):
    logging.getLogger().info("Scheduler: launcher %s tells us that inventory after of CoH #%s is done" % (launcher, id))
    pulse2.scheduler.scheduling.parseInventoryResult((exitcode, stdout, stderr), id)
    return True

def completed_reboot(launcher, (exitcode, stdout, stderr), id):
    logging.getLogger().info("Scheduler: launcher %s tells us that reboot after of CoH #%s is done" % (launcher, id))
    pulse2.scheduler.scheduling.parseRebootResult((exitcode, stdout, stderr), id)
    return True
