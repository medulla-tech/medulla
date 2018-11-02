--
-- (c) 2018 Siveo, http://www.siveo.net/
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


--

-- manage custom qa for grp
-- table for command

START TRANSACTION;

CREATE TABLE IF NOT EXISTS `xmppmaster`.`command_qa` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `command_name` VARCHAR(45) NULL,
  `command_action` VARCHAR(500) NOT NULL,
  `command_login` VARCHAR(45) NOT NULL,
  `command_os` VARCHAR(45) NULL,
  `command_start` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  `command_grp` VARCHAR(45) NULL DEFAULT NULL,
  `command_machine` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC));


CREATE TABLE IF NOT EXISTS `xmppmaster`.`command_action` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `command_id` INT NOT NULL,
  `session_id` VARCHAR(45) NOT NULL,
  `command_result` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`));


ALTER TABLE `xmppmaster`.`command_action`
ADD COLUMN `date` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP AFTER `id`;

ALTER TABLE `xmppmaster`.`command_action`
ADD COLUMN `typemessage` VARCHAR(20) NOT NULL DEFAULT 'log' AFTER `session_id`;

ALTER TABLE  `xmppmaster`.`command_action`
ADD COLUMN `target` VARCHAR(45) NOT NULL AFTER `command_result`;

UPDATE version SET Number = 14;

COMMIT;
