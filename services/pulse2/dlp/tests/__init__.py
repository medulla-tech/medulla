# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2013 Mandriva, http://www.mandriva.com
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
Unit tests for the dlp TEST API
"""

import os
import unittest
import time
import tempfile
import zipfile
from urllib2 import HTTPError

from pulse2.dlp.tests.utils import run_agent, run_tests, stop_agent, HTTPClient, clean_packages


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.client = HTTPClient("http://127.0.0.1:48999/api/v1")

    def testWrongAuth(self):
        with self.assertRaises(HTTPError) as context:
            self.client.post('/auth', {'authkey': 'FOO', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.assertEqual(context.exception.code, 401)

    def testBasHostname(self):
        with self.assertRaises(HTTPError) as context:
            self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'FOO', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.assertEqual(context.exception.code, 404)

    def testCorrectAuth(self):
        result = self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.assertEqual(result.code, 200)

    def testMultipleMACs(self):
        result = self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': ['AA:BB:CC:DD:EE:FF', 'AA:BB:CC:DD:EE:00']})
        self.assertEqual(result.code, 200)

    def testBadMAC(self):
        with self.assertRaises(HTTPError) as context:
            self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC'})
        self.assertEqual(context.exception.code, 400)

    def testBadParams(self):
        with self.assertRaises(HTTPError) as context:
            self.client.post('/auth', {'authkey': 'TEST', 'host': 'test1', 'macs': 'AA:BB:CC'})
        self.assertEqual(context.exception.code, 404)


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.client = HTTPClient("http://127.0.0.1:48999/api/v1")
        clean_packages()

    def testGetCommands(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        result = self.client.get('/commands')
        self.assertEqual(result.code, 200)
        self.assertEqual(result.data[0]['package_uuid'], u'd13d3eaa-587a-11e3-adfa-080027fd96ca')

    def testGetCommandsNoAuth(self):
        with self.assertRaises(HTTPError) as context:
            self.client.get('/commands')
        self.assertEqual(context.exception.code, 403)

    def testPackageCache(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        result = self.client.get('/commands')
        uuid = result.data[0]['package_uuid']
        infos_1 = os.stat('/tmp/test_packages/%s.zip' % uuid)
        self.client.get('/commands')
        infos_2 = os.stat('/tmp/test_packages/%s.zip' % uuid)
        self.assertEqual(infos_1.st_ctime, infos_2.st_ctime)
        # wait cache to expire (5 seconds)
        time.sleep(6)
        self.client.get('/commands')
        infos_3 = os.stat('/tmp/test_packages/%s.zip' % uuid)
        self.assertNotEqual(infos_2.st_ctime, infos_3.st_ctime)

    def tearDown(self):
        clean_packages()


class TestFile(unittest.TestCase):

    def setUp(self):
        self.client = HTTPClient("http://127.0.0.1:48999/api/v1")
        clean_packages()

    def testFileDownload(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        result = self.client.get('/commands')
        result = self.client.get('/file/%s' % result.data[0]['package_uuid'] + ".zip")
        fd, tmp_file = tempfile.mkstemp()
        f = os.fdopen(fd, 'w+')
        f.write(result.data)
        f.close()
        zip = zipfile.ZipFile(tmp_file)
        files_list = zip.namelist()
        self.assertTrue('base64' in files_list[1])
        self.assertTrue('mandriva-baseline-fr-FR.png' in files_list[2])
        self.assertTrue('pulse2-pdt-page.jpg' in files_list[3])
        os.unlink(tmp_file)

    def testNotFoundDownload(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.client.get('/commands')
        with self.assertRaises(HTTPError) as context:
            self.client.get('/file/notfound')
        self.assertEqual(context.exception.code, 404)

    def testNoRightsDownload(self):
        # generate package for test2
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test2', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.client.get('/commands')
        # auth as test1 and try to download test2 package
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.client.get('/commands')
        with self.assertRaises(HTTPError) as context:
            self.client.get('/file/fbcc96e2-58fd-11e3-877e-080027fd96ca.zip')
        self.assertEqual(context.exception.code, 401)

    def tearDown(self):
        clean_packages()


class TestStep(unittest.TestCase):

    def setUp(self):
        self.client = HTTPClient("http://127.0.0.1:48999/api/v1")
        clean_packages()

    def testSendResult(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.client.get('/commands')
        result = self.client.post('/step/1/upload/', data={'stdout': 'stdout', 'stderr': 'stderr', 'return_code': 0})
        self.assertEqual(result.code, 201)

    def testSendResultWrongCohId(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.client.get('/commands')
        with self.assertRaises(HTTPError) as context:
            self.client.post('/step/2/upload/', data={'stdout': 'stdout', 'stderr': 'stderr', 'return_code': 0})
        self.assertEqual(context.exception.code, 401)

    def testSendResultBadCohId(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        with self.assertRaises(HTTPError) as context:
            self.client.post('/step/foo/upload/', data={'stdout': 'stdout', 'stderr': 'stderr', 'return_code': 0})
        self.assertEqual(context.exception.code, 400)

    def testSendResultWrongStepId(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test1', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.client.get('/commands')
        with self.assertRaises(HTTPError) as context:
            self.client.post('/step/1/foo/', data={'stdout': 'stdout', 'stderr': 'stderr', 'return_code': 0})
        self.assertEqual(context.exception.code, 401)

    def testSenfResultServerError(self):
        self.client.post('/auth', {'authkey': 'TEST', 'hostname': 'test2', 'mac_list': 'AA:BB:CC:DD:EE:FF'})
        self.client.get('/commands')
        with self.assertRaises(HTTPError) as context:
            self.client.post('/step/2/upload/', data={'stdout': 'stdout', 'stderr': 'stderr', 'return_code': 0})
        self.assertEqual(context.exception.code, 503)

    def tearDown(self):
        clean_packages()


if __name__ == '__main__':
    process = run_agent()
    run_tests(TestAuth, process)
    run_tests(TestCommands, process)
    run_tests(TestFile, process)
    run_tests(TestStep, process)
    stop_agent(process)
