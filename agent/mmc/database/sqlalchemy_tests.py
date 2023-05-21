# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

from distutils.version import StrictVersion
from sqlalchemy import __version__

MIN_VERSION = "0.6.3"  # Debian Squeeze version
MAX_VERSION = "1.4.46"  # Debian Bookworm version
CUR_VERSION = __version__


def checkSqlalchemy():
    """
    Check if the provided version of sqlalchemy is suitable for mmc-core
    """
    return (
        StrictVersion(MIN_VERSION)
        <= StrictVersion(CUR_VERSION)
        <= StrictVersion(MAX_VERSION)
    )
