# -*- coding: utf-8; -*-
#
# (c) 2013 Mandriva, http://www.mandriva.com/
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import os
import logging
try:
    import cPickle as pickle
except ImportError :
    import pickle # pyflakes.ignore
from functools import wraps

from pulse2.utils import SingletonN



class NotInitializedError(Exception):

    def __repr__(self):
        return "Buffer not initialized"




def initialized(method):
    """
    Blocks the decorated method when _initialized attribute is False.

    @param method: decorated method
    @type method: callable
    """
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        if self._initialized :
            return method(self, *args, **kwargs)
        else :
            raise NotInitializedError

    return wrapped



class SendingBuffer(object):
    __metaclass__ = SingletonN

    """
    Provides a LIFO buffer processing the responses from launchers. 
    """

    packets = []

    _initialized = False

    config = None

    def init(self, config):
        self.config = config
        self._initialized = True
        self.logger = logging.getLogger()
 
    def register_sender(self, sender):
        self.sender = sender

    packets = []
    def add(self, pack):
        self.packets.append(pack)

    def send(self):
        """Sends a response to scheduler"""
        if len(self.packets) > 0 :
            if not self.sender.send_locked :
                self._send()

    def _send(self):
        """Sends the response to scheduler"""
        packet = self.packets[0]
        del self.packets[0]
        self.sender.call_remote(packet)
        logging.getLogger().debug("Remaining requests to send: %d" % (len(self.packets))) 

    @initialized
    def backup_buffer(self):
        """
        When the scheduler-proxy service ends, internal buffer may contain
        some responses to send. This runtime ensures a backup to temp file,
        which can be restored when sheduler-proxy starts.
        """
        if len(self.packets) > 0 :
            self.logger.info("XMLRPC Proxy: Backup the buffer with %d responses"
                    % len(self.packets))
            with open(self.config.scheduler_proxy_buffer_tmp, "wb") as fp :
                pickle.dump(self.packets, fp)

    @initialized
    def restore_buffer(self):
        """
        Restoring the backuped responses from a temp file.

        When the scheduler-proxy service starts, this runtime checks 
        the content of temp file for unsent responses.
        This content is moved to internal buffer to resend.
        """
        try: 
            if os.path.exists(self.config.scheduler_proxy_buffer_tmp):
                self.logger.info("XMLRPC Proxy: Restoring the buffer")
                
                with open(self.config.scheduler_proxy_buffer_tmp, "rb") as fp :
                    try:
                        content = pickle.load(fp)
                    except Exception, e:
                        self.logger.warn("XMLRPC Proxy: An error occured when restoring the buffer: %s" % str(e))
                    if isinstance(content, list):
                        self.packets.extend(content)
                    else:
                        self.logger.warn("XMLRPC Proxy: Invalid format of backup of buffer, operation ignored")
 
                    os.unlink(self.config.scheduler_proxy_buffer_tmp)
                    self.logger.info("XMLRPC Proxy: restore buffer with %d responses" % len(SendingBuffer().packets))
        except Exception, exc:
            self.logger.error("XMLRPC Proxy: buffer restore failed: %s"  % str(exc))


