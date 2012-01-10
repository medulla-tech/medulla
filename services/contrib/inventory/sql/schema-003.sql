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

--
-- Table structure for table Entity
--

CREATE TABLE Entity(
    id int(11) unsigned NOT NULL auto_increment,
    Label varchar(128) default NULL,
    parentId int(11) unsigned,
    PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table hasEntity
--

CREATE TABLE hasEntity (
    machine mediumint(9) unsigned NOT NULL default '0',
    entity int(11) unsigned NOT NULL default '0',
    inventory mediumint(5) unsigned NOT NULL default '0',
    PRIMARY KEY (machine)
) ENGINE=MYISAM;

--
-- Database version
--
TRUNCATE Version;
INSERT INTO Version VALUES( '3' );


