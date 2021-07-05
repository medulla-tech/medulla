# -*- coding: utf-8 -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
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
    This plugin is used to clean the rosters.

    To use this plugin, we need to have the substitutes on the same server as the ejabberd server.

    TODO: If we need a different testcase, we will need to use IQs.
"""
import logging
import traceback
from utils import simplecommand

plugin = {"VERSION": "1.0", "NAME": "scheduling_clean_roster", "TYPE": "all", "SCHEDULED": True}

SCHEDULE = {"schedule": "5 0 * * *", "nb": -1}

def schedule_main(objectxmpp):
    logging.getLogger().debug("==============Plugin scheduled==============")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("============================================")
    try:
        result = simplecommand("ejabberdctl process_rosteritems delete none:to none master@pulse any")
        
        logging.getLogger().debug("cmd = ejabberdctl process_rosteritems delete none:to none master@pulse any")
        logging.getLogger().debug("code return command = %s" % result['code'])
        logging.getLogger().debug("code return command = %s" % result['result'][0])

        logging.getLogger().debug("============================================")

    except Exception as execution_error:
        logging.getLogger().error("The scheduling_clean_roster plugin failed to run with the error: %s" % execution_error)
        logging.getLogger().error("We encountered the backtrace %s" % traceback.format_exc())

