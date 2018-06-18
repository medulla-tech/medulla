--
-- (c) 2018 Siveo, http://www.siveo.net/
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

CREATE TABLE IF NOT EXISTS `package_has_profil` (
  `id` INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(`id`),
  `package_id` INT NOT NULL,
  `profil_id` INT NOT NULL,
  `package_status` ENUM('allowed', 'restricted'))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `package` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(45) NOT NULL,
  `version_package` VARCHAR(45) NOT NULL,
  `software` VARCHAR(45) NOT NULL,
  `description` VARCHAR(200) NULL,
  `version_software` VARCHAR(45) NOT NULL,
  `package_uuid` VARCHAR(50) NOT NULL,
  `os` VARCHAR(45) NOT NULL,
  UNIQUE(`package_uuid`),
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


UPDATE version SET Number = 2;
