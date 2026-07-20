--
-- (c) 2024-2026 Medulla, http://www.medulla-tech.io
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/>.
--

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

-- =====================================================================
-- Global inventory tag -> entity rules (admin scope, root-managed)
-- =====================================================================
CREATE TABLE IF NOT EXISTS `admin_inventory_entity_rules` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `enabled` TINYINT(1) NOT NULL DEFAULT 1,
  `rule_name` VARCHAR(190) NOT NULL DEFAULT '',
  `tag_name` VARCHAR(100) NOT NULL DEFAULT 'TAG',
  `tag_value` VARCHAR(255) NOT NULL,
  `entity_id` INT NOT NULL,
  `priority` INT NOT NULL DEFAULT 100,
  -- Champ reserve pour future evaluation multi-regles.
  -- Actuellement non exploite par le moteur (premier match par priority/id).
  `stop_on_match` TINYINT(1) NOT NULL DEFAULT 1,
  `comment` VARCHAR(255) NOT NULL DEFAULT '',
  `created_by` VARCHAR(100) NOT NULL DEFAULT 'root',
  `updated_by` VARCHAR(100) NOT NULL DEFAULT 'root',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uniq_tag_rule` (`tag_name`, `tag_value`, `priority`),
  KEY `idx_tag_rule_lookup` (`enabled`, `tag_name`, `tag_value`, `priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='[Admin] Global inventory rules mapping TAG to GLPI entity';


--
-- Update version du schema (rejouable)
--
UPDATE version
SET Number = 18
WHERE Number < 18;

-- =====================================================================
-- Custom metadata storage for inventory machines (substitute scope)
-- =====================================================================
CREATE TABLE IF NOT EXISTS `substitute_inventory_metadata` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `jid` VARCHAR(255) NOT NULL,
  `hostname` VARCHAR(255) NOT NULL DEFAULT '',
  `key_name` VARCHAR(255) NOT NULL,
  `value` LONGTEXT,
  `description` LONGTEXT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uniq_jid_key` (`jid`, `key_name`),
  KEY `idx_jid_lookup` (`jid`),
  KEY `idx_hostname_lookup` (`hostname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='[Substitute] Custom metadata indexed by machine JID';

--
-- Finalize version update
--
UPDATE version
SET Number = 18
WHERE Number < 18;

COMMIT;
