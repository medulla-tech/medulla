# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

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
        self.funcname = f"{obj.__class__.__name__}::{f.f_code.co_name}"
        callStr = f"{self.funcname}::{str(f.f_lineno)}"
        nkargs = [str(item) for item in kargs]
        logger.exception(f"{callStr} " + " ".join(nkargs))
