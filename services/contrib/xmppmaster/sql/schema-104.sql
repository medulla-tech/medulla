--
-- (c) 2026, http://www.medulla-tech.io/
--
-- FILE contrib/xmppmaster/sql/schema-104.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- Correction du label partage entre deux statuts de deploiement.
--
-- Les regles 'ABORT ON TIMEOUT' et 'ABORT RESUMPTION ERROR' pointaient
-- toutes les deux sur le meme label interne 'abortontimeout'. Comme le
-- code (camembert et creation de groupe au clic) indexe ces regles par
-- label (le dernier ecrase le premier), la part "abortontimeout" etait
-- nommee a tort "Abort resumption error", et le clic filtrait les
-- machines sur le statut 'ABORT RESUMPTION ERROR' (absent en base, les
-- machines etant en 'ABORT ON TIMEOUT') -> groupe vide.
--
-- On donne un label propre a 'ABORT RESUMPTION ERROR' pour separer les
-- deux cas : l'affichage redevient correct et le clic cree le groupe
-- avec les bonnes machines.

START TRANSACTION;

USE `xmppmaster`;

UPDATE `def_remote_deploy_status`
SET `label` = 'abortresumptionerror'
WHERE `status` = 'ABORT RESUMPTION ERROR'
  AND `label`  = 'abortontimeout';


-- 1. Table des CVE
CREATE TABLE IF NOT EXISTS up_cve_linux (
    id INT(11) NOT NULL AUTO_INCREMENT,
    cve VARCHAR(32) NOT NULL,
    severity INT(11),
    description VARCHAR(128),
    PRIMARY KEY (id),
    UNIQUE KEY (cve)
) ENGINE=InnoDB;


-- 2. Table des packages
CREATE TABLE IF NOT EXISTS  up_package_linux (
    id INT(11) NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(255),
    PRIMARY KEY (id),
    UNIQUE KEY (name, version)
) ENGINE=InnoDB;


-- 3. Table de jointure entre CVE et packages
CREATE TABLE IF NOT EXISTS up_package_cve_linux (
    package_id INT(11) NOT NULL,
    cve_id INT(11) NOT NULL,
    PRIMARY KEY (package_id, cve_id),
    FOREIGN KEY (package_id) REFERENCES up_package_linux(id) ON DELETE CASCADE,
    FOREIGN KEY (cve_id) REFERENCES up_cve_linux(id) ON DELETE CASCADE,
    INDEX idx_up_package_cve_linux_cve_package (cve_id, package_id)
) ENGINE=InnoDB;


-- 4. Table des machines
CREATE TABLE `up_machine_linux` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) NOT NULL,
  `harduuid` varchar(64) NOT NULL,
  `distributor_id` varchar(64) DEFAULT NULL,
  `description` varchar(128) DEFAULT NULL,
  `release_version` varchar(32) DEFAULT NULL,
  `codename` varchar(64) DEFAULT NULL,
  `kernel_version` varchar(64) DEFAULT '0',
  `security_count` int(11) DEFAULT 0,
  `security_require` tinyint(1) DEFAULT 0,
  `security_curent` tinyint(1) DEFAULT 0,
  `security_start` datetime DEFAULT NULL,
  `security_stop` datetime DEFAULT NULL,
  `security_login` varchar(64) DEFAULT '0',
  `security_interval` varchar(64) DEFAULT '0',
  `kernel_count` int(11) DEFAULT 0,
  `kernel_require` tinyint(1) DEFAULT 0 COMMENT 'curent_deploy, de.required_deploy',
  `kernel_current` tinyint(1) DEFAULT 0,
  `kernel_start` datetime DEFAULT NULL,
  `kernel_stop` datetime DEFAULT NULL,
  `kernel_login` varchar(64) DEFAULT '0',
  `kernel_interval` varchar(64) DEFAULT '0',
  `other_count` int(11) DEFAULT 0,
  `other_require` tinyint(1) DEFAULT 0,
  `other_current` tinyint(1) DEFAULT 0,
  `other_start` datetime DEFAULT NULL,
  `other_stop` datetime DEFAULT NULL,
  `other_login` varchar(64) DEFAULT '0',
  `other_interval` varchar(64) DEFAULT '0',
  `total_count` int(11) DEFAULT 0,
  `last_scan` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `harduuid` (`harduuid`),
  KEY `idx_last_scan` (`last_scan`),
  KEY `idx_kernel_require` (`kernel_require`),
  KEY `idx_distributor_id` (`distributor_id`),
  KEY `idx_kernel_version` (`kernel_version`),
  KEY `idx_security_require` (`security_require`),
  KEY `idx_other_require` (`other_require`),
  KEY `idx_security_start` (`security_start`),
  KEY `idx_security_stop` (`security_stop`),
  KEY `idx_kernel_start` (`kernel_start`),
  KEY `idx_kernel_stop` (`kernel_stop`),
  KEY `idx_other_start` (`other_start`),
  KEY `idx_other_stop` (`other_stop`),
  KEY `idx_security_login` (`security_login`),
  KEY `idx_kernel_login` (`kernel_login`),
  KEY `idx_other_login` (`other_login`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- 5. Table des mises à jour des machines
CREATE TABLE IF NOT EXISTS up_machine_update_linux (
    id INT(11) NOT NULL AUTO_INCREMENT,
    machine_id INT(11) NOT NULL,
    package_id INT(11) NOT NULL,
    type ENUM('security', 'kernel', 'other', 'normal') NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (machine_id) REFERENCES up_machine_linux(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES up_package_linux(id) ON DELETE CASCADE,
    INDEX idx_up_machine_update_linux_machine_package (machine_id, package_id),
    INDEX idx_up_machine_update_linux_package_machine (package_id, machine_id),
    INDEX idx_up_machine_update_linux_machine_type (machine_id, type)
) ENGINE=InnoDB;


CREATE TABLE `up_rhel_versions` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique de la version RHEL',
  `version` int(11) NOT NULL COMMENT 'Numéro de version RHEL (ex: 10, 9, 8)',
  `name` varchar(45) DEFAULT NULL COMMENT 'Nom de code de la version RHEL (si applicable)',
  `is_managed` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est suivie / gérée par le système',
  `is_current_stable` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est actuellement la version stable officielle',
  `is_latest_lts` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est la dernière version LTS prise en compte',
  `end_standard_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité standard',
  `end_els_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité ELS (Extended Life Cycle Support)',
  `description` varchar(255) DEFAULT NULL COMMENT 'Description ou informations complémentaires sur la version',
  `package` varchar(36) DEFAULT NULL,
  `packagename` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_version` (`version`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Liste des versions RHEL et état de leur support (stable, ELS)';


CREATE TABLE `up_debian_versions` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique de la version Debian',
  `version` int(11) NOT NULL COMMENT 'Numéro de version Debian (ex: Numéro de version Debian 13, 12, 11 pour Bookworm)',
  `name` varchar(45) NOT NULL COMMENT 'Nom de la version Debian (ex: Bookworm)',
  `is_managed` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est suivie / gérée par le système',
  `is_current_stable` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est actuellement la version stable officielle',
  `is_latest_lts` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est la dernière version LTS prise en compte',
  `end_standard_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité standard (hors LTS)',
  `end_lts_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité LTS',
  `end_elts_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité ELTS (support étendu payant)',
  `description` varchar(100) DEFAULT NULL COMMENT 'Description ou informations complémentaires sur la version',
  `package` varchar(36) DEFAULT NULL,
  `packagename` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_version` (`version`),
  UNIQUE KEY `uniq_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Liste des versions Debian et état de leur support (stable, LTS, ELTS)';


CREATE TABLE `up_ubuntu_versions` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique de la version Ubuntu',
  `version` varchar(10) NOT NULL COMMENT 'Numéro de version Ubuntu (ex: 24.04, 22.04)',
  `name` varchar(45) NOT NULL COMMENT 'Nom de code de la version Ubuntu (ex: Noble Numbat)',
  `is_managed` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est suivie / gérée par le système',
  `is_current_stable` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est actuellement la version stable officielle',
  `is_latest_lts` tinyint(1) NOT NULL DEFAULT 0 COMMENT 'Indique si cette version est la dernière version LTS prise en compte',
  `end_standard_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité standard (hors LTS)',
  `end_lts_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité LTS',
  `end_esm_support` datetime DEFAULT NULL COMMENT 'Date de fin du support de sécurité ESM (Extended Security Maintenance)',
  `description` varchar(255) DEFAULT NULL COMMENT 'Description ou informations complémentaires sur la version',
  `package` varchar(36) DEFAULT NULL,
  `packagename` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_version` (`version`),
  UNIQUE KEY `uniq_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Liste des versions Ubuntu et état de leur support (stable, LTS, ESM)';


-- ================================================
-- Seed data: RHEL versions (imported from legacy dump)
-- ================================================
DELETE FROM `up_rhel_versions`;
INSERT INTO `up_rhel_versions`
(`id`, `version`, `name`, `is_managed`, `is_current_stable`, `is_latest_lts`, `end_standard_support`, `end_els_support`, `description`, `package`, `packagename`)
VALUES
(1, 10, 'RHEL 10', 1, 1, 1, '2030-05-31 00:00:00', '2038-05-31 00:00:00', 'RHEL 10', NULL, NULL),
(2, 9, 'RHEL 9', 1, 0, 0, '2027-05-31 00:00:00', '2035-05-31 00:00:00', 'RHEL 9', NULL, NULL),
(3, 8, 'RHEL 8', 1, 0, 0, '2024-05-31 00:00:00', '2032-05-31 00:00:00', 'RHEL 8', NULL, NULL);


-- ================================================
-- Seed data: ubuntu versions (imported from legacy dump)
-- ================================================
DELETE FROM `up_ubuntu_versions`;
INSERT INTO `up_ubuntu_versions`
(`id`, `version`, `name`, `is_managed`, `is_current_stable`, `is_latest_lts`, `end_standard_support`, `end_lts_support`, `end_esm_support`, `description`, `package`, `packagename`)
VALUES
(1, '26.04', 'Resolute Raccoon', 1, 1, 1, '2031-05-31 00:00:00', '2036-04-30 00:00:00', '2041-04-30 00:00:00', 'Version LTS actuelle', NULL, NULL),
(2, '24.04', 'Noble Numbat', 1, 0, 0, '2029-06-30 00:00:00', '2034-04-30 00:00:00', '2039-04-30 00:00:00', 'Version LTS précédente', NULL, NULL),
(3, '22.04', 'Jammy Jellyfish', 1, 0, 0, '2027-06-30 00:00:00', '2032-04-30 00:00:00', '2037-04-30 00:00:00', 'Version LTS encore utilisée', NULL, NULL),
(4, '20.04', 'Focal Fossa', 0, 0, 0, '2025-05-31 00:00:00', '2030-04-30 00:00:00', '2035-04-30 00:00:00', 'Version anciennement LTS', NULL, NULL);


-- ================================================
-- Seed data: Debian versions (imported from legacy dump)
-- ================================================
DELETE FROM `up_debian_versions`;
INSERT INTO `up_debian_versions` VALUES
(1,15,'Duke',0,0,0,NULL,NULL,NULL,'Nom de code annoncé, version non publiée',NULL,NULL),
(2,14,'Forky',0,0,0,NULL,NULL,NULL,'Version testing, date de publication non définie',NULL,NULL),
(3,13,'Trixie',1,1,0,'2028-08-09 00:00:00','2030-06-30 00:00:00','2035-06-30 00:00:00','Version stable actuelle','633eeeb2-upgradereleasedebiantotrixi','debian-upgrade-trixie'),
(4,12,'Bookworm',1,0,0,'2026-06-10 00:00:00','2028-06-30 00:00:00','2033-06-30 00:00:00','Version oldstable actuelle',NULL,NULL),
(5,11,'Bullseye',1,0,1,'2024-08-14 00:00:00','2026-08-31 00:00:00','2031-06-30 00:00:00','Version oldoldstable actuelle, prise en charge LTS',NULL,NULL),
(6,10,'Buster',0,0,0,'2022-09-10 00:00:00','2024-06-30 00:00:00','2029-06-30 00:00:00','Version archivée, prise en charge étendue LTS avec rémunération de tiers',NULL,NULL),
(7,9,'Stretch',0,0,0,'2020-07-18 00:00:00','2022-07-01 00:00:00','2027-06-30 00:00:00','Version archivée, prise en charge étendue LTS avec rémunération de tiers',NULL,NULL);

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 104;

commit;
