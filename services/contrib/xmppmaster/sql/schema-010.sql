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

START TRANSACTION;

-- --------------------------------------------------------------
-- add gestion cluster for xmpp ARS
-- --------------------------------------------------------------
-- -----------------------------------------------------
-- Table `cluster_ars`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `cluster_ars` ;

CREATE TABLE IF NOT EXISTS `cluster_ars` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

INSERT INTO `xmppmaster`.`cluster_ars` (`name`, `description`) VALUES ('ars_pulse', 'primary cluster');
-- -----------------------------------------------------
-- Table `has_cluster_ars`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `has_cluster_ars` ;

CREATE TABLE IF NOT EXISTS `has_cluster_ars` (
  `id` INT NOT NULL,
  `id_ars` VARCHAR(45) NOT NULL,
  `id_cluster` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

INSERT INTO `xmppmaster`.`has_cluster_ars` (`id`, `id_ars`, `id_cluster`) VALUES ('1', '1', '1');

-- -----------------------------------------------------
-- Table `relayserver add infos in relayserver`
-- -----------------------------------------------------
ALTER TABLE `xmppmaster`.`relayserver`
ADD COLUMN `moderelayserver` VARCHAR(7) NOT NULL DEFAULT 'static' AFTER `package_server_port`;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 10;

COMMIT;
