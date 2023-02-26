# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Utilities for running dlp tests
"""

import os
import shutil
import json
import unittest
from subprocess import Popen
import time
import cookielib
import urllib
import urllib2


def run_agent():
    print "### RUNNING DLP"
    process = Popen(['pulse2-dlp-server', '-d', '-c', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')])
    time.sleep(2)
    return process


def stop_agent(process):
    print "### STOPPING DLP"
    process.terminate()


def run_tests(test_case, process):
    print "### RUNNING TESTS"
    try:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
        unittest.TextTestRunner(verbosity=2).run(suite)
    except KeyboardInterrupt:
        process.terminate()


def clean_packages():
    # clean packages cache
    if os.path.exists('/tmp/test_packages/'):
        shutil.rmtree('/tmp/test_packages/')


class HTTPClient(object):

    def __init__(self, base_url):
        self.cookie_jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
        urllib2.install_opener(self.opener)
        self.base_url = base_url

    def get(self, url, headers={}):
        """HTTP GET

        url should be a string containing a valid URL.
        headers should be a dictionary
        """
        url = self.base_url + url
        request = urllib2.Request(url, headers=headers)
        return self.execute_request(request)

    def post(self, url, data=None, headers={}):
        """HTTP POST

        url should be a string containing a valid URL.
        data should be a url-encodable dictionary
        headers should be a dictionary
        """
        url = self.base_url + url
        if data is None:
            postdata = None
        else:
            postdata = urllib.urlencode(data, True)
        request = urllib2.Request(url, postdata, headers)
        return self.execute_request(request)

    def execute_request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read()
        if response.info().get("Content-Type", None) == "application/json":
            response.data = json.loads(response.data)
        return response
