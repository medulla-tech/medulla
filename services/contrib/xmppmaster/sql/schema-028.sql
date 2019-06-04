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
-- -----------------------------------------------------
-- Table `xmppmaster`.`deploy`
-- add syncthing condition
-- -----------------------------------------------------
ALTER TABLE `xmppmaster`.`deploy` 
ADD COLUMN `syncthing` INT NULL DEFAULT '0';

ALTER TABLE `xmppmaster`.`deploy` 
CHANGE COLUMN `title` `title` VARCHAR(255) NULL DEFAULT NULL AFTER `id`,
CHANGE COLUMN `jidmachine` `jidmachine` VARCHAR(255) NOT NULL AFTER `title`,
CHANGE COLUMN `jid_relay` `jid_relay` VARCHAR(255) NOT NULL AFTER `jidmachine`,
CHANGE COLUMN `startcmd` `startcmd` TIMESTAMP NULL DEFAULT NULL AFTER `start`,
CHANGE COLUMN `endcmd` `endcmd` TIMESTAMP NULL DEFAULT NULL AFTER `startcmd`,
CHANGE COLUMN `group_uuid` `group_uuid` VARCHAR(11) NULL DEFAULT NULL AFTER `command`,
CHANGE COLUMN `result` `result` TEXT NULL DEFAULT NULL AFTER `syncthing`;

-- -----------------------------------------------------
-- Table `xmppmaster`.`.has_login_command`
-- Valeur par défaut = 0
-- -----------------------------------------------------

Alter TABLE xmppmaster.has_login_command
ADD syncthing int NULL
DEFAULT 0;

-- -----------------------------------------------------
-- Table `xmppmaster`.`syncthing_deploy_group`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`syncthing_deploy_group` (
  `id` INT NOT NULL,
  `namepartage` VARCHAR(45) NULL,
  `directory_tmp` VARCHAR(45) NULL,
  `creation` VARCHAR(45) NULL,
  `grp_parent` VARCHAR(45) NULL,
  `cmd` VARCHAR(45) NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `xmppmaster`.`syncthing_ars_cluster`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`syncthing_ars_cluster` (
  `id` INT NOT NULL,
  `ars` VARCHAR(45) NULL,
  `keypartage` VARCHAR(45) NULL,
  `fk_deploy` INT NOT NULL,
  `type_partage` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_ARS_cluster_syncthing_deploy_group_syncthing1_idx` (`fk_deploy` ASC),
  CONSTRAINT `fk_syncthing_cluster_deploy_group`
    FOREIGN KEY (`fk_deploy`)
    REFERENCES `xmppmaster`.`syncthing_deploy_group` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



-- -----------------------------------------------------
-- Table `xmppmaster`.`syncthing_machine`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`syncthing_machine` (
  `id` INT NOT NULL,
  `jidmachine` VARCHAR(45) NULL,
  `uidmachine` VARCHAR(45) NULL,
  `comment` VARCHAR(45) NULL,
  `fk_arscluster` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_syncthing_machine_ars_cluster`
    FOREIGN KEY (`fk_arscluster`)
    REFERENCES `xmppmaster`.`syncthing_ars_cluster` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER = CURRENT_USER TRIGGER `xmppmaster`.`syncthing_deploy_group_BEFORE_DELETE` 
BEFORE DELETE ON `syncthing_deploy_group` FOR EACH ROW
BEGIN
DELETE FROM syncthing_ars_cluster
    WHERE syncthing_ars_cluster.fk_deploy = Old.id;
END$$


CREATE DEFINER = CURRENT_USER TRIGGER `xmppmaster`.`syncthing_ars_cluster_BEFORE_DELETE` 
BEFORE DELETE ON `syncthing_ars_cluster` FOR EACH ROW
BEGIN
DELETE FROM syncthing_ars_cluster
    WHERE syncthing_machine.fk_arscluster = Old.id;
END$$



DELIMITER ;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 28;

COMMIT;
