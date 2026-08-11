# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import sessionmaker


class PullTargets(object):
    """Targets for DLP"""

    def flush(self):
        """Handle SQL flushing"""
        # Get session from parent module's session factory
        from pulse2.database.msc import MscDatabase
        msc_db = MscDatabase()
        if msc_db.is_activated:
            session_factory = sessionmaker(bind=msc_db.engine_mscmmaster_base, expire_on_commit=False)
            session = session_factory()
            try:
                session.add(self)
                session.flush()
            finally:
                session.close()
        else:
            # Database not initialized
            pass
