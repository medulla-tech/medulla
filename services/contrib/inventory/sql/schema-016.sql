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
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

-- Change MyISAM motor to InnoDB

ALTER TABLE `Bios` ENGINE = innodb;
ALTER TABLE `Controller` ENGINE = innodb;
ALTER TABLE `CustomField` ENGINE = innodb;
ALTER TABLE `Drive` ENGINE = innodb;
ALTER TABLE `Hardware` ENGINE = innodb;
ALTER TABLE `Input` ENGINE = innodb;
ALTER TABLE `Inventory` ENGINE = innodb;
ALTER TABLE `Machine` ENGINE = innodb;
ALTER TABLE `Memory` ENGINE = innodb;
ALTER TABLE `Modem` ENGINE = innodb;
ALTER TABLE `Monitor` ENGINE = innodb;
ALTER TABLE `Network` ENGINE = innodb;
ALTER TABLE `Pci` ENGINE = innodb;
ALTER TABLE `Port` ENGINE = innodb;
ALTER TABLE `Printer` ENGINE = innodb;
ALTER TABLE `Slot` ENGINE = innodb;
ALTER TABLE `Software` ENGINE = innodb;
ALTER TABLE `Sound` ENGINE = innodb;
ALTER TABLE `Storage` ENGINE = innodb;
ALTER TABLE `Version` ENGINE = innodb;
ALTER TABLE `VideoCard` ENGINE = innodb;
ALTER TABLE `hasBios` ENGINE = innodb;
ALTER TABLE `hasController` ENGINE = innodb;
ALTER TABLE `hasDrive` ENGINE = innodb;
ALTER TABLE `hasHardware` ENGINE = innodb;
ALTER TABLE `hasInput` ENGINE = innodb;
ALTER TABLE `hasMemory` ENGINE = innodb;
ALTER TABLE `hasModem` ENGINE = innodb;
ALTER TABLE `hasMonitor` ENGINE = innodb;
ALTER TABLE `hasNetwork` ENGINE = innodb;
ALTER TABLE `hasPci` ENGINE = innodb;
ALTER TABLE `hasPort` ENGINE = innodb;
ALTER TABLE `hasPrinter` ENGINE = innodb;
ALTER TABLE `hasSlot` ENGINE = innodb;
ALTER TABLE `hasSoftware` ENGINE = innodb;
ALTER TABLE `hasSound` ENGINE = innodb;
ALTER TABLE `hasStorage` ENGINE = innodb;
ALTER TABLE `hasVideoCard` ENGINE = innodb;
ALTER TABLE `Registry` ENGINE = innodb;
ALTER TABLE `nomRegistryPath` ENGINE = innodb;
ALTER TABLE `hasRegistry` ENGINE = innodb;
ALTER TABLE `Entity` ENGINE = innodb;
ALTER TABLE `hasEntity` ENGINE = innodb;
ALTER TABLE `User` ENGINE = innodb;
ALTER TABLE `UserEntities` ENGINE = innodb;
ALTER TABLE `InventoryDebugLog` ENGINE = innodb;
ALTER TABLE `hasInventoryDebugLog` ENGINE = innodb;
ALTER TABLE `RightUserEntities` ENGINE = innodb;

UPDATE Version SET Number = 16;