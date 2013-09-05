--
-- (c) 2010 Mandriva, http://www.mandriva.com/
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
-- along with MMC.  If not, see <http://www.gnu.org/licenses/>.

START TRANSACTION;

-- Transform all integer field to int(11)
ALTER TABLE  `Bios` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `BootDisk` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `BootGeneral` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `BootMem` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `BootPart` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `BootPCI` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `Controller` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `Custom` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `CustomField` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `Entity` CHANGE  `parentId`  `parentId` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '1';
ALTER TABLE  `hasBios` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBios` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootDisk` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootDisk` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootGeneral` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootGeneral` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootMem` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootMem` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootPart` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootPart` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootPCI` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasBootPCI` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasController` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasController` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasCustom` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasCustom` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasDrive` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasDrive` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasEntity` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL ;
ALTER TABLE  `hasHardware` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasHardware` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasInput` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasInput` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasInventoryDebugLog` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasInventoryDebugLog` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasMemory` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasMemory` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasModem` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasModem` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasMonitor` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasMonitor` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasNetwork` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasNetwork` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasPci` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasPci` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasPort` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasPort` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasPrinter` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasPrinter` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasRegistry` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasRegistry` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasSlot` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasSlot` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasSoftware` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasSoftware` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasSound` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasSound` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasStorage` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasStorage` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasVideoCard` CHANGE  `machine`  `machine` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `hasVideoCard` CHANGE  `inventory`  `inventory` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '0';
ALTER TABLE  `Inventory` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `Machine` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `Machine` CHANGE  `lastId`  `lastId` INT( 11 ) UNSIGNED NULL DEFAULT NULL ;
ALTER TABLE  `Machine` CHANGE  `lastBootId`  `lastBootId` INT( 11 ) UNSIGNED NULL DEFAULT NULL ;
ALTER TABLE  `Machine` CHANGE  `lastCustomId`  `lastCustomId` INT( 11 ) UNSIGNED NULL DEFAULT NULL ;
ALTER TABLE  `Machine` CHANGE  `lastNmapId`  `lastNmapId` INT( 11 ) UNSIGNED NULL DEFAULT NULL ;
ALTER TABLE  `Memory` CHANGE  `Size`  `Size` INT( 11 ) NULL DEFAULT NULL ;
ALTER TABLE  `User` CHANGE  `id`  `id` INT( 11 ) UNSIGNED NOT NULL AUTO_INCREMENT ;
ALTER TABLE  `UserEntities` CHANGE  `fk_User`  `fk_User` INT( 11 ) UNSIGNED NOT NULL ;
ALTER TABLE  `UserEntities` CHANGE  `fk_Entity`  `fk_Entity` INT( 11 ) UNSIGNED NOT NULL DEFAULT  '1';


DELETE FROM Version;
INSERT INTO Version VALUES('12');

COMMIT;
