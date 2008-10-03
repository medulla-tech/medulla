#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from sqlalchemy import *
import logging

# Set up logging
logger = logging.getLogger(sys.argv[0])
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def deleteOldInventories(inventory):
    """
    Clean up the Inventory table, i.e. delete old inventories (Last != 1)
    """
    to_delete = inventory.delete(inventory.c.Last != 1)
    logger.debug("deleteOldInventories: SQL request: %s" % to_delete)
    to_delete.execute()


def deleteHasTablesMissingInventories(inventory):
    """
    Remove every linked tables (has*) rows referencing missing
    inventories
    """
    for table in tables_elements:
        has_table = Table("has" + table, metadata, autoload = True)

        inventory_ids = select([inventory.c.id])

        to_delete = has_table.delete(not_(has_table.c.inventory.in_(inventory_ids)))
        logger.debug("deleteHasTablesMissingInventories: on table %s: SQL request: %s" % (table, str(to_delete).replace('\n', ' ')))
        to_delete.execute()


def deleteHasTablesMissingMachines(machine):
    """
    Remove every linked tables (has*) rows referencing missing machines
    """
    for table in tables_elements:
        has_table = Table("has" + table, metadata, autoload = True)

        machine_ids = select([machine.c.id])

        to_delete = has_table.delete(not_(has_table.c.machine.in_(machine_ids)))
        logger.debug("deleteHasTablesMissingMachines: on table %s: SQL request: %s" % (table, str(to_delete).replace('\n', ' ')))
        to_delete.execute()


def cleanUpInventoryParts(inventory):
    """
    Clean up the inventory parts tables (Bios/hasBios, Drive/hasDrive etc)
    """
    for table in tables_elements:

        # First we look for inventory parts not linked to any has*
        element = Table(table, metadata, autoload = True)
        has_table = Table("has" + table, metadata, autoload = True)

        has_table_ids = select([getattr(has_table.c, table.lower())])

        to_delete = element.delete(not_(element.c.id.in_(has_table_ids)))
        logger.debug("cleanUpInventoryParts: on table %s: SQL request: %s" % (table, str(to_delete).replace('\n', ' ')))
        to_delete.execute()

        # Next, we look for the opposite : part / inventory links pointing
        # to missing inventory parts
        element_ids = select([element.c.id])

        to_delete = has_table.delete(not_(getattr(has_table.c, table.lower()).in_(element_ids)))
        logger.debug("cleanUpInventoryParts: on table %s: SQL request: %s" % (table, str(to_delete).replace('\n', ' ')))
        to_delete.execute()


def deleteEmptyInventories(inventory):
    """
    Check there are no empty inventories (i.e. Inventory rows not
    referenced by any has* row)
    """
    #First, build up the union for every machine in the has* tables
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

    # The inventory tables we wish to purge
    tables_elements = ["Bios", "BootDisk", "BootGeneral", "BootMem", "BootPCI", "BootPart", "Controller", "Custom", "Drive", "Entity", "Hardware", "Input", "Memory", "Modem", "Monitor", "Network", "Pci", "Port", "Printer", "Registry", "Slot", "Software", "Sound", "Storage", "VideoCard"]

    inventory = Table("Inventory", metadata, autoload = True)
    machine = Table("Machine", metadata, autoload = True)

    logger.info("Deleting old inventories...")
    deleteOldInventories(inventory)
    logger.info("Done !")

    logger.info("Deleting rows with missing inventories...")
    deleteHasTablesMissingInventories(inventory)
    logger.info("Done !")

    logger.info("Deleting rows with missing inventories...")
    deleteHasTablesMissingMachines(machine)
    logger.info("Done !")

    logger.info("Cleaning up inventory parts...")
    cleanUpInventoryParts(inventory)
    logger.info("Done !")

    logger.info("Deleting empty inventories...")
    deleteEmptyInventories(inventory)
    logger.info("Done !")
