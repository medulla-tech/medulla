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
    from sqlalchemy import create_engine, MetaData, Table, select, and_, __version__
except ImportError:
    print "SqlAlchemy was not found, please install it !"
    sys.exit(1)

def usage(argv):
    print >> sys.stderr, 'Usage: %s db_conn_string [--id entity_id|--name entity_name]' % argv[0]
    print >> sys.stderr, 'Where db_conn_string is a SQLAlchemy connection string, e.g. mysql://user:password@host/database'
    return 1

if __name__ == "__main__":
    if len(sys.argv) != 2 and len(sys.argv) != 4:
        sys.exit(usage(sys.argv))

    if not __version__.startswith('0.4'):
        print "Wrong version of SqlAlchemy found, please install a 0.4 version !"
        sys.exit(1)

    get_entity = False
    if len(sys.argv) == 4:
        if sys.argv[2] == '--id':
            id_entity = sys.argv[3]
            get_entity = True
        elif sys.argv[2] == '--name':
            id_entity = -1
            name_entity = sys.argv[3]
            get_entity = True
        else:
            print "dont know this option : %s" % sys.argv[2]
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
    
    entity_id = 1
    if get_entity:
        ent = []
        if id_entity != -1:
            ent = select([entity.c.id], and_(entity.c.id == id_entity)).execute().fetchall()
        else:
            ent = select([entity.c.id], and_(entity.c.Label == name_entity)).execute().fetchall()
        if ent == None or len(ent) == 0:
            print "Cant get the required entity"
            sys.exit(1)
        entity_id = ent[0][0]

    into_hasentity = []
    for computer in computers:
        into_hasentity.append({'machine' : computer[1], 'entity' : entity_id, 'inventory': computer[0]})
    connection.execute(hasentity.insert(), into_hasentity)
    
