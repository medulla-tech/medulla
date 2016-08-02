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
ALTER TABLE `Memory` CHANGE `Frequency` `Frequency` VARCHAR(32) DEFAULT NULL;
ALTER TABLE `Bios` CHANGE `Chipset` `Chipset` VARCHAR(255) DEFAULT NULL;

-- Update Table for Xml Improving

ALTER TABLE Hardware ADD OsArchitecture VarChar(30) default NULL;
ALTER TABLE Hardware ADD OsSerialKey VarChar(32) default NULL;
ALTER TABLE Hardware ADD OsInstallationDate VarChar(20) default NULL;
ALTER TABLE Hardware ADD DefaultGateway VarChar(15) default NULL;
ALTER TABLE Hardware ADD LastLoggedUser VarChar(256) default NULL;
ALTER TABLE Hardware ADD DateLastLoggedUser VarChar(20) default NULL;

ALTER TABLE Bios ADD DateFirstSwitchOn VarChar(20) default NULL;
ALTER TABLE Bios ADD DateLastSwitchOn VarChar(20) default NULL;

ALTER TABLE Drive ADD CDDVDBurner VarChar(12) default NULL;

-- ALTER TABLE Software DROP Application;
-- ALTER TABLE Software DROP Type;
ALTER TABLE Software ADD InstallationDate VarChar(25) default NULL;
ALTER TABLE Software ADD TypePackage VarChar(8) default NULL;
ALTER TABLE Software ADD UninstallPath VarChar(256) default NULL;
ALTER TABLE Software ADD RateOfUse VarChar(5) default NULL;
ALTER TABLE Software ADD FolderSize VarChar(8) default NULL;
ALTER TABLE Software ADD Icon text default NULL;


-- Update Columm to accept new data type

ALTER TABLE Software CHANGE ExecutableSize ExecutableSize VarChar(16) default NULL;
ALTER TABLE Software CHANGE ProductVersion ProductVersion VarChar(128) default NULL;
ALTER TABLE Software CHANGE Company Company VarChar(64) default NULL;


-- Server Invetory Error
ALTER TABLE Hardware ADD Host VarChar(32) default NULL;


-- OCS Debug Logs

--
-- Table structure for table `InventoryDebugLog`
--
CREATE TABLE InventoryDebugLog (
  id int(11) unsigned NOT NULL auto_increment,
  DebugLog text default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `hasInventoryDebugLog`
--

CREATE TABLE hasInventoryDebugLog (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  inventorydebuglog int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,inventorydebuglog)
) ENGINE=MYISAM;

--
-- Database version
--

TRUNCATE Version;
INSERT INTO Version VALUES( '10' );

COMMIT;
