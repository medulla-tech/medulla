# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com
#
# $Id$
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
Unit tests for the MMC password helper command line tool.
"""

import unittest
import os
import tempfile
from subprocess import Popen, PIPE, STDOUT

CMD='mmc-password-helper'

class TestPasswordHelper(unittest.TestCase):

    def testPasswordGeneration(self):
        fid = os.popen('%s -n' % CMD)
        output = fid.read()
        status = fid.close()
        self.assertEqual(len(output.strip()), 8)
        self.assertEqual(status, None)

    def testPasswordGenerationWithSize(self):
        fid = os.popen('%s -n -l 10' % CMD)
        output = fid.read()
        status = fid.close()
        self.assertEqual(len(output.strip()), 10)
        self.assertEqual(status, None)

    def testPasswordSimpleCheck(self):
        fid = Popen([CMD, '-c'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        fid.communicate("xNTY1+DE")
        self.assertEqual(fid.returncode, 0)

    def testPasswordSimpleCheckFail(self):
        fid = Popen([CMD, '-c'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        fid.communicate("simplepass")
        self.assertEqual(fid.returncode, 1)

    def testPasswordShortPass(self):
        fid = Popen([CMD, '-c', '-l', '10'], stdin=PIPE)
        fid.communicate("xNTY1+DE")
        self.assertEqual(fid.returncode, 1)

    def testPasswordFromFile(self):
        filename = tempfile.mktemp()
        file = open(filename, 'w')
        file.write("xNTY1+DE")
        file.close()
        fid = os.popen('%s -c -f %s' % (CMD, filename))
        output = fid.read()
        status = fid.close()
        os.unlink(filename)
        self.assertEqual(status, None)

if __name__ == '__main__':
    unittest.main()
        
