# -*- coding: utf-8; -*-
#
# (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
# (c) 2007-2009 Mandriva, http://www.mandriva.com/
#
# $Id$
#
# This file is part of Pulse 2, http://pulse2.mandriva.org
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# uses SA to handle sessions
import sqlalchemy.orm

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
            'stderr': self.stderr,
            'stdout': self.stdout,
            'error_code': self.error_code,
            'state': self.state
        }

    def flush(self):
        """ Handle SQL flushing """
        session = sqlalchemy.orm.create_session()
        session.add(self)
        session.flush()
        session.close()

