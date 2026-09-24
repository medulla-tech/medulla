-- (c) 2026 Medulla, http://www.medulla-tech.io
-- Schema 018: ITSM to ITSMLocal entity synchronization tables.

SET NAMES utf8mb4;
START TRANSACTION;

CREATE TABLE IF NOT EXISTS `admin`.`saas_itsm_entity_mapping` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL,
  `source_path` VARCHAR(500) NOT NULL,
  `source_id` VARCHAR(100) NOT NULL,
  `target_path` VARCHAR(500),
  `target_glpi_id` INT,
  `config_version` VARCHAR(50),
  `last_modifier` VARCHAR(100),
  `modification_origin` VARCHAR(20),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `uk_client_source_id` (`client_id`, `source_id`),
  INDEX `idx_client_target_glpi_id` (`client_id`, `target_glpi_id`),
  INDEX `idx_updated_at` (`updated_at`),
  INDEX `idx_modification_origin` (`modification_origin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `admin`.`saas_itsm_sync_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL,
  `sync_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `config_version` VARCHAR(50),
  `status` VARCHAR(20),
  `objects_created` INT DEFAULT 0,
  `objects_updated` INT DEFAULT 0,
  `objects_ignored` INT DEFAULT 0,
  `errors` LONGTEXT,
  `debug_mode` BOOLEAN DEFAULT FALSE,
  INDEX `idx_client_sync_timestamp` (`client_id`, `sync_timestamp`),
  INDEX `idx_status` (`status`),
  INDEX `idx_sync_timestamp` (`sync_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS `admin`.`saas_itsm_sync_metrics` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL,
  `sync_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `duration_seconds` INT,
  `objects_count` INT,
  `errors_count` INT,
  `performance_notes` TEXT,
  INDEX `idx_client_sync_timestamp` (`client_id`, `sync_timestamp`),
  INDEX `idx_duration_seconds` (`duration_seconds`),
  INDEX `idx_sync_timestamp` (`sync_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

UPDATE version SET Number = 18 WHERE Number < 18;

COMMIT;
