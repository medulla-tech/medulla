-- SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/updates/sql/schema-003.sql
--
-- Office Click-to-Run channels of the medulla-wsus mirror.

START TRANSACTION;

-- Update channels of Office Click-to-Run with their latest version, copied whole from the mirror.
CREATE TABLE IF NOT EXISTS `office_channels` (
  `channel_id` char(36) NOT NULL COMMENT 'Microsoft channel GUID, lowercase',
  `name` varchar(64) NOT NULL COMMENT 'e.g. Current Channel',
  `latest_version` varchar(32) NOT NULL COMMENT 'e.g. 16.0.20527.20088',
  `release_name` varchar(16) NULL COMMENT 'e.g. 2610',
  `available_at` datetime NULL,
  PRIMARY KEY (`channel_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

ALTER TABLE `replication`
  ADD COLUMN IF NOT EXISTS `office_channels_version` varchar(64) NULL COMMENT 'version of the Office channels list' AFTER `linux_releases_version`;

UPDATE version SET Number = 3;
COMMIT;
