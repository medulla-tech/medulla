--
-- (c) 2022 Siveo, http://www.siveo.net/
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
-- Table structure for table `version`
--
-- ----------------------------------------------------------------------
-- Database
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admin`.`saas_organisations` (
  `organization_id` INT NOT NULL,
  `organization_name` VARCHAR(45) NOT NULL,
  `entity_id` VARCHAR(45) NOT NULL,
  `entity_name` VARCHAR(400) NOT NULL,
  `user_id` VARCHAR(45) NULL,
  `user_name` VARCHAR(45) NULL,
  `profile_id` VARCHAR(45) NULL DEFAULT '0',
  `profile_name` VARCHAR(400) NOT NULL,
  `is_active` TINYINT NULL DEFAULT 1,
  `user_token` VARCHAR(45) NOT NULL,
  `tag_name` CHAR(36) NOT NULL DEFAULT (UUID()),
  PRIMARY KEY (`organization_id`, `entity_id`)
);

-- Création de la table `saas_application` pour stocker les configurations essentielles de l'application SaaS
-- Cette table contient des paramètres critiques nécessaires au fonctionnement de l'application.
 CREATE TABLE `saas_application` (
  `setting_name` varchar(45) NOT NULL,
  `setting_value` varchar(45) DEFAULT NULL,
  `setting_description` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`setting_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- cette table doit obligatoirement avoir ces datas.
-- +----------------------+------------------------------------------+------------------------+
-- | setting_name         | setting_value                            | setting_description    |
-- +----------------------+------------------------------------------+------------------------+
-- | glpi_mmc_app_token   | OXOMtrKNUkD5kUAPubPEUX84pZX9WAlvkgFhKZnz | token application MMC  |
-- | glpi_root_user_token | fjNoSBCBIPpt925Hgxorc4QGEgWGEADQ1GmcRaTI | token user super admin |
-- | glpi_url_base_api    | http://jfk.medulla.lan/glpi/apirest.php  | url REST API           |
-- | API_REST             | GLPI                                     | quel api est utiliser  |
-- +----------------------+------------------------------------------+------------------------+

--
-- Dumping data for table `version`
--

UPDATE version SET Number = 4;

COMMIT;
