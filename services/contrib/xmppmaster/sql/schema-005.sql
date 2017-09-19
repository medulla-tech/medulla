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

START TRANSACTION;

-- -----------------------------------------------------
-- Table `logs add infos in logs`
-- -----------------------------------------------------
ALTER TABLE `xmppmaster`.`logs`
ADD COLUMN `how` VARCHAR(255) NULL DEFAULT '' AFTER `sessionname`,
ADD COLUMN `why` VARCHAR(255) NULL DEFAULT '' AFTER `how`,
ADD COLUMN `module` VARCHAR(45) NULL DEFAULT '' AFTER `type`,
ADD COLUMN `fromuser` VARCHAR(45) NULL DEFAULT '' AFTER `date`,
ADD COLUMN `touser` VARCHAR(45) NULL DEFAULT '' AFTER `fromuser`,
ADD COLUMN `action` VARCHAR(45) NULL DEFAULT '' AFTER `touser`;

-- -----------------------------------------------------
-- Table `logs modify position champ`
-- -----------------------------------------------------
ALTER TABLE `xmppmaster`.`logs`
CHANGE COLUMN `date` `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `id`,
CHANGE COLUMN `priority` `priority` INT(11) NULL DEFAULT '0' AFTER `why`;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 5;

COMMIT;
