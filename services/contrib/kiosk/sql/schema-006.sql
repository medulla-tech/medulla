--
-- (c) 2022 Siveo, http://www.siveo.net/
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

START TRANSACTION;

USE kiosk;
ALTER TABLE package_has_profil change column package_id package_uuid VARCHAR(255) NOT NULL;

ALTER TABLE `kiosk`.`profile_has_ous`
CHANGE COLUMN `ou` `ou` VARCHAR(200) NULL DEFAULT NULL ;

ALTER TABLE `kiosk`.`profile_has_ous`
ADD INDEX IF NOT EXISTS `ind_pr_ous_ou` (`ou` ASC),
ADD INDEX IF NOT EXISTS `ind_profile` (`profile_id` ASC);

ALTER TABLE `kiosk`.`package_has_profil` 
ADD INDEX IF NOT EXISTS `ind_packid` (`package_uuid` ASC),
ADD INDEX IF NOT EXISTS `ind_profil` (`profil_id` ASC);

UPDATE version SET Number = 6;
COMMIT;
