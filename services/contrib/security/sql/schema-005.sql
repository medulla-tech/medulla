START TRANSACTION;

-- Schema 005: CVE Central v2. Replayable.
-- software_cves keyed by the raw GLPI name and version (= glpi_softwares.name, glpi_softwareversions.name)

UPDATE `software_cves` SET `glpi_software_name` = `software_name` WHERE `glpi_software_name` IS NULL;

DELETE sc FROM `software_cves` sc
JOIN `software_cves` dup
  ON dup.`glpi_software_name` = sc.`glpi_software_name`
 AND dup.`software_version` = sc.`software_version`
 AND dup.`cve_id` = sc.`cve_id`
 AND dup.`id` < sc.`id`;

ALTER TABLE `software_cves`
    MODIFY COLUMN `glpi_software_name` varchar(255) NOT NULL COMMENT 'Nom GLPI brut (glpi_softwares.name)',
    MODIFY COLUMN `software_version` varchar(255) NOT NULL COMMENT 'Version GLPI brute (glpi_softwareversions.name)',
    ADD COLUMN IF NOT EXISTS `fix_available` tinyint(1) DEFAULT NULL COMMENT 'Version corrigée connue (NULL : inconnu)' AFTER `target_platform`;

ALTER TABLE `software_cves` DROP INDEX IF EXISTS `uk_software_cve`;
ALTER TABLE `software_cves` DROP INDEX IF EXISTS `idx_glpi_software`;
ALTER TABLE `software_cves`
    ADD UNIQUE KEY IF NOT EXISTS `uk_glpi_software_cve` (`glpi_software_name`, `software_version`, `cve_id`);

ALTER TABLE `cves`
    ADD COLUMN IF NOT EXISTS `exploited_since` date DEFAULT NULL COMMENT 'Known exploited since (KEV)' AFTER `last_modified`,
    ADD COLUMN IF NOT EXISTS `euvd_id` varchar(30) DEFAULT NULL COMMENT 'Ex: EUVD-2024-12345' AFTER `exploited_since`;

ALTER TABLE `scans` DROP COLUMN IF EXISTS `machines_affected`;

-- show_patched (never used) replaced by show_unfixed
INSERT IGNORE INTO `policies_defaults` (`category`, `key`, `value`) VALUES ('display', 'show_unfixed', 'false');
INSERT IGNORE INTO `policies` (`category`, `key`, `value`, `updated_at`, `updated_by`)
    VALUES ('display', 'show_unfixed', 'false', NOW(), 'system');
-- min_cvss duplicated min_severity (severity = CVSS range): only the severity is kept
DELETE FROM `policies_defaults` WHERE `category` = 'display' AND `key` IN ('show_patched', 'min_cvss');
DELETE FROM `policies` WHERE `category` = 'display' AND `key` IN ('show_patched', 'min_cvss');

UPDATE `version` SET `Number` = 5;

COMMIT;
