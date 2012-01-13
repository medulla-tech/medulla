--
-- (c) 2008 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Pulse 2, http://pulse2.mandriva.org
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

START TRANSACTION;

-- Too short fields
ALTER TABLE `Drive` CHANGE `VolumeName` `VolumeName` VARCHAR(32) DEFAULT NULL;

-- Missing indexes: see http://pulse2.mandriva.org/ticket/444
CREATE INDEX machine ON hasRegistry(machine);
CREATE INDEX inventory ON hasRegistry(inventory);
CREATE INDEX registry ON hasRegistry(registry);
CREATE INDEX path ON hasRegistry(path);

-- hasPci lacks some indexes
CREATE INDEX machine ON hasPci(machine);
CREATE INDEX inventory ON hasPci(inventory);
CREATE INDEX pci ON hasPci(pci);

-- hasSoftware has some duplicated indexes
ALTER TABLE `hasSoftware` DROP INDEX `hassoft_machine_idx`;
ALTER TABLE `hasSoftware` DROP INDEX `hassoft_inventory_idx`;
ALTER TABLE `hasSoftware` DROP INDEX `hassoft_software_idx`;

-- By default an entity is linked to the root entity (1)
ALTER TABLE Entity CHANGE `parentId` `parentId` INT UNSIGNED NOT NULL DEFAULT 1;
ALTER TABLE Entity ADD FOREIGN KEY (parentId) REFERENCES Entity(id);

-- Change some data definition in hasEntity
ALTER TABLE hasEntity CHANGE machine machine MEDIUMINT UNSIGNED NOT NULL;
ALTER TABLE hasEntity CHANGE entity entity INT UNSIGNED NOT NULL DEFAULT 1;
ALTER TABLE hasEntity CHANGE inventory inventory INT UNSIGNED NOT NULL;
ALTER TABLE hasEntity DROP PRIMARY KEY, ADD PRIMARY KEY (machine, entity, inventory);
CREATE INDEX machine ON hasEntity(machine);
CREATE INDEX entity ON hasEntity(entity);
CREATE INDEX inventory ON hasEntity(inventory);

-- User table for users/entities link
CREATE TABLE User (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  uid VARCHAR(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (uid)
) ENGINE=MYISAM;

-- User to entites table
CREATE TABLE UserEntities (
  fk_User INT UNSIGNED NOT NULL,
  fk_Entity INT UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (fk_User, fk_Entity),
  FOREIGN KEY (fk_User) REFERENCES User(id),
  FOREIGN KEY (fk_Entity) REFERENCES Entity(id)
) ENGINE=MYISAM;

-- Initialize the Entity table with the root entity
INSERT INTO Entity (Label, parentId) VALUES ("root", 1);

-- Some columns are too small to contain the data
ALTER TABLE `Storage` CHANGE `VolumeName` `VolumeName` VARCHAR(64) DEFAULT NULL;
ALTER TABLE `Storage` CHANGE `Model` `Model` VARCHAR(64) DEFAULT NULL;
ALTER TABLE `Slot` CHANGE `Connector` `Connector` VARCHAR(64) DEFAULT NULL;

--
-- Database version
--

TRUNCATE Version;
INSERT INTO Version VALUES( '9' );

COMMIT;

