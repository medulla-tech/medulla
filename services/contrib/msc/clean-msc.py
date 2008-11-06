#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from sqlalchemy import *
import sqlalchemy
import logging
import datetime

logger = logging.getLogger(sys.argv[0])
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def query_bundles_to_delete(commands, commands_on_host, creation_timestamp):
    """
    Get bundle and related commands to delete.
    A bundle is deleted only if all its commands can be deleted

    @rtype: list
    @returns: list of bundle ids and command ids to remove
    """
    if sqlalchemy.__version__.startswith('0.3'):
        to_delete = select([commands.c.fk_bundle, commands.c.id], and_(commands_on_host.c.fk_commands == commands.c.id, commands_on_host.c.current_state.in_(*['done', 'failed']), commands.c.fk_bundle != None, commands.c.creation_date < creation_timestamp ), distinct = True)
    else:
        to_delete = select([commands.c.fk_bundle, commands.c.id]).select_from(commands.join(commands_on_host)).where(and_(commands_on_host.c.current_state.in_(['done', 'failed']), commands.c.fk_bundle != None, commands.c.creation_date < creation_timestamp )).distinct()
    ret = to_delete.execute().fetchall()
    return ret

def query_commands_to_delete(commands, commands_on_host, creation_timestamp):
    """
    Get commands to delete, not part of a bundle

    @rtype: list
    @returns: list of command ids to delete
    """
    if sqlalchemy.__version__.startswith('0.3'):
        to_delete = select([commands.c.id], and_(commands_on_host.c.fk_commands == commands.c.id, commands_on_host.c.current_state.in_(*['done', 'failed']), commands.c.fk_bundle == None, commands.c.creation_date < creation_timestamp), distinct = True)
    else:
        to_delete = select([commands.c.id]).select_from(commands.join(commands_on_host)).where(and_(commands_on_host.c.current_state.in_(['done', 'failed']), commands.c.fk_bundle == None, commands.c.creation_date < creation_timestamp )).distinct()
    ret = to_delete.execute().fetchall()
    return ret

def run_query(msg, connection, query):
    logger.info(msg)
    ret = connection.execute(query)
    logger.info('Count of deleted rows: %ld' % ret.rowcount)
    
def msc_delete(connection, bundles_to_delete, commands_to_delete, bundle, commands, target, commands_on_host, commands_history):
    if sqlalchemy.__version__.startswith('0.3'):
        in_coh_op = commands_on_host.c.fk_commands.in_(*commands_to_delete)
        in_c_op = commands.c.id.in_(*commands_to_delete)
        in_b_op = bundle.c.id.in_(*bundles_to_delete)
    else:
        in_coh_op = commands_on_host.c.fk_commands.in_(commands_to_delete)
        in_c_op = commands.c.id.in_(commands_to_delete)
        in_b_op = bundle.c.id.in_(bundles_to_delete)

    query = commands_history.delete(commands_history.c.fk_commands_on_host.in_(select([commands_on_host.c.id], in_coh_op)))
    run_query('Purging commands_history table', connection, query)
    
    query = target.delete(target.c.id.in_(select([commands_on_host.c.fk_target], in_coh_op)))
    run_query('Purging target table', connection, query)
    
    query = commands_on_host.delete(in_coh_op)
    run_query('Purging commands_on_host table', connection, query)

    query = commands.delete(in_c_op)
    run_query('Purging commands table', connection, query)

    if bundles_to_delete:
        query = bundle.delete(in_b_op)
        run_query('Purging bundle table', connection, query)

def usage(argv):
    print >> sys.stderr, 'Usage: %s <db_conn_string> <days>' % argv[0]
    print >> sys.stderr, 'Where db_conn_string is a SQLAlchemy connection string, e.g. mysql://user:password@host/database'
    print >> sys.stderr, 'Where days is a positive integer specifying from which age the commands should be purged, e.g. 30 for 30 days'
    return 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(usage(sys.argv))

    try:
        days = int(sys.argv[2])
        if not days:
            raise ValueError
    except:
        sys.exit(usage(sys.argv))
    
    mysql_db = create_engine(sys.argv[1])    
    metadata = MetaData(mysql_db)

    bundle = Table('bundle',
                   metadata,
                   autoload = True)
    commands = Table('commands',
                     metadata,
                     Column('fk_bundle', Integer, ForeignKey('bundle.id')),
                     autoload = True)
    target = Table("target",
                   metadata,
                   autoload = True)
    commands_on_host = Table('commands_on_host',
                             metadata,
                             Column('fk_commands', Integer, ForeignKey('commands.id')),
                             Column('fk_target', Integer, ForeignKey('target.id')),
                             autoload = True)
    commands_history = Table("commands_history",
                             metadata,
                             Column('fk_commands_on_host', Integer, ForeignKey('commands_on_host.id')),
                             autoload = True)

    creation_timestamp =  datetime.datetime.now() - datetime.timedelta(days)
    cids = query_commands_to_delete(commands, commands_on_host, creation_timestamp)
    commands_to_delete = map(lambda x: x[0], cids)
    
    bcids = query_bundles_to_delete(commands, commands_on_host, creation_timestamp)
    commands_to_delete.extend(map(lambda x: x[1], bcids))
    bundles_to_delete = map(lambda x: x[0], bcids)

    logger.info("Number of commands to delete: %d", len(commands_to_delete))
    logger.info("Number of bundles to delete: %d", len(bundles_to_delete))

    if commands_to_delete:
        # Start transaction
        connection = mysql_db.connect()
        trans = connection.begin()
        msc_delete(connection, bundles_to_delete, commands_to_delete, bundle, commands, target, commands_on_host, commands_history)
        trans.commit()
    else:
        logger.info("No purge to do")

