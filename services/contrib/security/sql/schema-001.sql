-- ----------------------------------------------------------------------
-- Security Module - Schema 001
-- CVE scanning and vulnerability management via CVE Central API
-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `version` (
    `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `version` VALUES (1);

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
-- Cache local des CVEs récupérées de CVE Central
-- Cette table contient TOUTES les CVEs connues pour les logiciels du parc
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `cves` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `cve_id` varchar(20) NOT NULL COMMENT 'Ex: CVE-2024-12345',
    `cvss_score` decimal(3,1) DEFAULT NULL COMMENT 'Score CVSS (0.0 - 10.0)',
    `severity` enum('Critical','High','Medium','Low','None') DEFAULT 'None',
    `description` text DEFAULT NULL,
    `published_at` date DEFAULT NULL,
    `last_modified` date DEFAULT NULL COMMENT 'Dernière modification sur NVD',
    `fetched_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Quand on a récupéré cette CVE',
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
    `software_name` varchar(255) NOT NULL,
    `software_version` varchar(100) NOT NULL,
    `cve_id` int(11) NOT NULL COMMENT 'Référence vers cves.id',
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_software_cve` (`software_name`, `software_version`, `cve_id`),
    KEY `idx_software` (`software_name`, `software_version`),
    KEY `idx_cve_id` (`cve_id`),
    CONSTRAINT `fk_software_cves_cve` FOREIGN KEY (`cve_id`) REFERENCES `cves` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Lien logiciel vers CVE';

-- ----------------------------------------------------------------------
-- Table: scans
-- Historique des scans effectués
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `scans` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `finished_at` datetime DEFAULT NULL,
    `status` enum('running','completed','failed') DEFAULT 'running',
    `softwares_sent` int(11) DEFAULT 0 COMMENT 'Nombre de logiciels envoyés à CVE Central',
    `cves_received` int(11) DEFAULT 0 COMMENT 'Nombre de CVEs reçues',
    `machines_affected` int(11) DEFAULT 0 COMMENT 'Nombre de machines avec vulnérabilités',
    `error_message` text DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_started_at` (`started_at`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Historique des scans de sécurité';

-- ----------------------------------------------------------------------
-- Table: cve_exclusions
-- CVE à ignorer (faux positifs globaux, exceptions métier)
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
-- Note: Configuration is stored in /etc/mmc/plugins/security.ini.local
-- NOT in database (following Medulla convention for module configuration)
-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Note: Les machines affectées sont calculées dynamiquement via une requête
-- qui joint les tables:
--   xmppmaster.local_glpi_machines (machines GLPI)
--   xmppmaster.local_glpi_items_softwareversions (logiciels installés)
--   xmppmaster.local_glpi_softwareversions (versions)
--   xmppmaster.local_glpi_softwares (noms)
--   security.software_cves (lien logiciel->CVE)
--   security.cves (détails CVE)
-- ----------------------------------------------------------------------
