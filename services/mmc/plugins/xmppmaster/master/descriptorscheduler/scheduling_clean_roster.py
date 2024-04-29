# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
    This plugin is used to clean the rosters.

    To use this plugin, we need to have the substitutes on the same server as the ejabberd server.

    TODO: If we need a different testcase, we will need to use IQs.
"""
import logging
import traceback
from utils import simplecommand

plugin = {
    "VERSION": "1.0",
    "NAME": "scheduling_clean_roster",
    "TYPE": "all",
    "SCHEDULED": True,
}

SCHEDULE = {"schedule": "5 0 * * *", "nb": -1}


def schedule_main(objectxmpp):
    logging.getLogger().debug("==============Plugin scheduled==============")
    logging.getLogger().debug(plugin)
    logging.getLogger().debug("============================================")
    try:
        result = simplecommand(
            "ejabberdctl process_rosteritems delete none:to none master@medulla any"
        )

        logging.getLogger().debug(
            "cmd = ejabberdctl process_rosteritems delete none:to none master@medulla any"
        )
        logging.getLogger().debug("code return command = %s" % result["code"])
        logging.getLogger().debug("code return command = %s" % result["result"][0])

        logging.getLogger().debug("============================================")

    except Exception as execution_error:
        logging.getLogger().error(
            "The scheduling_clean_roster plugin failed to run with the error: %s"
            % execution_error
        )
        logging.getLogger().error(
            "We encountered the backtrace %s" % traceback.format_exc()
        )
