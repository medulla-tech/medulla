# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# SPDX-FileCopyrightText: 2007-2009 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

# uses SA to handle sessions
import sqlalchemy.orm
from base64 import b64encode

""" Class to map msc.commands_history to SA
"""
class CommandsHistory(object):
    """ Mapping between msc.commands_history and SA
    """
    def toH(self):
        return {
            'id': self.id,
            'fk_commands_on_host': self.fk_commands_on_host,
            'date': self.date,
            'stderr': b64encode(self.stderr.encode('utf-8', 'ignore')),
            'stdout': b64encode(self.stdout.encode('utf-8', 'ignore')),
            'error_code': self.error_code,
            'state': self.state,
            'phase': self.phase
        }

    def flush(self):
        """ Handle SQL flushing """
        session = sqlalchemy.orm.create_session()
        session.add(self)
        session.flush()
        session.close()
