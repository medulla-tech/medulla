# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2012 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Create and control deferred execution plan of scheduled commands.
"""

import logging
import random
import time

class ParabolicBalance (object):
    """
    A interpretation of run of the parabolic curve, based
    on quadratic function : y = - ax^2 + bx.

    The balance coeficient is based on matematical integration
    of area between the parabolic curve and x-axis.

    Output is a list of balance coeficients which total is 1.
    """
    delta = 1

    #    Example for 5 attepts :
    #    -----------------------
    #
    # |
    # |          .--^^^--.    -x^2 + kx
    # |        :° |     | °:
    # |       °   |     |   °
    # |      /    |     |    \
    # |    .°     |     |     °.
    # |   / |     |     |     | \
    # | .   |     |     |     |   .
    # |/ S0 | S1  | S2  | S3  | S4 \
    # +-----+-----+-----+-----+-----+---
    #       1     2     3     4     k=5
    #  ---- number of attempts ----->
    #
    # S0..S4 - balance coefficients

    def __init__(self, attempts_total):
        """
        @param attempts_total: number of balances to calculate
        @type attempts_total: int
        """
        self.attempts_total = attempts_total
        self._balances = []
        self._calc()

    def get_index (self, n):
        """ """
        if n in range(self.attempts_total+1)  :
            return self.delta * n
        else :
            logging.getLogger().debug("ParabolicBalance: Out of area")

    def fx (self, x):
        """
        Integral of quadratic function.

        ITG (-x^2 + kx) dx = - x^3/3 + 2kx/2
        """
        k = self.attempts_total
        return ( (k * x**2 / 2.0)  - x**3 / 3.0)

    def fx_delta (self, x):
        """
        Get slice of integrated area.
        """
        return self.fx(x) - self.fx(x - self.delta)

    def _calc(self):

        areas = []
        for period in range(self.attempts_total) :
            x = self.get_index(period+1)
            s = self.fx_delta(x)
            areas.append(s)

        total_area = sum(areas)
        for area in areas :
            balance = 1.0 * area / total_area
            self._balances.append(balance)

    @property
    def balances (self):
        return self._balances



def randomListByBalance (balances, limit):
    """
    Function to selecting the commands_on_host ids to re-schedule.

    First step is the choice of treshold into the sorted dict (by balance).
    This treshold is considered as the lower limit of the interval to drawing
    next ids to select.
    All the choices are based on random selecting.

    @param balances: dictionary of balances having CoH id as key
    @type balances: dict

    @param limit: maximum of selected commands
    @type limit: int

    @return: list of CoH ids to reschedule
    @rtype: list

    """
    if len(balances) > 0 :
        if len(balances) <= limit :
            # no necesity to choice the most important CoHs
            return balances.keys()
        while True :

            # sort by balance
            sorted_keys = sorted(balances, key=balances.get, reverse=True)
            # draw the treshold
            drw_coh = random.choice(sorted_keys)

            logging.getLogger().debug("Keys to draw: %s " % str(sorted_keys))
            treshold_idx = sorted_keys.index(drw_coh)
            # remove all the keys bellow the treshold
            sorted_keys = sorted_keys[-treshold_idx:]
            logging.getLogger().debug("Reduced interval: %s " % str(sorted_keys))

            count = 0
            selected = []
            while True :
                if count >= limit :
                    break
                if count >= len(sorted_keys) :
                    break
                drw_coh = random.choice(sorted_keys)
                if drw_coh not in selected :
                    selected.append(drw_coh)
                    count += 1
            if len(selected) / limit > 0.8 :
                # OK when number of selected is more than 80% of limit
                return selected
            else :
                logging.getLogger().debug("List of drawed CoHs too small. Repeat the drawing")

def getBalanceByAttempts (start_date, end_date, attempts_failed) :
    """
    Calculate the command priority.

    @param start_date: date of start of launched action
    @type start_date: datetime

    @param end_date: date of end of launched action
    @type end_date: datetime

    @return: balance coefficient
    @rtype: float
    """
    # random values
    P1 = 1.6
    P2 = 2.0
    now = time.time()

    start_timestamp = time.mktime(start_date.timetuple())
    end_timestamp = time.mktime(end_date.timetuple())


    # half-cycle timestamp
    l = (end_timestamp + start_timestamp) / 2.0
    # half-cycle duration
    d = (end_timestamp - start_timestamp) / 2.0

    td = ((now - l) / d) ** P2
    dd = P1 ** (attempts_failed * 1.0)

    return td / dd
