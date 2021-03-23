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


START TRANSACTION;

-- -----------------------------------------------------
-- Table `pkgs`.`pkgs_shares`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pkgs_shares`;
CREATE TABLE IF NOT EXISTS `pkgs`.`pkgs_shares` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `comments` VARCHAR(1024) NULL DEFAULT '\"\"',
  `enabled` INT NOT NULL DEFAULT 1,
  `type` VARCHAR(45) NOT NULL DEFAULT 'local',
  `uri` VARCHAR(255) NOT NULL,
  `ars_name` VARCHAR(255) NULL,
  `ars_id` INT NOT NULL,
  `share_path` VARCHAR(255) NOT NULL DEFAULT '\"/var/lib/pulse/local\"',
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'Cette table permet de definir des partages.\n';

-- -----------------------------------------------------
-- Table `pkgs`.`pkgs_shares_ars`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pkgs_shares_ars`;
CREATE TABLE IF NOT EXISTS `pkgs`.`pkgs_shares_ars` (
  `id` INT NOT NULL COMMENT 'cet id doit correspondre a id de ars de la table relayserver.',
  `hostname` VARCHAR(255) NULL,
  `jid` VARCHAR(255) NULL,
  `pkgs_shares_id` INT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `index3` (`jid` ASC, `hostname` ASC))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `pkgs`.`pkgs_shares_ars_web`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pkgs_shares_ars_web`;
CREATE TABLE IF NOT EXISTS `pkgs`.`pkgs_shares_ars_web` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `ars_share_id` INT NOT NULL,
  `packages_id` INT(11) NOT NULL,
  `status` VARCHAR(45) NOT NULL DEFAULT 'pending',
  `finger_print` VARCHAR(255) NULL,
  `size` VARCHAR(45) NULL,
  `date_edition` DATETIME NULL,
  PRIMARY KEY (`id`, `ars_share_id`, `packages_id`),
  INDEX `fk_pkgs_ars_web_partages_packages1_idx` (`packages_id` ASC),
  INDEX `fk_pkgs_ars_web_partages_ars_partage1_idx` (`ars_share_id` ASC),
  UNIQUE INDEX `idx_pap_uniq` (`ars_share_id` ASC, `packages_id` ASC),
  CONSTRAINT `fk_pkgs_ars_web_partages_packages1`
    FOREIGN KEY (`packages_id`)
    REFERENCES `pkgs`.`packages` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pkgs_ars_web_partages_ars_partage1`
    FOREIGN KEY (`ars_share_id`)
    REFERENCES `pkgs`.`pkgs_shares_ars` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `pkgs`.`pkgs_rules_algos`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pkgs_rules_algos`;
CREATE TABLE IF NOT EXISTS `pkgs`.`pkgs_rules_algos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NOT NULL,
  `level` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
COMMENT = 'definition des algos pour attribution des partages.';

-- -----------------------------------------------------
-- Table `pkgs`.`pkgs_rules_global`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pkgs_rules_global`;
CREATE TABLE IF NOT EXISTS `pkgs`.`pkgs_rules_global` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pkgs_rules_algos_id` INT NOT NULL,
  `pkgs_shares_id` INT NOT NULL,
  `order` INT NULL DEFAULT 0,
  `subject` VARCHAR(255) NOT NULL,
  `permission` varchar(5) DEFAULT 'rw',
  PRIMARY KEY (`id`, `pkgs_rules_algos_id`),
  INDEX `fk_pkgs_rules_global_pkgs_rules_algos1_idx` (`pkgs_rules_algos_id` ASC),
  INDEX `fk_pkgs_rules_global_pkgs_shares1_idx` (`pkgs_shares_id` ASC),
  CONSTRAINT `fk_pkgs_rules_global_pkgs_rules_algos1`
    FOREIGN KEY (`pkgs_rules_algos_id`)
    REFERENCES `pkgs`.`pkgs_rules_algos` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pkgs_rules_global_pkgs_shares1`
    FOREIGN KEY (`pkgs_shares_id`)
    REFERENCES `pkgs`.`pkgs_shares` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'definition des regles ordonees qui sont utilisees pour determiner les partages globals.';


-- -----------------------------------------------------
-- Table `pkgs`.`pkgs_rules_local`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `pkgs_rules_local`;
CREATE TABLE IF NOT EXISTS `pkgs`.`pkgs_rules_local` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pkgs_rules_algos_id` INT NOT NULL,
  `order` INT NULL DEFAULT 0,
  `suject` VARCHAR(255) NULL,
  `permission` varchar(5) DEFAULT 'rw',
  `pkgs_shares_id` INT NOT NULL,
  PRIMARY KEY (`id`, `pkgs_rules_algos_id`),
  INDEX `fk_pkgs_rules_local_pkgs_rules_algos1_idx` (`pkgs_rules_algos_id` ASC),
  INDEX `fk_pkgs_rules_local_pkgs_shares1_idx` (`pkgs_shares_id` ASC),
  CONSTRAINT `fk_pkgs_rules_local_pkgs_rules_algos1`
    FOREIGN KEY (`pkgs_rules_algos_id`)
    REFERENCES `pkgs`.`pkgs_rules_algos` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_pkgs_rules_local_pkgs_shares1`
    FOREIGN KEY (`pkgs_shares_id`)
    REFERENCES `pkgs`.`pkgs_shares` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
COMMENT = 'definition des regles ordonees qui sont utilisees pour determiner les partages locaux.';

-- 
-- -----------------------------------------------------
-- add field `table packages`.
-- -----------------------------------------------------
ALTER TABLE `pkgs`.`packages` 
ADD COLUMN `pkgs_share_id` INT(11) NULL DEFAULT NULL AFTER `preCommand_name`;

ALTER TABLE `pkgs`.`packages` 
ADD COLUMN `edition_status` INT NULL DEFAULT 1 AFTER `pkgs_share_id`;

ALTER TABLE `pkgs`.`packages` 
ADD COLUMN `conf_json` TEXT NULL AFTER `edition_status`;

ALTER TABLE `pkgs`.`packages`
ADD COLUMN `size` INT NULL DEFAULT "0" AFTER `conf_json`;

-- -----------------------------------------------------
-- add field `table pkgs_shares`.manage quotas
-- -----------------------------------------------------

ALTER TABLE `pkgs`.`pkgs_shares`
ADD COLUMN `usedquotas` INT NULL DEFAULT 0 AFTER `share_path`,
ADD COLUMN `quotas` INT NULL DEFAULT 0 AFTER `usedquotas`;


UPDATE version SET Number = 4;

COMMIT;
