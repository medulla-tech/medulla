# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-2.0-or-later

from sqlalchemy.orm import create_session


class PullTargets(object):
    """Targets for DLP"""

    def flush(self):
        """Handle SQL flushing"""
        session = create_session()
        session.add(self)
        session.flush()
        session.close()
