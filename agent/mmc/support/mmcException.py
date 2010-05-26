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
Class for MMC exceptions
"""

import logging
import sys

class mmcException(Exception):

    def __init__(self, *kargs):
        Exception.__init__(self, kargs)
        logger = logging.getLogger()
        if not logger.handlers:
            # No handler defined
            # We create a default handler that writes to stderr
            logger.addHandler(logging.StreamHandler())
        f = sys.exc_info()[2].tb_frame
        obj = f.f_locals.get("self", None)
        self.funcname = obj.__class__.__name__+"::"+f.f_code.co_name
        callStr = self.funcname + "::" + str(f.f_lineno)
        nkargs = []
        for item in kargs:
            nkargs.append(str(item))
        logger.exception(callStr + " " + " ".join(nkargs))





