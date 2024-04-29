--
-- (c) 2010 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Medulla 2, http://medulla.mandriva.org
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------


START TRANSACTION;


-- Create table package_pending_exclusions
DROP TABLE IF EXISTS `pkgs`.`package_pending_exclusions`;
CREATE TABLE `pkgs`.`package_pending_exclusions` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `relayserver_jid` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`id`));


-- Create trigger that deletes all ARS which we do not need to wait for from syncthingsync table
DROP TRIGGER IF EXISTS `pkgs`.`syncthingsync_BEFORE_INSERT`;

DELIMITER $$
USE `pkgs`$$
CREATE DEFINER = CURRENT_USER TRIGGER `pkgs`.`syncthingsync_BEFORE_INSERT` BEFORE INSERT ON `syncthingsync` FOR EACH ROW
BEGIN
    if EXISTS (SELECT * FROM `pkgs`.`package_pending_exclusions` WHERE `package_pending_exclusions`.`relayserver_jid` = NEW.relayserver_jid) THEN
        set NEW.relayserver_jid = NULL;
    END if;
END;$$
DELIMITER ;


UPDATE version SET Number = 2;

COMMIT;
