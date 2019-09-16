--
-- (c) 2019 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://www.siveo.net/
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
-- insert item params_json  parameters deployement general

START TRANSACTION;

SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

-- Add new parameters for wolImaging support
ALTER TABLE  `Entity` ADD  `isWolImaging` VARCHAR( 255 ) NOT NULL DEFAULT 'false';

UPDATE version SET Number = 22;

COMMIT;

