--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
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
-- along with MMC; If not, see <http://www.gnu.org/licenses/.>

START TRANSACTION;

-- ----------------------------------------------------------------------
-- Security Module - Schema 001
-- CVE scanning and vulnerability management via CVE Central API
-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Table: tests (legacy, for module activation test)
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tests` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(50) NOT NULL,
    `message` varchar(255) NULL,
    PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `tests` (`name`, `message`) VALUES
    ('msg1', 'My message 1'),
    ('msg2', 'My message 2');

-- ----------------------------------------------------------------------
-- Table: cves
-- Cache local des CVEs recuperees de CVE Central
-- Cette table contient TOUTES les CVEs connues pour les logiciels du parc
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cves` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `cve_id` varchar(20) NOT NULL COMMENT 'Ex: CVE-2024-12345',
    `cvss_score` decimal(3,1) DEFAULT NULL COMMENT 'Score CVSS (0.0 - 10.0)',
    `severity` enum('Critical','High','Medium','Low','None') DEFAULT 'None',
    `description` text DEFAULT NULL,
    `published_at` date DEFAULT NULL,
    `last_modified` date DEFAULT NULL COMMENT 'Derniere modification sur NVD',
    `fetched_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Quand on a recupere cette CVE',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_cve_id` (`cve_id`),
    KEY `idx_severity` (`severity`),
    KEY `idx_cvss` (`cvss_score`),
    KEY `idx_published` (`published_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Cache local des CVEs';

-- ----------------------------------------------------------------------
-- Table: software_cves
-- Lien entre logiciels et CVEs
-- Un logiciel (nom+version) peut avoir plusieurs CVEs
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_cves` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `software_name` varchar(255) NOT NULL COMMENT 'Nom normalise (ex: Python)',
    `software_version` varchar(100) NOT NULL COMMENT 'Version normalisee (ex: 3.11.9)',
    `glpi_software_name` varchar(255) DEFAULT NULL COMMENT 'Nom original GLPI pour jointure (ex: Python 3.11.9 (64-bit))',
    `target_platform` varchar(50) DEFAULT NULL COMMENT 'Plateforme cible depuis CPE (android, macos, ios, windows, etc.)',
    `cve_id` int(11) NOT NULL COMMENT 'Reference vers cves.id',
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_software_cve` (`software_name`, `software_version`, `cve_id`),
    KEY `idx_software` (`software_name`, `software_version`),
    KEY `idx_glpi_software` (`glpi_software_name`),
    KEY `idx_cve_id` (`cve_id`),
    CONSTRAINT `fk_software_cves_cve` FOREIGN KEY (`cve_id`) REFERENCES `cves` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Lien logiciel vers CVE';

-- ----------------------------------------------------------------------
-- Table: scans
-- Historique des scans effectues
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `scans` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `finished_at` datetime DEFAULT NULL,
    `status` enum('running','completed','failed') DEFAULT 'running',
    `softwares_sent` int(11) DEFAULT 0 COMMENT 'Nombre de logiciels envoyes a CVE Central',
    `cves_received` int(11) DEFAULT 0 COMMENT 'Nombre de CVEs reçues',
    `machines_affected` int(11) DEFAULT 0 COMMENT 'Nombre de machines avec vulnerabilites',
    `error_message` text DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_started_at` (`started_at`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historique des scans de securite';

-- ----------------------------------------------------------------------
-- Table: cve_exclusions
-- CVE a ignorer (faux positifs globaux, exceptions metier)
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cve_exclusions` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `cve_id` varchar(20) NOT NULL,
    `reason` text DEFAULT NULL,
    `excluded_by` varchar(100) DEFAULT NULL,
    `excluded_at` datetime DEFAULT CURRENT_TIMESTAMP,
    `expires_at` datetime DEFAULT NULL COMMENT 'NULL = permanent',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_cve_id` (`cve_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CVE exclues des rapports';

-- ----------------------------------------------------------------------
-- Table: policies
-- Policies editables via UI (display, alert, exclusions)
-- Priorite: DB > security.ini.local > security.ini
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `policies` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `category` varchar(50) NOT NULL COMMENT 'display, policy, exclusions',
    `key` varchar(100) NOT NULL,
    `value` text DEFAULT NULL,
    `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `updated_by` varchar(100) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_category_key` (`category`, `key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Policies editables via UI';

-- Default policies for security module
--   - min_cvss: 4.0 (ignore minor CVEs with score < 4)
--   - min_severity: Medium (ignore Low severity CVEs)
--   - show_patched: true (show CVEs that have a fix available)
--   - max_age_days: 365 (show only CVEs from the last year)
--   - min_published_year: 2020 (ignore CVEs published before 2020)
--   - exclusions: empty by default (vendors, names, cve_ids)
INSERT INTO `policies` (`category`, `key`, `value`, `updated_at`, `updated_by`) VALUES
('display', 'min_cvss', '4.0', NOW(), 'root'),
('display', 'min_severity', 'Medium', NOW(), 'root'),
('display', 'show_patched', 'true', NOW(), 'root'),
('display', 'max_age_days', '365', NOW(), 'root'),
('display', 'min_published_year', '2020', NOW(), 'root'),
('exclusions', 'vendors', '[]', NOW(), 'root'),
('exclusions', 'names', '[]', NOW(), 'root'),
('exclusions', 'cve_ids', '[]', NOW(), 'root');

-- ----------------------------------------------------------------------
-- Note: Configuration is stored in /etc/mmc/plugins/security.ini.local
-- NOT in database (following Medulla convention for module configuration)
-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Note: Les machines affectees sont calculees dynamiquement via une requête
-- qui joint les tables:
--   xmppmaster.local_glpi_machines (machines GLPI)
--   xmppmaster.local_glpi_items_softwareversions (logiciels installes)
--   xmppmaster.local_glpi_softwareversions (versions)
--   xmppmaster.local_glpi_softwares (noms)
--   security.software_cves (lien logiciel->CVE)
--   security.cves (details CVE)
-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

--
-- Table structure for table `version`
--

CREATE TABLE IF NOT EXISTS `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO `version` VALUES (1);

COMMIT;
