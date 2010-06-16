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
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

SET storage_engine=INNODB;
SET GLOBAL character_set_server=UTF8;
SET SESSION character_set_server=UTF8;

START TRANSACTION;

CREATE TABLE Version (
  Number tinyint(4) unsigned NOT NULL default '0'
);

INSERT INTO Version VALUES( '1' );

-- link tables
-- PackageServerEntity
CREATE TABLE PackageServerEntity (
    entity_uuid Text NOT NULL,
    package_server_uuid Text NOT NULL
);

-- ----------------------------------------------------------------------
-- Add unicity constraints
-- ----------------------------------------------------------------------
ALTER TABLE PackageServerEntity                 ADD UNIQUE (entity_uuid(50), package_server_uuid(50));

-- ----------------------------------------------------------------------
-- Add foreign constraints
-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Add indexes
-- ----------------------------------------------------------------------
CREATE INDEX entity_uuid_idx ON PackageServerEntity(entity_uuid(50));
CREATE INDEX package_server_uuid_idx ON PackageServerEntity(package_server_uuid(50));

-- ----------------------------------------------------------------------
-- Insert data
-- ----------------------------------------------------------------------

COMMIT;
