--
-- (c) 2016 Siveo, http://www.siveo.net/
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

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

UPDATE version SET Number = 5;

- -----------------------------------------------------
-- Table `logs add infos in logs`
-- -----------------------------------------------------
ALTER TABLE `xmppmaster`.`logs` 
ADD COLUMN `how` VARCHAR(255) NULL DEFAULT '""' AFTER `who`,
ADD COLUMN `why` VARCHAR(255) NULL DEFAULT '""' AFTER `how`,
ADD COLUMN `module` VARCHAR(45) NULL DEFAULT 'xmpp' AFTER `why`,
ADD COLUMN `from` VARCHAR(45) NULL DEFAULT '""' AFTER `module`,
ADD COLUMN `to` VARCHAR(45) NULL DEFAULT '""' AFTER `from`,
ADD COLUMN `action` VARCHAR(45) NULL DEFAULT '""' AFTER `to`;

- -----------------------------------------------------
-- Table `logs modify position champ`
-- -----------------------------------------------------
ALTER TABLE `xmppmaster`.`logs` 
CHANGE COLUMN `date` `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `id`,
CHANGE COLUMN `from` `from` VARCHAR(45) NULL DEFAULT NULL AFTER `date`,
CHANGE COLUMN `to` `to` VARCHAR(45) NULL DEFAULT NULL AFTER `from`,
CHANGE COLUMN `action` `action` VARCHAR(45) NULL DEFAULT NULL AFTER `to`,
CHANGE COLUMN `module` `module` VARCHAR(45) NULL DEFAULT 'xmpp' AFTER `type`,
CHANGE COLUMN `how` `how` VARCHAR(255) NULL DEFAULT '""' AFTER `sessionname`,
CHANGE COLUMN `priority` `priority` INT(11) NULL DEFAULT '0' AFTER `why`;
