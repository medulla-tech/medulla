-- SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/updates/sql/schema-002.sql
--
-- Local copy of the medulla-wsus mirror.

START TRANSACTION;

CREATE TABLE IF NOT EXISTS `products` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `mirror_id` char(36) NOT NULL COMMENT 'Microsoft product GUID',
  `name` varchar(255) NOT NULL,
  `family` varchar(255) NULL,
  `display_group` varchar(32) NULL COMMENT 'set by the mirror: windows11, windows10, server, office, visual_studio, security',
  `display_name` varchar(255) NULL COMMENT 'set by the mirror when the Microsoft name is unclear or duplicated',
  `position` smallint unsigned NOT NULL DEFAULT 0 COMMENT 'set by the mirror: display order',
  `supported` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'set by the mirror: still supported by Microsoft',
  `copied` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'full history replicated since an entity tracks it',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_products_mirror_id` (`mirror_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `entity_products` (
  `entity_id` int unsigned NOT NULL COMMENT 'GLPI entity',
  `product_id` int unsigned NOT NULL,
  PRIMARY KEY (`entity_id`, `product_id`),
  KEY `idx_entity_products_product_id` (`product_id`),
  CONSTRAINT `fk_entity_products_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `releases` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `product_id` int unsigned NOT NULL,
  `os_product_name` varchar(64) NOT NULL COMMENT 'e.g. Client.OS.RS2.AMD64',
  `build` int unsigned NOT NULL,
  `name` varchar(20) NULL COMMENT 'e.g. 25H2',
  `architecture` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_releases_os_build` (`os_product_name`, `build`),
  KEY `idx_releases_product_id` (`product_id`),
  CONSTRAINT `fk_releases_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Versions tracked by an entity (releases.name); entity_products keeps the product
CREATE TABLE IF NOT EXISTS `entity_releases` (
  `entity_id` int unsigned NOT NULL COMMENT 'GLPI entity',
  `product_id` int unsigned NOT NULL,
  `release_name` varchar(20) NOT NULL COMMENT 'releases.name, e.g. 25H2',
  PRIMARY KEY (`entity_id`, `product_id`, `release_name`),
  KEY `idx_entity_releases_product_id` (`product_id`),
  CONSTRAINT `fk_entity_releases_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Linux versions an entity allows its machines to reach; none by default
CREATE TABLE IF NOT EXISTS `entity_linux_releases` (
  `entity_id` int unsigned NOT NULL COMMENT 'GLPI entity',
  `distribution` varchar(32) NOT NULL COMMENT 'ID of os-release, e.g. debian',
  `release_name` varchar(20) NOT NULL COMMENT 'version reported by the machines, e.g. 14',
  PRIMARY KEY (`entity_id`, `distribution`, `release_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `updates` (
  `id` int unsigned NOT NULL COMMENT 'mirror id',
  `mucatalog_id` char(36) NULL,
  `wsus_id` char(36) NULL,
  `kb` int unsigned NULL,
  `title` varchar(500) NOT NULL,
  `description` text NULL,
  `classification` varchar(100) NULL,
  `severity` varchar(20) NULL,
  `release_id` int unsigned NULL,
  `target_version` varchar(32) NULL COMMENT 'build.UBR reached',
  `dotnet_versions` varchar(32) NULL COMMENT '.NET versions targeted, comma separated (3.5,4.8.1)',
  `published_at` datetime NULL,
  `superseded` tinyint(1) NOT NULL DEFAULT 0,
  `removed` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'withdrawn by Microsoft',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_updates_kb` (`kb`),
  KEY `idx_updates_release_superseded` (`release_id`, `superseded`),
  CONSTRAINT `fk_updates_release` FOREIGN KEY (`release_id`) REFERENCES `releases` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `update_products` (
  `update_id` int unsigned NOT NULL,
  `product_id` int unsigned NOT NULL,
  PRIMARY KEY (`update_id`, `product_id`),
  KEY `idx_update_products_product_id` (`product_id`),
  CONSTRAINT `fk_update_products_update` FOREIGN KEY (`update_id`) REFERENCES `updates` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_update_products_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `files` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `sha1` char(28) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'base64',
  `sha256` char(44) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT 'base64',
  `name` varchar(255) NOT NULL,
  `size` bigint unsigned NULL,
  `url` varchar(1024) NOT NULL,
  `kind` varchar(10) NULL COMMENT 'file extension',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_files_sha1` (`sha1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `update_files` (
  `update_id` int unsigned NOT NULL,
  `file_id` int unsigned NOT NULL,
  `language` varchar(20) NULL,
  PRIMARY KEY (`update_id`, `file_id`),
  KEY `idx_update_files_file_id` (`file_id`),
  CONSTRAINT `fk_update_files_update` FOREIGN KEY (`update_id`) REFERENCES `updates` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_update_files_file` FOREIGN KEY (`file_id`) REFERENCES `files` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `supersedences` (
  `update_id` int unsigned NOT NULL,
  `superseded_id` int unsigned NOT NULL,
  PRIMARY KEY (`update_id`, `superseded_id`),
  KEY `idx_supersedences_superseded_id` (`superseded_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `cves` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `cve` varchar(32) NOT NULL,
  `title` varchar(500) NULL,
  `severity` varchar(20) NULL,
  `cvss_score` decimal(3,1) NULL,
  `exploited` tinyint(1) NOT NULL DEFAULT 0,
  `publicly_disclosed` tinyint(1) NOT NULL DEFAULT 0,
  `published_at` datetime NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_cves_cve` (`cve`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `kb_cves` (
  `kb` int unsigned NOT NULL,
  `cve_id` int unsigned NOT NULL,
  PRIMARY KEY (`kb`, `cve_id`),
  KEY `idx_kb_cves_cve_id` (`cve_id`),
  CONSTRAINT `fk_kb_cves_cve` FOREIGN KEY (`cve_id`) REFERENCES `cves` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `replication` (
  `id` tinyint unsigned NOT NULL COMMENT 'single row, id = 1',
  `mirror_generation` varchar(64) NULL,
  `mirror_version` int unsigned NOT NULL DEFAULT 0,
  `media_version` varchar(64) NULL COMMENT 'version of the media list (/v1/media)',
  `linux_releases_version` varchar(64) NULL COMMENT 'version of the Linux releases list',
  `last_attempt_at` datetime NULL,
  `last_success_at` datetime NULL,
  `last_error` text NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO `replication` (`id`) VALUES (1);

-- Complete Windows media of the official Microsoft catalogs, copied whole from the mirror (/v1/media).
-- base_build: build of the image; a later version on the same base is reached by updates.
CREATE TABLE IF NOT EXISTS `media_files` (
  `file_name` varchar(255) NOT NULL,
  `edition` varchar(64) NOT NULL,
  `base_build` varchar(32) NOT NULL,
  `architecture` varchar(10) NOT NULL,
  `language_code` varchar(20) NOT NULL,
  `size` bigint unsigned NOT NULL,
  `sha256` char(64) NOT NULL,
  `url` varchar(500) NOT NULL,
  PRIMARY KEY (`file_name`, `edition`),
  KEY `idx_media_files_base` (`base_build`, `architecture`, `language_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Linux releases of each distribution, copied whole from the mirror.
CREATE TABLE IF NOT EXISTS `linux_releases` (
  `distribution` varchar(32) NOT NULL COMMENT 'ID of os-release, e.g. debian',
  `release_name` varchar(20) NOT NULL COMMENT 'e.g. 14',
  `codename` varchar(32) NULL,
  `released` date NULL,
  PRIMARY KEY (`distribution`, `release_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `machine_reports` (
  `jid` varchar(255) NOT NULL,
  `glpi_uuid` varchar(32) NULL COMMENT 'xmppmaster.machines.uuid_inventorymachine, e.g. UUID12; empty until GLPI has the machine',
  `hostname` varchar(255) NULL,
  `received_at` datetime NOT NULL,
  `format` smallint unsigned NOT NULL COMMENT 'report format version',
  `os` enum('windows','linux') NOT NULL DEFAULT 'windows',
  `distribution` varchar(32) NULL COMMENT 'Linux: ID of os-release, e.g. debian',
  `family` varchar(16) NULL COMMENT 'Linux package manager: apt, dnf or zypper',
  `kernel` varchar(64) NULL COMMENT 'Linux: running kernel',
  `product` varchar(255) NULL COMMENT 'e.g. Windows 11 Pro, Debian GNU/Linux 13 (trixie)',
  `edition` varchar(64) NULL COMMENT 'EditionID',
  `release` varchar(16) NULL COMMENT 'DisplayVersion, e.g. 25H2',
  `build` int unsigned NULL,
  `ubr` int unsigned NULL,
  `architecture` varchar(10) NULL,
  `language` varchar(20) NULL COMMENT 'e.g. fr-fr',
  `system_type` varchar(10) NULL COMMENT 'client or server',
  `esu_licensed` tinyint(1) NULL,
  `search_status` varchar(16) NULL COMMENT 'ok, failed, blocked, timeout, skipped',
  `search_error` text NULL,
  `search_server` varchar(32) NULL COMMENT 'windows_update or microsoft_update',
  `search_duration` int unsigned NULL COMMENT 'seconds',
  `searched_at` datetime NULL,
  `wsus_server` varchar(255) NULL COMMENT 'WUServer policy',
  `automatic_updates` varchar(32) NULL,
  `service_state` varchar(32) NULL COMMENT 'wuauserv state',
  `windows11_eligible` tinyint(1) NULL,
  `windows11_blockers` varchar(255) NULL COMMENT 'comma separated, e.g. tpm,secure_boot,cpu',
  `windows11_source` varchar(16) NULL COMMENT 'windows or facts',
  `reboot_pending` tinyint(1) NULL COMMENT 'Windows waits for a restart',
  `restart_requested_at` datetime NULL COMMENT 'last restart sent from Medulla',
  `report` mediumtext NULL COMMENT 'raw JSON report',
  PRIMARY KEY (`jid`),
  KEY `idx_machine_reports_received_at` (`received_at`),
  KEY `idx_machine_reports_glpi_uuid` (`glpi_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `machine_installed_kbs` (
  `jid` varchar(255) NOT NULL,
  `kb` int unsigned NOT NULL,
  `installed_on` date NULL,
  PRIMARY KEY (`jid`, `kb`),
  KEY `idx_machine_installed_kbs_kb` (`kb`),
  CONSTRAINT `fk_machine_installed_kbs_report` FOREIGN KEY (`jid`) REFERENCES `machine_reports` (`jid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `machine_missing_updates` (
  `jid` varchar(255) NOT NULL,
  `windows_update_id` char(36) NOT NULL COMMENT 'UpdateID from the machine search',
  `kb` int unsigned NULL,
  `title` varchar(500) NULL,
  PRIMARY KEY (`jid`, `windows_update_id`),
  KEY `idx_machine_missing_updates_kb` (`kb`),
  CONSTRAINT `fk_machine_missing_updates_report` FOREIGN KEY (`jid`) REFERENCES `machine_reports` (`jid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `machine_updates` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `jid` varchar(255) NOT NULL,
  `update_id` int unsigned NULL COMMENT 'mirror id, NULL when absent from the catalog',
  `kb` int unsigned NULL,
  `title` varchar(500) NOT NULL,
  `origin` enum('machine','deduced') NOT NULL COMMENT 'machine search or catalog deduction',
  `package` varchar(255) NULL COMMENT 'Linux: package name',
  `installed_version` varchar(128) NULL COMMENT 'Linux',
  `available_version` varchar(128) NULL COMMENT 'Linux',
  `classification` varchar(64) NULL COMMENT 'Linux, catalog vocabulary: Security Updates or Updates',
  `severity` varchar(16) NULL COMMENT 'Linux, catalog vocabulary: Critical, Important, Moderate, Low',
  `offer` varchar(16) NOT NULL DEFAULT 'main' COMMENT 'Windows: main, optional, esu; Linux: main',
  `computed_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_machine_updates_jid` (`jid`),
  KEY `idx_machine_updates_update_id` (`update_id`),
  KEY `idx_machine_updates_kb` (`kb`),
  CONSTRAINT `fk_machine_updates_report` FOREIGN KEY (`jid`) REFERENCES `machine_reports` (`jid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Version upgrade of each machine, recomputed with its updates.
-- state: up_to_date, ready, not_eligible, not_concerned, no_report (transient), undetermined (our defect)
-- steps: comma-separated, in order (cumulative, cleanup, scan, media, enablement)
-- launched_*: written by the admin and the runner, never by the computation
CREATE TABLE IF NOT EXISTS `machine_upgrades` (
  `jid` varchar(255) NOT NULL,
  `state` varchar(32) NOT NULL,
  `target_release` varchar(20) NULL,
  `target_build` int unsigned NULL,
  `steps` varchar(100) NULL,
  `reason` varchar(255) NULL,
  `media_file` varchar(255) NULL,
  `computed_at` datetime NOT NULL,
  `launched_at` datetime NULL COMMENT 'set by the admin, cleared when done or failed',
  `launched_by` varchar(255) NULL,
  `run_error` varchar(255) NULL COMMENT 'why the last launched upgrade stopped',
  PRIMARY KEY (`jid`),
  KEY `idx_machine_upgrades_state` (`state`),
  KEY `idx_machine_upgrades_launched` (`launched_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Explicit decisions; no row = pending unless an approval rule matches
CREATE TABLE IF NOT EXISTS `approvals` (
  `entity_id` int unsigned NOT NULL COMMENT 'GLPI entity',
  `update_id` int unsigned NOT NULL,
  `status` enum('approved','declined') NOT NULL,
  `decided_by` varchar(255) NULL,
  `decided_at` datetime NOT NULL,
  PRIMARY KEY (`entity_id`, `update_id`),
  KEY `idx_approvals_update_id` (`update_id`),
  CONSTRAINT `fk_approvals_update` FOREIGN KEY (`update_id`) REFERENCES `updates` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Automatic approval cells, evaluated at read time
CREATE TABLE IF NOT EXISTS `approval_rules` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `entity_id` int unsigned NOT NULL COMMENT 'GLPI entity',
  `os` enum('windows','linux') NOT NULL DEFAULT 'windows',
  `classification` varchar(100) NOT NULL,
  `severity` varchar(20) NULL COMMENT 'NULL matches every update of the classification',
  `created_by` varchar(255) NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_approval_rules_cell` (`entity_id`, `os`, `classification`, `severity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- No row = defaults (no automatic deployment, no window)
CREATE TABLE IF NOT EXISTS `entity_settings` (
  `entity_id` int unsigned NOT NULL COMMENT 'GLPI entity',
  `auto_deploy` tinyint(1) NOT NULL DEFAULT 0,
  `window_start` time NULL,
  `window_end` time NULL,
  `upgrade_window_start` time NULL COMMENT 'start of the steps of the upgrades; none = any time',
  `upgrade_window_end` time NULL,
  `updated_by` varchar(255) NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`entity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- GLPI entity tree; signed parent: older GLPI versions store -1 for the root
CREATE TABLE IF NOT EXISTS `glpi_entities` (
  `id` int unsigned NOT NULL,
  `entities_id` int NULL COMMENT 'parent, NULL for the root',
  PRIMARY KEY (`id`)
) ENGINE=FEDERATED DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
  CONNECTION='itsm_federated/glpi_entities';

-- The entity has its own setting, possibly empty; no row = inherited
CREATE TABLE IF NOT EXISTS `entity_overrides` (
  `entity_id` int unsigned NOT NULL COMMENT 'GLPI entity',
  `setting` enum('products','rules','linux_rules','linux_releases') NOT NULL COMMENT 'rules: Windows approval rules',
  PRIMARY KEY (`entity_id`, `setting`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Every ancestor of each entity, the entity itself at depth 0.
-- The GLPI table is read once (GROUP BY keeps it from being merged), self
-- parents are cut and the depth is bounded against a cycle.
CREATE OR REPLACE VIEW `entity_ancestors` AS
WITH RECURSIVE
  ent AS (SELECT id,
                 CASE WHEN entities_id >= 0 AND entities_id <> id
                      THEN entities_id END AS parent_id
            FROM glpi_entities
           GROUP BY id, entities_id),
  tree AS (SELECT id AS entity_id, id AS ancestor_id, parent_id,
                  CAST(0 AS UNSIGNED) AS depth
             FROM ent
           UNION ALL
           SELECT t.entity_id, e.id, e.parent_id, t.depth + 1
             FROM tree t
             JOIN ent e ON e.id = t.parent_id
            WHERE t.depth < 32)
SELECT entity_id, ancestor_id, depth FROM tree;

-- Source of the tracked products: nearest ancestor with its own; NULL = none
CREATE OR REPLACE VIEW `effective_products` AS
SELECT s.entity_id, s.source_id
FROM (SELECT ea.entity_id, eo.entity_id AS source_id,
             ROW_NUMBER() OVER (PARTITION BY ea.entity_id
                                ORDER BY eo.entity_id IS NULL, ea.depth) AS rn
        FROM entity_ancestors ea
        LEFT JOIN entity_overrides eo
          ON eo.entity_id = ea.ancestor_id AND eo.setting = 'products') s
WHERE s.rn = 1;

-- Source of the tracked Linux versions; NULL = none
CREATE OR REPLACE VIEW `effective_linux_releases` AS
SELECT s.entity_id, s.source_id
FROM (SELECT ea.entity_id, eo.entity_id AS source_id,
             ROW_NUMBER() OVER (PARTITION BY ea.entity_id
                                ORDER BY eo.entity_id IS NULL, ea.depth) AS rn
        FROM entity_ancestors ea
        LEFT JOIN entity_overrides eo
          ON eo.entity_id = ea.ancestor_id AND eo.setting = 'linux_releases') s
WHERE s.rn = 1;

-- Source of the automatic approval rules; NULL = none
CREATE OR REPLACE VIEW `effective_rules` AS
SELECT s.entity_id, s.os, s.source_id
FROM (SELECT ea.entity_id, o.os, eo.entity_id AS source_id,
             ROW_NUMBER() OVER (PARTITION BY ea.entity_id, o.os
                                ORDER BY eo.entity_id IS NULL, ea.depth) AS rn
        FROM entity_ancestors ea
        CROSS JOIN (SELECT 'windows' AS os, 'rules' AS setting
                    UNION ALL SELECT 'linux', 'linux_rules') o
        LEFT JOIN entity_overrides eo
          ON eo.entity_id = ea.ancestor_id AND eo.setting = o.setting) s
WHERE s.rn = 1;

-- Settings of the nearest ancestor with a row; defaults without one
CREATE OR REPLACE VIEW `effective_settings` AS
SELECT s.entity_id, s.source_id,
       COALESCE(s.auto_deploy, 0) AS auto_deploy, s.window_start, s.window_end,
       s.upgrade_window_start, s.upgrade_window_end
FROM (SELECT ea.entity_id, es.entity_id AS source_id, es.auto_deploy,
             es.window_start, es.window_end, es.upgrade_window_start, es.upgrade_window_end,
             ROW_NUMBER() OVER (PARTITION BY ea.entity_id
                                ORDER BY es.entity_id IS NULL, ea.depth) AS rn
        FROM entity_ancestors ea
        LEFT JOIN entity_settings es ON es.entity_id = ea.ancestor_id) s
WHERE s.rn = 1;

-- Per update, decision of the nearest ancestor that made one
CREATE OR REPLACE VIEW `effective_approvals` AS
SELECT s.entity_id, s.update_id, s.status, s.source_id
FROM (SELECT ea.entity_id, a.update_id, a.status, a.entity_id AS source_id,
             ROW_NUMBER() OVER (PARTITION BY ea.entity_id, a.update_id
                                ORDER BY ea.depth) AS rn
        FROM entity_ancestors ea
        JOIN approvals a ON a.entity_id = ea.ancestor_id) s
WHERE s.rn = 1;

-- Approved catalog updates missing on a machine of each entity; same status
-- as the approval page: effective decision first, then an effective rule, which
-- covers the offer main only. An update offered as esu everywhere is never approved.
-- by_rule: a machine where the update is not main needs a decision (mu.offer)
CREATE OR REPLACE VIEW `approved_updates` AS
SELECT m.entity_id, m.update_id, (a.status IS NULL) AS by_rule
FROM (SELECT lgm.entities_id AS entity_id, mu.update_id, MAX(mu.offer = 'main') AS has_main
        FROM machine_reports mr
        JOIN xmppmaster.local_glpi_machines lgm
          ON mr.glpi_uuid REGEXP '^UUID[0-9]+$'
         AND lgm.id = CAST(SUBSTRING(mr.glpi_uuid, 5) AS UNSIGNED)
         AND lgm.is_deleted = 0
         AND lgm.is_template = 0
        JOIN xmppmaster.local_glpi_entities e ON e.id = lgm.entities_id
        JOIN machine_updates mu ON mu.jid = mr.jid
       WHERE mu.update_id IS NOT NULL AND mu.offer <> 'esu'
       GROUP BY lgm.entities_id, mu.update_id) m
JOIN updates u ON u.id = m.update_id
LEFT JOIN effective_approvals a ON a.entity_id = m.entity_id AND a.update_id = m.update_id
LEFT JOIN effective_rules er ON er.entity_id = m.entity_id AND er.os = 'windows'
WHERE a.status = 'approved'
   OR (a.status IS NULL AND m.has_main
       AND EXISTS (SELECT 1 FROM approval_rules ar
                    WHERE ar.entity_id = er.source_id AND ar.os = 'windows'
                      AND ar.classification = u.classification
                      AND (ar.severity IS NULL OR ar.severity = u.severity)));

-- One deployment package per distinct set of files
CREATE TABLE IF NOT EXISTS `packages` (
  `uuid` char(36) NOT NULL,
  `files_hash` char(40) NOT NULL COMMENT 'sha1 hex of the sorted file sha1s',
  `share` varchar(32) NOT NULL,
  `state` enum('building','ready','failed','unsupported') NOT NULL,
  `error` text NULL,
  `size` bigint unsigned NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ready_at` datetime NULL,
  PRIMARY KEY (`uuid`),
  UNIQUE KEY `uq_packages_files_hash` (`files_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Installation media package of an ESD, for one edition
CREATE TABLE IF NOT EXISTS `media_packages` (
  `file_name` varchar(255) NOT NULL,
  `edition` varchar(64) NOT NULL,
  `package_uuid` char(36) NOT NULL,
  PRIMARY KEY (`file_name`, `edition`),
  KEY `idx_media_packages_package` (`package_uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `update_packages` (
  `update_id` int unsigned NOT NULL,
  `package_uuid` char(36) NOT NULL,
  PRIMARY KEY (`update_id`),
  KEY `idx_update_packages_package_uuid` (`package_uuid`),
  CONSTRAINT `fk_update_packages_update` FOREIGN KEY (`update_id`) REFERENCES `updates` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_update_packages_package` FOREIGN KEY (`package_uuid`) REFERENCES `packages` (`uuid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Template table of schema 001, never used
DROP TABLE IF EXISTS `tests`;

UPDATE version SET Number = 2;
COMMIT;
