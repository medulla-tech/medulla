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
