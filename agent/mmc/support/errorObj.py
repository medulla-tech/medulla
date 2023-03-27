# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

"""
Contains the errorMessage Class.
FIXME: deprecated ?
"""

import logging
import re

class errorMessage:
    def __init__(self,funcName, message = ''):
      self.funcName = funcName
      self.message = message

    def addMessage(self,message):
      if (self.message):
        self.message=self.message+"\n"
      self.message=self.message+str(message)

    def errorArray(self):
        logger = logging.getLogger()
        if not logger.handlers:
            # No handler defined
            # We create a default handler that writes to stderr
            logger.addHandler(logging.StreamHandler())
        logger.error(f"__call {self.funcName}" + "\n" + self.message)

        self.message=re.sub('\n',"<br />\n",self.message)
        return {'errorFuncNameXMLRPC': self.funcName, 'errorCodeXMLRPC': self.message}
