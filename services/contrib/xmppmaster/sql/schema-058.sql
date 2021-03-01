--
-- (c) 2021 Siveo, http://www.siveo.net/
--
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

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;
DELETE FROM `xmppmaster`.`machines` WHERE 1;
ALTER TABLE `xmppmaster`.`machines`
ADD COLUMN IF NOT EXISTS `glpi_description` VARCHAR(90) NULL DEFAULT '' AFTER `keysyncthing`,
ADD COLUMN IF NOT EXISTS `glpi_owner_firstname` VARCHAR(45) NULL DEFAULT '' AFTER `glpi_description`,
ADD COLUMN IF NOT EXISTS `glpi_owner_realname` VARCHAR(45) NULL DEFAULT '' AFTER `glpi_owner_firstname`,
ADD COLUMN IF NOT EXISTS `glpi_owner` VARCHAR(45) NULL DEFAULT '' AFTER `glpi_owner_realname`,
ADD COLUMN IF NOT EXISTS `glpi_entity_id` INT(11)  DEFAULT NULL AFTER `glpi_owner`,
ADD COLUMN IF NOT EXISTS `glpi_location_id` INT(11)  DEFAULT NULL AFTER `glpi_entity_id`,
ADD COLUMN IF NOT EXISTS `model` VARCHAR(45) NULL DEFAULT '' AFTER `glpi_location_id`,
ADD COLUMN IF NOT EXISTS `manufacturer` VARCHAR(45) NULL DEFAULT '' AFTER `model`;

CREATE TABLE IF NOT EXISTS  `glpi_entity` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `complete_name` varchar(512) NOT NULL,
    `name` varchar(45) NOT NULL,
    `glpi_id` int(11) NOT NULL,
    PRIMARY KEY (`id`))
    ENGINE=InnoDB DEFAULT CHARSET=utf8;

    -- optimise jointure machine
    ALTER TABLE `xmppmaster`.`glpi_entity`
ADD INDEX IF NOT EXISTS `index_glpi_id` (`glpi_id` ASC);



CREATE TABLE IF NOT EXISTS  `glpi_location` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `complete_name` varchar(512) NOT NULL,
    `name` varchar(45) NOT NULL,
    `glpi_id` int(11) NOT NULL,
    PRIMARY KEY (`id`))
     ENGINE=InnoDB DEFAULT CHARSET=utf8;
  -- optimise jointure machine
ALTER TABLE `xmppmaster`.`glpi_location`
ADD INDEX IF NOT EXISTS `index2` (`glpi_id` ASC);




ALTER TABLE `xmppmaster`.`machines`
ADD INDEX IF NOT EXISTS `index_locent` (`glpi_entity_id` ASC, `glpi_location_id` ASC);


ALTER TABLE `xmppmaster`.`machines`
ADD INDEX IF NOT EXISTS `index_aggenttype` (`agenttype`(1) ASC);
ALTER TABLE `xmppmaster`.`machines`
ADD INDEX IF NOT EXISTS `index_enabled` (`enabled` ASC);


CREATE TABLE IF NOT EXISTS `glpi_register_keys` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(90) NOT NULL,
    `value` varchar(90) NOT NULL,
    `comment` varchar(45) DEFAULT NULL,
    `machines_id` int(11) NOT NULL,
    PRIMARY KEY (`id`),
    KEY `fk_glpi_register_keys_idx` (`machines_id`),
    CONSTRAINT `fk_glpi_register_keys`
    FOREIGN KEY (`machines_id`)
    REFERENCES `machines` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- DELETE FROM `xmppmaster`.`machines` WHERE 1;
-- ALTER TABLE `xmppmaster`.`machines`
-- ADD INDEX IF NOT EXISTS `fk_glpi_register_keys_id` (`glpi_regkey_id` ASC);

ALTER TABLE `xmppmaster`.`machines`
ADD INDEX IF NOT EXISTS `fk_glpi_entity_id` (`glpi_entity_id` ASC);
ALTER TABLE `xmppmaster`.`machines`
ADD CONSTRAINT `fk_glpi_entity_id`
  FOREIGN KEY IF NOT EXISTS(`glpi_entity_id`)
  REFERENCES `xmppmaster`.`glpi_entity` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

ALTER TABLE `xmppmaster`.`machines`
ADD INDEX IF NOT EXISTS `fk_glpi_location_id` (`glpi_location_id` ASC);
ALTER TABLE `xmppmaster`.`machines`
ADD CONSTRAINT `fk_glpi_location_id`
  FOREIGN KEY IF NOT EXISTS(`glpi_location_id`)
  REFERENCES `xmppmaster`.`glpi_location` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

SET FOREIGN_KEY_CHECKS=1;
UPDATE version SET Number = 56;

COMMIT;
