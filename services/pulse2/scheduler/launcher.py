# -*- coding: utf-8; -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
#
# $Id: management.py 25 2008-02-11 16:11:18Z nrueff $
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

def tell_i_am_alive(launcher):
    """ A launcher just contact us, log it """
    logging.getLogger().info("Scheduler: launcher %s tells us it is alive" % launcher)
    return True

def completed_quick_action(launcher, (exitcode, stdout, stderr), id):
    """ A launcher tell us a quick action is finished """
    logging.getLogger().info("Scheduler: launcher %s tells us that CoH #%s is done" % (launcher, id))
    print "GOT: |%s|%s|%s|" % (exitcode, stdout, stderr)
    return True
