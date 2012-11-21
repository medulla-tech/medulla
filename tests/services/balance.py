#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# (c) 2012 Mandriva, http://www.mandriva.com
#
# This file is part of Mandriva Management Console (MMC).
#
# MMC is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# MMC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MMC.  If not, see <http://www.gnu.org/licenses/>.

"""
Test module for the scheduler balance module - part of advanced scheduling
"""

import sys
import unittest
import random
import datetime

from pulse2.scheduler import balance


def get_nbr_steps (nbr_attempts):
    if nbr_attempts % 2 > 0 :
        return nbr_attempts // 2
    else :
        return nbr_attempts / 2



class class01BalanceTest(unittest.TestCase):
    """
    Test to get parabolic balanced list of coefficients
    """
    def setUp (self):
        self.NBR_ATTEMPTS = random.choice(range(2,100))
        #print "Number of attempts : %d" % self.NBR_ATTEMPTS

    def test01get_list(self):
        b = balance.ParabolicBalance(self.NBR_ATTEMPTS)
        result = sum(b.balances)
         
        self.assertEqual(round(result,2), 1)

    def test02is_symetric_curve(self):
        b = balance.ParabolicBalance(self.NBR_ATTEMPTS)
        nbr_steps = get_nbr_steps(self.NBR_ATTEMPTS)
        egality = True
        for i in range(nbr_steps) :
            b_offset = self.NBR_ATTEMPTS - i
            left = b.balances[i]
            right = b.balances[b_offset-1:b_offset][0]
            if round(left,5) != round(right,5) :
                egality = False

        self.assertEqual(egality, True)

    def test_is_parabolic_curve(self):
        """test of curve run"""
        b = balance.ParabolicBalance(self.NBR_ATTEMPTS)
        nbr_steps = get_nbr_steps(self.NBR_ATTEMPTS)
        
        is_parabolic = True
        previous = 0.0
        for i in range(nbr_steps) :
            if previous >= b.balances[i] :
                is_parabolic = False
                break
            previous = b.balances[i]
        if is_parabolic :
            previous = 0.0
            for i in range(self.NBR_ATTEMPTS-1, nbr_steps, -1):
                if previous >= b.balances[i] :
                    is_parabolic = False
                    break
                previous = b.balances[i]
 
        self.assertEqual(is_parabolic, True)


class class02BalanceTest(unittest.TestCase):
    """Test of calculation of balances linked on CoHs"""

    def setUp(self):
        start = datetime.datetime.now()
        
        self.coh_struct_set = []
        self.limit = random.choice(range(1,100))
        for i in range(100) :
            id = random.choice(range(500))
            hours = random.choice(range(1,100))
            attempts_failed = random.choice(range(100))
            end = start + datetime.timedelta(hours=hours)

            self.coh_struct_set.append((id, start, end, attempts_failed)) 


    def test01get_list(self):
        """calculed balance must be less than 1"""
        is_correct = True
        for (id, start, end, attempts_failed) in self.coh_struct_set :
            value = balance.getBalanceByAttempts (start, end, attempts_failed)
            if value > 1 :
                is_correct = False
                break
    
        self.assertEqual(is_correct, True)



    def test02draw_and_choice(self):
        """random choice must return more than 80% elements"""
        cohs = {}
        for (id, start, end, attempts_failed) in self.coh_struct_set :
            value = balance.getBalanceByAttempts (start, end, attempts_failed)
            cohs[id] = value

        selected = balance.randomListByBalance(cohs, self.limit)
        is_correct = len(selected) / self.limit > 0.8

        self.assertEqual(is_correct, True)

 
if __name__ == "__main__" :
    unittest.main()

