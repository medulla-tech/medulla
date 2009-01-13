#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2008 Mandriva, http://www.mandriva.com/
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

import sys

try:
    from sqlalchemy import *
except ImportError:
    print "SqlAlchemy was not found, please install it !"
    sys.exit(1)

import sqlalchemy
import logging

def usage(argv):
    print >> sys.stderr, 'Usage: %s [db_conn_string]' % argv[0]
    print >> sys.stderr, 'Where db_conn_string is a SQLAlchemy connection string, e.g. mysql://user:password@host/database'
    return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(usage(sys.argv))

    if not sqlalchemy.__version__.startswith('0.4'):
        print "Wrong version of SqlAlchemy found, please install a 0.4 version !"
        sys.exit(1)

    mysql_db = create_engine(sys.argv[1])
    metadata = MetaData(mysql_db)
    connection = mysql_db.connect()

    inventory = Table("Inventory", metadata, autoload = True)
    machine = Table("Machine", metadata, autoload = True)
    entity = Table("Entity", metadata, autoload = True)
    hasentity = Table("hasEntity", metadata, autoload = True)
    hashardware = Table("hasHardware", metadata, autoload = True)

    computers = select([inventory.c.id, machine.c.id], and_(machine.c.id == hashardware.c.machine, hashardware.c.inventory == inventory.c.id, inventory.c.Last == 1)).execute().fetchall()

    into_hasentity = []
    for computer in computers:
        into_hasentity.append({'machine' : computer[1], 'entity' : 1, 'inventory': computer[0]})
    connection.execute(hasentity.insert(), into_hasentity)
    
