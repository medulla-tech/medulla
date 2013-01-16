# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com
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
# along with MMC; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import os.path
import glob
import datetime
import logging
import time
import xmlrpclib

from mmc.plugins.msc.config import MscConfig
from mmc.plugins.msc.scheduler_api import SchedulerApi
from mmc.plugins.msc.client.scheduler import getProxy
from twisted.internet.threads import deferToThread
import twisted.internet.defer

class MscDownloadProcess:

    """
    Class to download file from a computer
    """

    # Some exit codes and constants
    DLOK =   0 # OK
    DLAIP =  1 # Download Already In Progress
    DLFAIL = 2 # Download failed

    def __init__(self, userid, computer, dlpath, bwlimit):
        self.userid = userid
        self.computer = computer
        self.dlpath = dlpath
        self.bwlimit = bwlimit
        self.uuid = computer[1]['objectUUID'][0]
        self.mscdlfiles = MscDownloadedFiles(self.userid)
        self.storage = self.mscdlfiles.storage
        self.lockfile = os.path.join(self.storage, self.uuid + '.' + self.mscdlfiles.LOCKEXT)
        self.logger = logging.getLogger()

    def _cbDownloadOk(self, result):
        """
        If there is a result, store it into a file.
        """
        if result != False:
            dlname, data = result
            # Convert from base64 to string
            data = str(data)
            timestamp = int(time.time())
            # Write the received file
            fname = os.path.join(self.storage, '%s-%d-%s' % (self.uuid, timestamp, dlname))
            self.logger.debug("download_file: Writing %s with %d bytes" % (fname, len(data)))
            fobj = file(fname, 'w+')
            fobj.write(data)
            fobj.close()
        else:
            self.logger.error("download_file: Couln't download the file")
            self._recordError()
        return result

    def _cbDownloadErr(self, failure):        
        self.logger.error(failure)
        self._recordError()
        return failure

    def _recordError(self):
        """
        Create a file to remember there was an error during a download
        """
        timestamp = int(time.time())
        errorfile = os.path.join(self.storage, '%s-%d' % (self.uuid, timestamp)+ '.' + self.mscdlfiles.ERROREXT)
        fobj = file(errorfile, 'w+')
        fobj.close()

    def _cbDownloadCleanup(self, result):
        """
        Call after the download to remove the download lock file
        """
        self.logger.debug("download_file: Removing lock file %s" % self.lockfile)
        os.remove(self.lockfile)

    def _gotScheduler(self, result):
        """
        Called when a scheduler has been found to start the download
        """
        if not result:
            scheduler_name = MscConfig().default_scheduler
        else:
            scheduler_name = result
        if scheduler_name not in MscConfig().schedulers:
            return twisted.internet.defer.fail(twisted.python.failure.Failure("scheduler %s does not exist" % (scheduler_name)))

        # Create the lock file
        f = file(self.lockfile, 'w+')
        f.close()        
        # Start download process
        d = getProxy(MscConfig().schedulers[scheduler_name]).callRemote(
            'download_file',
            self.computer[1]['objectUUID'][0],
            self.computer[1]['fullname'],
            self.computer[1]['cn'][0],
            self.computer[1]['ipHostNumber'],
            self.computer[1]['macAddress'],
            self.dlpath,
            self.bwlimit
        )
        # Add callback
        d.addCallback(self._cbDownloadOk).addErrback(self._cbDownloadErr)
        d.addBoth(self._cbDownloadCleanup)

    def startDownload(self):
        """
        Start file download process in a new thread.

        @rtype: tuple
        @returns: tuple with (status, reason)        
        """
        def _start():
            # Start download process
            mydeffered = SchedulerApi().getScheduler(self.uuid)
            mydeffered.addCallback(self._gotScheduler).addErrback(lambda reason: reason)

        if self.mscdlfiles.isDownloadInProgress():
            return (False, self.DLAIP)
        if not os.path.exists(self.storage):
            os.mkdir(self.storage)
        deferToThread(_start)
        return (True, self.DLOK)


class MscDownloadedFiles:

    """
    Class to manage the downloaded files of a user
    """

    LOCKEXT = 'lock'
    ERROREXT = 'error'

    def __init__(self, userid):
        self.userid = userid
        self.storage = os.path.join(MscConfig().download_directory_path, self.userid)

    def isDownloadInProgress(self):
        """
        Check if a download is in progress for the current user
        """
        return len(glob.glob(os.path.join(self.storage, '*.' + self.LOCKEXT))) > 0

    def getFile(self, node):
        """
        Return file content

        @rtype: tuple
        @returns: tuple with (filename, data)
        """
        ret = False
        for fname in os.listdir(self.storage):
            fp = os.path.join(self.storage, fname)
            statinfo = os.stat(fp)
            if statinfo.st_ino == long(node):
                uuid, timestamp, name = fname.split('-', 2)
                f = file(fp)
                data = f.read()
                f.close()
                ret = (name, xmlrpclib.Binary(data))
                break
        return ret

    def getFilesList(self):
        """
        Return the available downloaded files for the current user.
        The later the latest in the list.

        @rtype: list
        @returns: list of tuples (filename, uuid, timestamp, length, inode)
        """
        ret = []
        if os.path.exists(self.storage):
            tmp = {}
            # Get files list from the storage directory
            for fname in os.listdir(self.storage):
                statinfo = os.stat(os.path.join(self.storage, fname))
                if fname.endswith(self.LOCKEXT):
                    # Download lock file
                    timestamp = statinfo.st_mtime
                    uuid = fname.split('.')[0]
                    tmp[timestamp] = ('', uuid, list(datetime.datetime.fromtimestamp(float(statinfo.st_mtime)).timetuple()), 0, statinfo.st_ino)
                elif fname.endswith(self.ERROREXT):
                    # Error status file
                    uuid, timestamp = os.path.splitext(fname)[0].split('-')
                    tmp[timestamp] = ('', uuid, list(datetime.datetime.fromtimestamp(float(timestamp)).timetuple()), -1, statinfo.st_ino)
                else:
                    # Downloaded file
                    try:
                        uuid, timestamp, name = fname.split('-', 2)
                        tmp[int(timestamp)] = (name, uuid, list(datetime.datetime.fromtimestamp(float(timestamp)).timetuple()), statinfo.st_size, statinfo.st_ino)
                    except ValueError:
                        pass
            # Sort file list by inverse chronological order
            timestamps = tmp.keys()
            timestamps.sort(reverse = True)
            for timestamp in timestamps:
                ret.append(tmp[timestamp])
        return ret
        
    def removeFiles(self, inodes):
        """
        Remove the files with the given inode numbers

        @rtype: int
        @returns: the count of removed files
        """
        ret = 0
        for fname in os.listdir(self.storage):
            statinfo = os.stat(os.path.join(self.storage, fname))
            if str(statinfo.st_ino) in inodes:
                os.remove(os.path.join(self.storage, fname))
                ret = ret + 1
        return ret
