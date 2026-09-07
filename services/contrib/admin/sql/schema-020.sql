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

-- A source user is unique only inside its ITSM client. Local GLPI logins are
-- technical identifiers so identical source logins or emails never collide.
CREATE TABLE IF NOT EXISTS `saas_itsm_user_mapping` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL,
  `source_user_id` VARCHAR(100) NOT NULL,
  `source_login` VARCHAR(255) NOT NULL DEFAULT '',
  `source_email` VARCHAR(255) NOT NULL DEFAULT '',
  `target_user_id` INT NOT NULL,
  `target_login` VARCHAR(255) NOT NULL,
  `source_updated_at` VARCHAR(50) NOT NULL DEFAULT '',
  `last_seen_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_client_source_user` (`client_id`, `source_user_id`),
  UNIQUE KEY `uk_target_user` (`target_user_id`),
  KEY `idx_client_email` (`client_id`, `source_email`),
  KEY `idx_client_login` (`client_id`, `source_login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='[SaaS] Mapping scoped ITSM source users to ITSMLocal users';

-- Explicit Medulla-owned exceptions to the default source profile remapping.
-- A target profile is validated by the synchronizer and can never be the
-- ITSMLocal platform Super-Admin profile.
CREATE TABLE IF NOT EXISTS `saas_itsm_profile_mapping` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL,
  `source_profile_id` VARCHAR(100) NOT NULL,
  `source_profile_name` VARCHAR(255) NOT NULL DEFAULT '',
  `target_profile_name` VARCHAR(255) NOT NULL,
  `enabled` TINYINT(1) NOT NULL DEFAULT 1,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_client_source_profile` (`client_id`, `source_profile_id`),
  KEY `idx_client_target_profile` (`client_id`, `target_profile_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='[SaaS] Explicit client ITSM profile to allowed ITSMLocal profile mapping';

-- OIDC identity is scoped by both tenant/client and provider. Email is only
-- searchable for an explicit initial match and is never globally unique.
CREATE TABLE IF NOT EXISTS `saas_oidc_user_mapping` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL,
  `provider_id` INT NOT NULL,
  `subject` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL DEFAULT '',
  `preferred_username` VARCHAR(255) NOT NULL DEFAULT '',
  `target_user_id` INT NOT NULL,
  `target_login` VARCHAR(255) NOT NULL,
  `first_seen_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_client_provider_subject` (`client_id`, `provider_id`, `subject`),
  UNIQUE KEY `uk_client_target_user` (`client_id`, `target_user_id`),
  KEY `idx_client_email` (`client_id`, `email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='[SaaS] Mapping scoped OIDC identities to ITSMLocal users';

UPDATE version
SET Number = 20
WHERE Number < 20;

COMMIT;
