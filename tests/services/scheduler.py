#!/usr/bin/python
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
Test module for the Pulse 2 scheduler
"""

import sys
import xmlrpclib
import unittest

from tempfile import mkdtemp
from testutils import generation_Launcher, generation_Commands, generation_Machine
from os import removedirs, remove, getcwd, system

ipserver='localhost' # Address of pulse2 scheduler
uuid='UUID1' # Client UUID
fqdn='localhost.localdomain'
protocol='https'
directory=mkdtemp(suffix='launcher',prefix='pulse2',dir="/tmp")
dbdriver= "mysql"
dbhost= "localhost"
dbport= "3306"
generation_Launcher(directory)

if "debug" in sys.argv:
    mode="debug"
    Verbosity=2
else:
    mode="info"

del(sys.argv[1:])

server = xmlrpclib.ServerProxy('%s://username:password@%s:8000/' % (protocol, ipserver))

connectionC=generation_Commands(dbdriver,dbhost,dbport)

class class01schedulerTest(unittest.TestCase):
    """
    Test's class of ping,probe,ping_probe_client,download,tcp_sproxy,tell_i_alive and healt functions
    """
    def test101ping_client(self):
        result=server.ping_client(uuid,fqdn,ipserver,['127.0.0.1'],["00:11:22:33:44:55"])
        self.assertEqual (result,True)

    def test102probe_client(self):
        result=server.probe_client(uuid,fqdn,ipserver,['127.0.0.1'],["00:11:22:33:44:55"])
        self.assertEqual (result,'GNU Linux')

    def test103ping_probe_client(self):
        result=server.ping_and_probe_client(uuid,fqdn,ipserver,['127.0.0.1'],["00:11:22:33:44:55"])
        self.assertEqual (result,2)

    def test104ping_client_error(self):
        result=server.ping_client(uuid,fqdn,'0.0.0.1',['0.0.0.1'],["00:11:22:33:44:55"])
        self.assertEqual (result,False)

    def test105probe_client_error(self):
        result=server.probe_client(uuid,fqdn,'0.0.0.1',['0.0.0.1'],["00:11:22:33:44:55"])
        self.assertEqual (result,'Not available')

    def test106ping_probe_client_error(self):
        result=server.ping_and_probe_client(uuid,fqdn,'0.0.0.1',['0.0.0.1'],["00:11:22:33:44:55"])
        self.assertEqual (result,0)

    def test107download_file(self):
        result=server.download_file(uuid,fqdn,ipserver,['127.0.0.1'],["00:11:22:33:44:55"],[directory],0)
        self.assertEqual (result,['test.bin', result[1]])

    def test108tcp_sproxy(self):
        result=server.tcp_sproxy(uuid,fqdn,ipserver,'localhost',"00:11:22:33:44:55",ipserver,"9990")
        self.assertEqual (result,['127.0.0.1', result[1]])

    def test109tell_i_am_alive(self):
        result=server.tell_i_am_alive("launcher_01")
        self.assertEqual(result, True)

    def test110get_healt(self) :
        result=server.get_health()
        self.assertEqual(result, {"db":result["db"],'loadavg': result["loadavg"], 'fd': result["fd"], 'memory': result["memory"]})

class class02commandsTest(unittest.TestCase):
    """
    Test's class of start_these,start,stop and start_all commands functions, start and stop command functions and all completed functions
    """
    def test201start_these_commands(self):
        result=server.start_these_commands([2])
        self.assertEqual (result, True)

    def test202start_command(self):
        result=server.start_command("1")
        self.assertEqual(result, True)

    def test203stop_command(self):
        result=server.stop_command("1")
        self.assertEqual(result, True)


    def test204completed_quick_action (self):
        result=server.completed_quick_action('launcher_01',("","",""),"1")
        self.assertEqual(result, True)

    def test205completed_pull(self):
        result=server.completed_pull('launcher_01',("","",""),"1")
        self.assertEqual(result, True)

    def test206completed_execution(self):
        result=server.completed_execution('launcher_01',("","",""),"1")
        self.assertEqual(result, True)

    def test207completed_deletion(self):
        result=server.completed_deletion('launcher_01',("","",""),"1")
        self.assertEqual(result, True)

    def test208completed_inventory(self):
        result=server.completed_inventory('launcher_01',("","",""),"1")
        self.assertEqual(result, True)

    def test209completed_reboot(self):
        result=server.completed_reboot('launcher_01',("","",""),"1")
        self.assertEqual(result, True)

    def test210completed_halt(self):
        result=server.completed_halt('launcher_01',("","",""),"1")
        self.assertEqual(result, True)

    def test211start_all_commands(self):
        result=server.start_all_commands()
        self.assertEqual(result, True)

    def test212start_commands(self):
        result=server.start_commands(["1"])
        self.assertEqual(result, True)


    def test213stop_commands(self):
        result=server.stop_commands(["1"])
        self.assertEqual(result, True)



class class03supressionTest(unittest.TestCase):

    def test301removedirs(self):
        remove('test.bin')
        directory=getcwd()
        removedirs(directory)

    def test302supdbCommands(self):
        c=connectionC.connect()
        c.execute(""" DELETE FROM commands WHERE id="1" """)
        c.execute(""" DELETE FROM commands WHERE id="2" """)
        c.execute(""" DELETE FROM commands_on_host WHERE id="1" """)
        c.execute(""" DELETE FROM commands_on_host WHERE id="2" """)
        c.execute(""" DELETE FROM commands_on_host WHERE id="3" """)
        c.execute(""" DELETE FROM target WHERE id="1" """)
        c.close()


system ("/etc/init.d/pulse2-scheduler restart")

if mode=="debug":
    success=[]
    nb=0
    for klass in [class01schedulerTest,class02commandsTest,class03supressionTest]:
        suite = unittest.TestLoader().loadTestsFromTestCase(klass)
        test=unittest.TextTestRunner(verbosity=Verbosity).run(suite)
        success.append(test.wasSuccessful())
        nb=nb+test.testsRun


    if False in success:
        print "One or more test are failed or have an unexpected error"
    else:
        print "All function work"

    print "Pserver\'s test has run %s test" %(nb)
else:
    unittest.main()
