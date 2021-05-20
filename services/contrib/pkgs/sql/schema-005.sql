--
-- (c) 2021 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://www.siveo.net
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
-- Table `pkgs`.`pkgs_rules_global` suppression FOREIGN KEY
-- -----------------------------------------------------

ALTER TABLE `pkgs`.`pkgs_rules_global`
DROP FOREIGN KEY `fk_pkgs_rules_global_pkgs_shares1`;
ALTER TABLE `pkgs`.`pkgs_rules_global`
DROP INDEX `fk_pkgs_rules_global_pkgs_shares1_idx` ;

INSERT INTO `pkgs`.`pkgs_rules_algos` (`id`, `name`, `description`, `level`) VALUES ('3', 'login_cluster_ars_admin', 'Rule Use to add admin rights to the cluster.', '1');
UPDATE `pkgs`.`pkgs_rules_algos` SET `level` = 2 WHERE `id` = 2;

ALTER TABLE `pkgs`.`pkgs_rules_global`
CHANGE COLUMN `pkgs_shares_id` `pkgs_cluster_ars_id` INT(11) NOT NULL ;

ALTER TABLE packages
CHANGE COLUMN size size BIGINT null default 0;

UPDATE version SET Number = 5;

COMMIT;
