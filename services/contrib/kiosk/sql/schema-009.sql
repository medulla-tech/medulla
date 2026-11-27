-- SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/kiosk/sql/schema-009.sql
--
-- =======================================
-- Database kiosk
-- =======================================
-- A profile belongs to one GLPI entity. Installation requests are removed.

USE `kiosk`;

START TRANSACTION;

ALTER TABLE `profiles`
    ADD COLUMN IF NOT EXISTS `entity_id` INT UNSIGNED NULL COMMENT 'GLPI entity' AFTER `owner`;
ALTER TABLE `profiles`
    ADD INDEX IF NOT EXISTS `ind_profiles_entity` (`entity_id`);

-- Restricted packages needed an accepted request to be installed
DELETE FROM `package_has_profil` WHERE `package_status` = 'restricted';

DROP TABLE IF EXISTS `acknowledgements`;
DROP TABLE IF EXISTS `package`;
DROP TABLE IF EXISTS `groups`;
DROP TABLE IF EXISTS `has_machine_groups`;

UPDATE version SET Number = 9;

COMMIT;
