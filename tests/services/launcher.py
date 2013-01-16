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
Test module for the Pulse 2 Launcher
"""

from xmlrpclib import ServerProxy
from unittest import TestCase
from os import chdir, popen, system, removedirs, remove, getcwd, mkdir, path
from tempfile import mkdtemp
from time import sleep
import unittest
from testutils import generation_Launcher
import sys

ipserver='localhost' #adress of pulse2 Launcher
uuid='UUID1' #client uuid
makefile=False
if "makefile" in sys.argv:
    makefile=True

if "debug" in sys.argv:
    mode="debug"
    Verbosity=2
else:
    mode="info"

del(sys.argv[1:])
direct=getcwd()

server=ServerProxy('https://username:password@%s:8001' % ipserver)

class class01sync_push_inventoryTest(TestCase):
    """
    Test's class of sync_remote_push and sync_remote_inventory
    """

    def test101sync_remote_push(self):
        result=server.sync_remote_push(1,{'protocol':'rsyncssh','host':ipserver,'uuid':uuid},[file])
        self.assertEqual ( result,[0,result[1], ''])

    def test102sync_remote_inventory(self):
        result=server.sync_remote_inventory(0,{'protocol':'ssh','host':ipserver,'uuid':uuid})
        self.assertEqual ( result, [1, result[1], ''])


class class02sync_deleteTest(TestCase):
    """
    Test's class of sync_remote_delete
    """

    def test201sync_remote_delete(self):
        result=server.sync_remote_delete(1,{'protocol':'ssh','host':ipserver,'uuid':uuid},["test.bin"])
        self.assertEqual ( result, [0, result[1],''])

class class03async_push_inventoryTest(TestCase):
    """
    Test's class of async_remote_push and async_remote_inventory
    """

    def test301async_remote_push(self):
        result=server.async_remote_push(1,{'protocol':'rsyncssh','host':ipserver,'uuid':uuid},[file])
        self.assertEqual ( result, True)

    def test302async_remote_inventory(self):
        result=server.async_remote_inventory(0,{'protocol':'ssh','host':ipserver,'uuid':uuid})
        self.assertEqual ( result, True)

class class04async_deleteTest(TestCase):
    """
    Test's class of async_remote_delete
    """

    def test401async_remote_delete(self):
        result=server.async_remote_delete(2,{'protocol':'ssh','host':ipserver,'uuid':uuid},["test.bin"])
        self.assertEqual ( result, True)

class class05statTest(TestCase):
    """
    Test's class of get_process_times, get_process_state and get_process_statistics
    """

    def test501get_process_times(self):
        result=server.get_process_times(1)
        self.assertEqual (result,{'end': result['end'], 'age': result['age'], 'elapsed': result['elapsed'], 'start':result['start'], 'last': result['last'], 'now': result['now']})

    def test502get_process_state(self):
        result=server.get_process_state(1)
        self.assertEqual (result,{'status': result['status'], 'kind': result['kind'], 'group': result['group'], 'signal': result['signal'], 'pid': result['pid'], 'exit_code': result['exit_code'], 'command':result['command'], 'done': result['done'], 'id':1})

    def test503get_process_statistics(self):
        result=server.get_process_statistics(1)
        self.assertEqual (result,{'status': result['status'], 'kind': result['kind'], 'end': result['end'], 'signal': result['signal'], 'age': result['age'], 'pid': result['pid'],'exit_code': result['exit_code'], 'elapsed': result['elapsed'],  'start':result['start'], 'command': result['command'] , 'done':result['done'], 'last': result['last'], 'now': result['now'], 'id': 1, 'group': result['group']})


class class06killTest(TestCase):
    """
    Test's class of kill_all_process and stop_all_process
    """
    def test601stop_all_process(self):
        result=server.stop_all_process()
        self.assertEqual (result,True)

    def test602kill_all_process(self):
        result=server.kill_all_process()
        self.assertEqual (result,True)

class class07sync_execTest(TestCase):
    """
    Test's class of sync_remote_exec with his three output, get_process_count, get_running_count and get_zombie_count
    """
    def test701sync_remote_exececcho(self):
        result=server.sync_remote_exec(2,{'protocol':'ssh','host':ipserver,'uuid':uuid},"echo \"toto\"")
        self.assertEqual ( result, [0,result[1],""])

    def tests702ync_remote_execerreur(self):
        result=server.sync_remote_exec(3,{'protocol':'ssh','host':ipserver,'uuid':uuid},"echo \"toto\" 1>&2")
        self.assertEqual ( result, [0,result[1],""])

    def test703sync_remote_execexit(self):
        result=server.sync_remote_exec(4,{'protocol':'ssh','host':ipserver,'uuid':uuid},"exit 1")
        self.assertEqual ( result, [1,result[1],""])

    def test704get_process_count(self):
        result=server.get_process_count()
        self.assertEqual(result, 0)

    def test705get_running_count(self):
        result=server.get_running_count()
        self.assertEqual(result, 0)

    def test706get_zombie_count(self):
        result=server.get_zombie_count()
        self.assertEqual(result, 0)

class class08async_execTest(TestCase):
    """
    Test's class of async_remote_exec with his three output, term_processes and hup_all_process
    """

    def test801async_remote_execerreur(self):
        result=server.async_remote_exec(4,{'protocol':'ssh','host':ipserver,'uuid':uuid},"echo \"toto\" 1>&2")
        self.assertEqual (result, True)

    def test802async_remote_execexit(self):
        result=server.async_remote_exec(5,{'protocol':'ssh','host':ipserver,'uuid':uuid},"exit 1")
        self.assertEqual (result, True)

    def test803term_processes(self):
        result=server.term_processes([4,5])
        self.assertEqual (result,True)

    def test804hup_all_process(self):
        result=server.hup_all_process()
        self.assertEqual (result,True)

    def test805async_remote_execsleep(self):
        result=server.async_remote_exec(3,{'protocol':'ssh','host':ipserver,'uuid':uuid}, "cat")
        self.assertEqual ( result, True)

class class09stopTest(TestCase):
    """
    Test's class of stop_process
    """
    def test901stop_process(self):
        result=server.stop_process(3)
        self.assertEqual (result,True)

class class10stdTest(TestCase):
    """
    Test's class of get_process_stdout, get_process_stder and get_process_exitcode
    """
    def test1001get_process_stdout(self):
        result=server.get_process_stdout(3)
        self.assertEqual(result, '')

    def test1001get_process_stderr(self):
        result=server.get_process_stderr(3)
        self.assertEqual(result, '')

    def test1002get_process_exitcode(self):
        result=server.get_process_exitcode(3)
        self.assertEquals(result, '')

class class11int_contTest(TestCase):
    """
    Test's class of int_process and cont_process
    """
    def test1101cont_process(self):
        result=server.cont_process(3)
        self.assertEqual (result,True)

    def test1102int_process(self):
        result = server.int_process(3)
        self.assertEqual(result,True)

class class12sync_quickactionTest(TestCase):
    """
    Test's class of sync_remote_quickaction with his three output
    """
    def test1201sync_remote_quickactionecho(self):
        result=server.sync_remote_quickaction(6,{'protocol':'ssh','host':ipserver,'uuid':uuid},"echo \"toto\"")
        self.assertEqual ( result, [0,result[1],""])

    def test1202sync_remote_quickactionerreur(self):
        result=server.sync_remote_quickaction(7,{'protocol':'ssh','host':ipserver,'uuid':uuid},"echo \"toto\" 1>&2")
        self.assertEqual ( result, [0,result[1],""])

    def test1203sync_remote_quickactionexit(self):
        result=server.sync_remote_quickaction(8,{'protocol':'ssh','host':ipserver,'uuid':uuid},"exit 1")
        self.assertEqual ( result, [1,result[1],""])

class class13async_quickactionTest(TestCase):
    """
    Test's class of async_remote_quickaction with his three output, kill_proces, hup_process, term_process and term_all_process
    """
    def test1301async_remote_quickactionecho(self):
        result=server.async_remote_quickaction(6,{'protocol':'ssh','host':ipserver,'uuid':uuid},"echo \"toto\"")
        self.assertEqual ( result, True)

    def test1302async_remote_quickactionerreur(self):
        result=server.async_remote_quickaction(7,{'protocol':'ssh','host':ipserver,'uuid':uuid},"echo \"toto\" 1>&2")
        self.assertEqual ( result, True)

    def test1303async_remote_quickactionexit(self):
        result=server.async_remote_quickaction(8,{'protocol':'ssh','host':ipserver,'uuid':uuid},"exit 1")
        self.assertEqual ( result, True)

    def test1304kill_process(self):
        result=server.kill_process(8)
        self.assertEqual (result, True)

    def test1305hup_process(self):
        result=server.hup_process(6)
        self.assertEqual (result,True)

    def test1306term_process(self):
        result=server.term_process(7)
        self.assertEqual (result,True)

    def test1307term_all_process(self):
        result=server.term_all_process()
        self.assertEqual (result,True)

class class14idsTest(TestCase):
    """
    Test's class of get_process_id, get_running_ids, get_zombie_ids, cont_all_process and int_all_process
    """
    def test1401get_process_ids(self):
        sleep (10)
        result=server.get_process_ids()
        self.assertEqual (result,[])

    def test1402get_running_ids(self):
        result=server.get_running_ids()
        self.assertEqual (result,[])

    def test1403get_zombie_ids(self):
        result=server.get_zombie_ids()
        self.assertEqual (result,[])

    def test1404cont_all_process(self):
        result=server.cont_all_process()
        self.assertEqual (result,True)

    def test1405int_all_process(self):
        result=server.int_all_process()
        self.assertEqual (result,True)

class class15NetworkStuffTest (TestCase):
    """
    Test's class of icmp with one right ip's adress and one fake ip's adress, probe with one right ip's adress and one fake ip's adress, get_pubkey, wol and sync_remote_wol
    """
    def test1501icmp(self):
        result=server.icmp("127.0.0.1")
        self.assertEqual(result,True)

    def test1502icmp_error(self):
        result=server.icmp("0.0.0.1")
        self.assertEqual(result,False)

    def test1503probe(self):
        result=server.probe("127.0.0.1")
        self.assertEqual(result,'GNU Linux')

    def test1504probe_error(self):
        result=server.probe("0.0.0.1")
        self.assertEqual(result,'Not available')

    def test1505get_pubkey(self):
        result=server.get_pubkey("")
        ssh=open("/root/.ssh/id_rsa.pub","r")
        ssh_key=ssh.read()
        self.assertEqual(result,ssh_key)

    def test1506wol(self):
        result=server.wol(["00:11:22:33:44:55"],["255.255.255.255"])
        self.assertEqual(result,[True, "mac addresses: ['00:11:22:33:44:55'], target broadcasts: ['255.255.255.255']", ''])

#    def test1507sync_remote_wol(self):
#        result=server.sync_remote_wol(0,{'protocol':'ssh','host':ipserver,'uuid':uuid})
#        self.assertEqual ( result, False)

class class16SProxyStuffTest(TestCase):
    """
    Test's class of get_health, download_file, get_balance, tcp_sproxy
    """
    def test1601get_health(self):
        result=server.get_health()
        self.assertEqual (result,{'slots': result["slots"], 'loadavg': result["loadavg"], 'fd': result["fd"], 'memory':result["memory"]})

    def test1602download_file(self):
        result=server.download_file({'protocol':'ssh','fqdn':'localhost.localdomain','host':ipserver,'uuid':uuid,'ips':['127.0.0.1'],'macs':["00:11:22:33:44:55"]},[directory])
        self.assertEqual (result,['test.bin', result[1]])

    def test1603get_balance(self):
        result=server.get_balance()
        self.assertEqual (result,{'global': result["global"], 'by_group': result["by_group"], 'by_kind': result["by_kind"]})

#    def test1604tcp_sproxy(self):
#        result=server.tcp_sproxy({'protocol':'ssh','fqdn':'localhost.localdomain','host':ipserver,'uuid':uuid,'ips':['127.0.0.1'],'macs':["00:11:22:33:44:55"]},'11227.0.0.1',"9990")
#        self.assertEqual (result,True)

class class17sleepTest(TestCase):
    """
    Test's class witch verifies if the process changes his state correctly
    """
    def disabletest1701get_sleep(self):
        CMD = "cat"
        server.async_remote_quickaction(111190,{'protocol':'ssh','host':ipserver,'uuid':uuid}, CMD)
        sleep(5)
        test=popen('ps -C %s -o state=' % CMD)
        t=test.read()
        test.close()
        if t.startswith("S"):
            r="S"
        else:
            r="error"
        server.stop_process(111190)
        sleep(5)
        test=popen('ps -C %s -o state=' % CMD)
        t=test.read()
        test.close()
        if t.startswith("T"):
            e="T"
        else:
            e="error"
        server.cont_process(111190)
        sleep(5)
        test=popen('ps -C %s -o state=' % CMD)
        t=test.read()
        test.close()
        if t.startswith("S"):
            s="S"
        else:
            s="error"
        result=r+e+s
        server.kill_process(111190)
        self.assertEqual(result, "STS")

class class18removedir(TestCase):
    """
    Test's class which exist only for remove the tempory's directory
    """
    def test1801removedirs(self):
        remove('test.bin')
        if makefile:
            removedirs(directory)

if makefile:
    test=popen('ps ax|grep \"bin/pulse2-launchers\"')
    t=test.read()
    ts=t.split()
    process=int(ts[0])
    test.close()
    system ("kill %i" %(process))
    directory=mkdtemp(suffix='launcher',prefix='pulse2',dir="/tmp")
    generation_Launcher(directory)
    file=directory+'/test.bin'
    chdir("%s/config/" %(directory))
    system("sed \'s/src = /src = \/tmp\/%s/\' package_server.conf > package-server.conf" % (directory[5:]))
    system( "sed -i \'s/host = /host = %s/\' package-server.conf" %(ipserver))
    system ("%s/services/bin/pulse2-launcher -c %s/services/test/config/launchers.conf -i launcher_01 -l %s/services/test/config/launchers.conf &" %(direct,direct,direct))
else:
    directory='/var/lib/pulse2/packages'
    file=directory+'/test.bin'
    generation_Launcher(directory)
    system ("/etc/init.d/pulse2-launchers restart")

if not path.exists("/tmp/log"):
    mkdir ("/tmp/log")

sleep(10)
if mode=="debug":
    success=[]
    nb=0
    for klass in [class01sync_push_inventoryTest,class02sync_deleteTest,class03async_push_inventoryTest,class04async_deleteTest,class05statTest,class06killTest,class07sync_execTest,class08async_execTest,class09stopTest,class12sync_quickactionTest,class13async_quickactionTest,class14idsTest,class15NetworkStuffTest,class16SProxyStuffTest,class17sleepTest,class18removedir]:
        suite = unittest.TestLoader().loadTestsFromTestCase(klass)
        test=unittest.TextTestRunner(verbosity=Verbosity).run(suite)
        success.append(test.wasSuccessful())
        nb=nb+test.testsRun


    if False in success:
        print "One or more test are failed or have an unexpected error"
    else:
        print "All function work"
else:

    unittest.main()

