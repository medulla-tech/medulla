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
  `id` INT NOT NULL AUTO_INCREMENT,
  `namepartage` VARCHAR(80) NULL,
  `directory_tmp` VARCHAR(80) NULL,
  `datecreation`  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` VARCHAR(6) NOT NULL DEFAULT 'C',
  `package` VARCHAR(90) NOT NULL,
  `grp_parent` INT(11) NOT NULL ,
  `cmd` INT(11) NOT NULL ,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

-- "path": "/var/lib/pulse2/packages/66836348-85c7-11e9-950b-000c292ae18d",
-- -----------------------------------------------------
-- Table `xmppmaster`.`syncthing_ars_cluster`
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Table `xmppmaster`.`syncthing_ars_cluster`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`syncthing_ars_cluster` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `numcluster` INT(11) NOT NULL ,
  `namecluster` VARCHAR(45) NULL,
  `liststrcluster` TEXT NOT NULL,
  `arsmastercluster` VARCHAR(255) NOT NULL,
  `keypartage` VARCHAR(255) NULL,
  `fk_deploy` INT NOT NULL,
  `type_partage` VARCHAR(45) NULL,
  `devivesyncthing` VARCHAR(512) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_ARS_cluster_syncthing_deploy_group_syncthing1_idx` (`fk_deploy` ASC),
  CONSTRAINT `fk_syncthing_cluster_deploy_group`
    FOREIGN KEY (`fk_deploy`)
    REFERENCES `xmppmaster`.`syncthing_deploy_group` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
    ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `xmppmaster`.`syncthing_machine`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`syncthing_machine` (
    `id`            INT NOT NULL AUTO_INCREMENT,
    `jidmachine`    VARCHAR(255) NOT NULL,
    `inventoryuuid` INT(11) NULL,
    `title`         VARCHAR(255) NULL,
    `jid_relay`     VARCHAR(255) NOT NULL,
    `cluster`       VARCHAR(1024) NOT NULL,
    `pathpackage`   VARCHAR(100)  NOT NULL,
    `state`         VARCHAR(45)  NOT NULL,
    `sessionid`     VARCHAR(45)  NOT NULL,
    `start`         TIMESTAMP    NOT NULL,
    `startcmd`      TIMESTAMP    NOT NULL,
    `endcmd`        TIMESTAMP    NOT NULL,
    `user`          VARCHAR(45)  NULL,
    `command`       INT(11)      NOT NULL,
    `group_uuid`    INT(11)  NOT NULL,
    `login`         VARCHAR(45)  NULL,
    `macadress`     VARCHAR(255) NULL,
    `syncthing`     INT(11)      NOT NULL,
    `result`        TEXT         NOT NULL,
    `comment`       VARCHAR(45) NULL,
    `fk_arscluster` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_syncthing_machine_ars_cluster`
    FOREIGN KEY (`fk_arscluster`)
    REFERENCES `xmppmaster`.`syncthing_ars_cluster` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
  ENGINE = InnoDB;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 28;

COMMIT;
