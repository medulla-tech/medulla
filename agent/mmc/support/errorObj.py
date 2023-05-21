# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

"""
Contains the errorMessage Class.
FIXME: deprecated ?
"""

import logging
import re


class errorMessage:
    def __init__(self, funcName, message=""):
        self.funcName = funcName
        self.message = message

    def addMessage(self, message):
        if self.message:
            self.message = self.message + "\n"
        self.message = self.message + str(message)

    def errorArray(self):
        logger = logging.getLogger()
        if not logger.handlers:
            # No handler defined
            # We create a default handler that writes to stderr
            logger.addHandler(logging.StreamHandler())
        logger.error(f"__call {self.funcName}" + "\n" + self.message)

        self.message = re.sub("\n", "<br />\n", self.message)
        return {"errorFuncNameXMLRPC": self.funcName, "errorCodeXMLRPC": self.message}
