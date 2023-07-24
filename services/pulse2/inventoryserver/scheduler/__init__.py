#!/usr/bin/python3
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2012 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Anticipated executing of scheduled tasks on scheduler.
"""
import logging
from time import sleep

from pulse2.inventoryserver.utils import InventoryUtils, MMCProxy


logger = logging.getLogger()


class AttemptToScheduler(object):
    """
    Trigger to early executions of scheduled attempts.

    This engine is called when an inventory is received.
    """

    # First delay after the inventory reception
    # TODO - move the delays in a .ini file ?
    FIRST_DELAY = 60
    BETWEEN_TASKS_DELAY = 1

    def __init__(self, xml_content, uuid):
        """
        @param uuid: Host UUID
        @type uuid: string

        """
        self.xml = xml_content
        self.uuid = uuid
        mmc = MMCProxy()
        if not mmc.failure:
            self.proxy = mmc.proxy
            self.check_target()
        else:
            logger.warn(
                "<Inventory2Scheduler> Unable to contact MMC Agent using XMLRPC (check host/port and credentials)"
            )
            logger.warn("<Inventory2Scheduler> Scheduler actions aborted")
        logger.info("<Inventory2Scheduler> Scheduler actions finished")

    def check_target(self):
        if InventoryUtils.is_coming_from_pxe(self.xml):
            logger.info(
                "<Inventory2Scheduler> Ignoring inventory for %s received (Minimal PXE inventory)"
                % self.uuid
            )
            return

        if self.proxy.msc.is_pull_target(self.uuid):
            logger.info(
                "<Inventory2Scheduler> Ignoring inventory for %s received (Client is in Pull mode)"
                % self.uuid
            )
            return

        logger.info("<Inventory2Scheduler> Valid inventory for %s received" % self.uuid)
        self.dispatch_msc()

    def dispatch_msc(self):
        """
        Get a filtered list of scheduled tasks and executing each of them.
        """
        try:
            tasks = self.proxy.msc.checkLightPullCommands(self.uuid)
        except Exception as e:
            logger.exception(
                "<Inventory2Scheduler> Unable to start Light Pull, error was: %s"
                % str(e)
            )
            return False

        # if tasks == False:
        if len(tasks) == 0:
            logger.debug(
                "<Inventory2Scheduler> Light Pull: No deployments scheduled, skipping"
            )
            return
        else:
            # execute all commands on host :
            total = len(tasks)
            logger.info(
                "<Inventory2Scheduler> Light Pull: %d deployments to start" % total
            )

            success = self.start_all_tasks_on_host(tasks)

            if not success:
                return False

    def start_all_tasks_on_host(self, tasks):
        """
        Listing of all the commands to execute, including the delays
        before and between the executions.

        @param tasks: list of ids (coh) command_on_host.id
        @type tasks: list

        @return: bool

        """
        logger.info(
            "<Inventory2Scheduler> Light Pull: Waiting %d seconds before awaking deployments"
            % self.FIRST_DELAY
        )

        sleep(self.FIRST_DELAY)

        for id in tasks:
            try:
                self.proxy.msc.start_command_on_host(id)
            except Exception as e:
                logger.exception(
                    "<Inventory2Scheduler> Light Pull: Unable to start command %d on host %s, error was: %s"
                    % (id, self.uuid, str(e))
                )
                return False

            logger.info(
                "<Inventory2Scheduler> Light Pull: Task %d on host %s successfully re-queued)"
                % (int(id), self.uuid)
            )
            sleep(self.BETWEEN_TASKS_DELAY)

        return True
