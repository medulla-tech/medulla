#!/usr/bin/env python
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

import sys
import os
import platform
import os.path

import traceback
import logging
import time
from datetime import datetime
import croniter

# print os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "descriptorscheduler"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "..", "descriptorscheduler")))
logger = logging.getLogger()


class manage_scheduler:
    """
    This class manages events and it executes the scheduler plugins that are contained in
     The / descriptorscheduler
     Scheduled plugins are files prefixed by scheduling_

     These files must have a function schedule_main
     Def schedule_main (objectxmpp):
         Contained function

     These files also need to have a dict with its crontab descriptor.
     # Nb -1 infinite
     SCHEDULE = {"schedule": "* / 1 * * * *", "nb": -1}
     Nb makes it possible to limit the operation a n times.
    """

    def __init__(self, objectxmpp):
        # creation repertoire si non exist.
        self.taches = []

        self.now = datetime.now()

        self.objectxmpp = objectxmpp
        self.directoryschedule = os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "..", "descriptorscheduler"))

        # creation repertoire si non exist
        if not os.path.exists(self.directoryschedule):
            logging.getLogger().debug("create directory scheduler %s" % self.directoryschedule)
            os.makedirs(self.directoryschedule, 0700)

        for x in os.listdir(self.directoryschedule):
            if x.endswith(".pyc") or not x.startswith("scheduling"):
                continue
            # recupere SCHEDULERDATA
            name = x[11:-3]
            try:
                datascheduler = self.litschedule(name)
                self.add_event(name, datascheduler)
            except Exception:
                logger.error("%s" % traceback.format_exc())
                pass

    def add_event(self, name, datascheduler):
        tabcron = datascheduler['schedule']
        cron = croniter.croniter(tabcron, self.now)
        nextd = cron.get_next(datetime)
        if 'nb' in datascheduler:
            nbcount = datascheduler['nb']
        else:
            nbcount = -1
        obj = {"name": name, "exectime": time.mktime(
            nextd.timetuple()), "tabcron": tabcron, "timestart": str(self.now), "nbcount": nbcount, "count": 0}
        self.taches.append(obj)

    def process_on_event(self):
        now = datetime.now()
        secondeunix = time.mktime(now.timetuple())
        deleted = []
        for t in self.taches:
            if (secondeunix - t["exectime"]) > 0:
                # replace exectime
                t["count"] = t["count"] + 1
                if "nbcount" in t and t["nbcount"] != -1 and t["count"] > t["nbcount"]:
                    deleted.append(t)
                    logging.getLogger().debug("terminate plugin %s" % t)
                    continue
                cron = croniter.croniter(t["tabcron"], now)
                nextd = cron.get_next(datetime)
                t["exectime"] = time.mktime(nextd.timetuple())
                self.call_scheduling_main(t["name"], self.objectxmpp)
        for y in deleted:
            self.taches.remove(y)

    def call_scheduling_main(self, name, *args, **kwargs):
        mod = __import__("scheduling_%s" % name)
        logging.getLogger().debug("exec plugin scheduling_%s" % name)
        mod.schedule_main(*args, **kwargs)

    def call_scheduling_mainspe(self, name, *args, **kwargs):
        mod = __import__("scheduling_%s" % name)

        return mod.schedule_main

    def litschedule(self, name):
        mod = __import__("scheduling_%s" % name)
        return mod.SCHEDULE
