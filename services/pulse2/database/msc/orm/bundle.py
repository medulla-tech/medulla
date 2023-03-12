# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

""" Class to map msc.bundle to SA
"""


class Bundle(object):
    """Mapping between msc.bundle and SA"""

    def getId(self):
        return self.id

    def toH(self):
        return {"id": self.id, "title": self.title}
