# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later
"""
Utilities functions for the dlp application
"""

import os
import time
import urllib2
import zipfile
import cherrypy
import logging

from pulse2.dlp.tools import HOSTNAME_KEY, UUID_KEY


def log(message, severity=logging.DEBUG, traceback=False):
    hostname = cherrypy.session.get(HOSTNAME_KEY, False)
    uuid = cherrypy.session.get(UUID_KEY, False)
    start = "APIv1"
    if hostname and uuid:
        start += ' (%s, %s)' % (hostname, uuid)
    cherrypy.request.app.log(message, start, severity=severity, traceback=traceback)


def download_file(url, dest, retries):
    try:
        res = urllib2.urlopen(url)
        path, filename = url.rsplit('/', 1)
        blocksize = 8192
        with open(os.path.join(dest, filename), 'wb') as f:
            while True:
                chunk = res.read(blocksize)
                if not chunk:
                    break
                f.write(chunk)
        return True
    except:
        if retries > 0:
            log("Failed to download file. Retrying...", logging.WARNING)
            time.sleep(1)
            return download_file(url, dest, retries - 1)
        else:
            log("Failed to download file:\n", logging.ERROR, True)
            raise


def make_zipfile(output_filename, source_dir):
    relroot = os.path.abspath(source_dir)
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(source_dir):
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)
