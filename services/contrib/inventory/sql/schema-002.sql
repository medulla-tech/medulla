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

ALTER TABLE Inventory ADD COLUMN Last int(2) NOT NULL DEFAULT 0;

--
-- Table structure for table `Registry`
--

CREATE TABLE Registry (
  id int(11) unsigned NOT NULL auto_increment,
  Value varchar(128) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `nomRegistryKey`
--

CREATE TABLE nomRegistryPath (
  id int(11) unsigned NOT NULL auto_increment,
  Path varchar(128) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `hasRegistry`
--

CREATE TABLE hasRegistry (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  registry int(11) unsigned NOT NULL default '0',
  path int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,registry,path)
) ENGINE=MYISAM;


ALTER TABLE Software MODIFY ProductName VarChar(256) default NULL;
ALTER TABLE Controller MODIFY StandardType VarChar(32) default NULL;
ALTER TABLE Storage MODIFY StandardType VarChar(32) default NULL;
ALTER TABLE Slot MODIFY PortType VarChar(32) default NULL;

--
-- Database version
--
TRUNCATE Version;
INSERT INTO Version VALUES( '2' );


