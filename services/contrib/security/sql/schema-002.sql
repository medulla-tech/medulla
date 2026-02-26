START TRANSACTION;

-- Schema 002: Add sources and source_urls columns to cves table
-- Also add 'N/A' to severity enum for CVEs without CVSS score

-- Add sources column (ex: "nvd,circl,euvd")
ALTER TABLE `cves` ADD COLUMN `sources` varchar(50) DEFAULT NULL COMMENT 'Sources ayant cette CVE (ex: nvd,circl,euvd)' AFTER `last_modified`;

-- Add source_urls column (JSON, ex: {"nvd": "https://...", "circl": "https://..."})
ALTER TABLE `cves` ADD COLUMN `source_urls` text DEFAULT NULL COMMENT 'URLs des sources en JSON' AFTER `sources`;

-- Add N/A to severity enum
ALTER TABLE `cves` MODIFY COLUMN `severity` enum('Critical','High','Medium','Low','None','N/A') DEFAULT 'None';

UPDATE `version` SET `Number` = 2;

COMMIT;
