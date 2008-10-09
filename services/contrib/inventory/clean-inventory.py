#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from sqlalchemy import *
import logging

# The inventory tables we wish to purge
tables_elements = ["Bios", "BootDisk", "BootGeneral", "BootMem", "BootPCI", "BootPart", "Controller", "Custom", "Drive", "Entity", "Hardware", "Input", "Memory", "Modem", "Monitor", "Network", "Pci", "Port", "Printer", "Registry", "Slot", "Software", "Sound", "Storage", "VideoCard"]

# Set up logging
logger = logging.getLogger(sys.argv[0])
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def deleteOldInventories(inventory):
    """
    Clean up the Inventory table, i.e. delete old inventories (Last != 1)
    """
    to_delete = map(lambda x: x['id'], inventory.select(inventory.c.Last != 1).execute().fetchall())
    if len(to_delete) > 0:
        logger.info("deleteOldInventories : will purge %d inventories" % len(to_delete))
        for i in range(0, 1+len(to_delete)/1000): # delete by 1000-pack
            inventory.delete(inventory.c.id.in_(*to_delete[i*1000:(i+1)*1000])).execute()
            logger.info("deleteOldInventories : done %d%%" % (i * 100 / (1+len(to_delete)/1000)))
        logger.debug("deleteOldInventories : purged inventories : %s" % to_delete)
    else:
        logger.info("deleteOldInventories : no inventory to purge")

def deleteHasTablesMissingInventories(inventory):
    """
    Remove every linked tables (has*) rows referencing missing
    inventories
    """

    for table in tables_elements:
        has_table = Table("has" + table, metadata, autoload = True)

        to_delete = map(lambda x: x['inventory'], # I may use list(set()) to deduplicate entries, but it would fake the real number of delete rows (one ID may lead to several rows deleted)
            outerjoin(has_table, inventory, has_table.c.inventory == inventory.c.id).\
            select(inventory.c.id == None).\
            execute().\
            fetchall()
        )

        if len(to_delete) > 0:
            logger.info("deleteHasTablesMissingInventories : on table has%s: will purge %d rows" % (table, len(to_delete)))
            to_delete = list(set(to_delete)) # now I may deduplicate my IDs
            for i in range(0, 1+len(to_delete)/1000): # delete by 1000-pack
                has_table.delete(has_table.c.inventory.in_(*to_delete[i*1000:(i+1)*1000])).execute()
                logger.info("deleteHasTablesMissingInventories : done %d%% in has%s" % ((i * 100 / (1+len(to_delete)/1000)), table))
            logger.debug("deleteHasTablesMissingInventories : on table has%s : purged rows : %s" % (table, to_delete))
        else:
            logger.info("deleteHasTablesMissingInventories : on table has%s: no rows to purge" % (table))

def deleteHasTablesMissingMachines(machine):
    """
    Remove every linked tables (has*) rows referencing missing machines
    """

    for table in tables_elements:
        has_table = Table("has" + table, metadata, autoload = True)

        to_delete = map(lambda x: x['machine'], # I may use list(set()) to deduplicate entries, but it would fake the real number of delete rows (one ID may lead to several rows deleted)
            outerjoin(has_table, machine, has_table.c.machine == machine.c.id).\
            select(machine.c.id == None).\
            execute().\
            fetchall()
        )

        if len(to_delete) > 0:
            logger.info("deleteHasTablesMissingMachines : on table has%s: will purge %d rows" % (table, len(to_delete)))
            to_delete = list(set(to_delete)) # now I may deduplicate my IDs
            for i in range(0, 1+len(to_delete)/1000): # delete by 1000-pack
                has_table.delete(has_table.c.machine.in_(*to_delete[i*1000:(i+1)*1000])).execute()
                logger.info("deleteHasTablesMissingMachines : done %d%% in has%s" % ((i * 100 / (1+len(to_delete)/1000)), table))
            logger.debug("deleteHasTablesMissingMachines : on table cleanUpInventoryParts%s : purged rows : %s" % (table, to_delete))
        else:
            logger.info("deleteHasTablesMissingMachines : on table has%s: no rows to purge" % (table))

def cleanUpInventoryParts(inventory):
    """
    Clean up the inventory parts tables (Bios/hasBios, Drive/hasDrive etc)
    """
    for table in tables_elements:

        # First we look for inventory parts not linked to any has*
        element = Table(table, metadata, autoload = True)
        has_table = Table("has" + table, metadata, autoload = True)

        to_delete = map(lambda x: x['id'], # I may use list(set()) to deduplicate entries, but it would fake the real number of delete rows (one ID may lead to several rows deleted)
            outerjoin(element, has_table, has_table.c.get(table.lower()) == element.c.id).\
            select(has_table.c.get(table.lower()) == None).\
            execute().\
            fetchall()
        )

        if len(to_delete) > 0:
            logger.info("cleanUpInventoryParts : on table %s: will purge %d rows" % (table, len(to_delete)))
            to_delete = list(set(to_delete)) # now I may deduplicate my IDs
            for i in range(0, 1+len(to_delete)/1000): # delete by 1000-pack
                element.delete(element.c.id.in_(*to_delete[i*1000:(i+1)*1000])).execute()
                logger.info("cleanUpInventoryParts : done %d%% in %s" % ((i * 100 / (1+len(to_delete)/1000)), table))
            logger.debug("cleanUpInventoryParts : on table %s : purged rows : %s" % (table, to_delete))
        else:
            logger.info("cleanUpInventoryParts : on table %s: no rows to purge" % (table))

def deleteEmptyInventories(inventory):
    """
    Check there are no empty inventories (i.e. Inventory rows not
    referenced by any has* row)
    FIXME: to refactor
    """
    #First, build up the union for every machine in the has* tables

    return # security to prevent using this function

    all_inventories_select = []
    for table in tables_elements:
        has_table = Table("has" + table, metadata, autoload = True)
        all_inventories_select.append(select([has_table.c.inventory]))

    all_inventories = union(*all_inventories_select)
    to_delete = inventory.delete(not_(inventory.c.id.in_(all_inventories)))
    logger.debug("deleteEmptyInventories: SQL request: %s" % str(to_delete).replace('\n', ' '))
    to_delete.execute()

def usage(argv):
    print >> sys.stderr, 'Usage: %s [db_conn_string]' % argv[0]
    print >> sys.stderr, 'Where db_conn_string is a SQLAlchemy connection string, e.g. mysql://user:password@host/database'
    return 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit(usage(sys.argv))
    mysql_db = create_engine(sys.argv[1])
    metadata = MetaData(mysql_db)

    inventory = Table("Inventory", metadata, autoload = True)
    machine = Table("Machine", metadata, autoload = True)

    logger.info("Deleting old inventories...")
    deleteOldInventories(inventory)
    logger.info("Done !")

    logger.info("Deleting rows with missing inventories...")
    deleteHasTablesMissingInventories(inventory)
    logger.info("Done !")

    logger.info("Deleting rows with missing computers...")
    deleteHasTablesMissingMachines(machine)
    logger.info("Done !")

    logger.info("Cleaning up inventory parts...")
    cleanUpInventoryParts(inventory)
    logger.info("Done !")

    """
    logger.info("Deleting empty inventories...")
    deleteEmptyInventories(inventory)
    logger.info("Done !")
    """
