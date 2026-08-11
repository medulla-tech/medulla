# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from packaging.version import Version
from sqlalchemy import __version__

MIN_VERSION = "0.6.3"  # Debian Squeeze version
MAX_VERSION = "2.0.46"  # SQLAlchemy 2.0 compatible
CUR_VERSION = __version__


def checkSqlalchemy():
    """
    Check if the provided version of sqlalchemy is suitable for mmc-core
    """
    return (
        Version(MIN_VERSION)
        <= Version(CUR_VERSION)
        <= Version(MAX_VERSION)
    )
