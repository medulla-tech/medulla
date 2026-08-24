-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
--
-- FILE contrib/xmppmaster/sql/schema-110.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Ajout de commentaires de colonnes pour reset_machine
-- + ajout de la Quick Action de reset agent dans qa_custom_command
--

START TRANSACTION;

USE `xmppmaster`;

ALTER TABLE `reset_machine`
    MODIFY `id` INT(11) NOT NULL AUTO_INCREMENT
        COMMENT 'Identifiant technique unique de la demande de reset.',
    MODIFY `jid` VARCHAR(255) NOT NULL
        COMMENT 'JID complet de la machine cible a reinitialiser (ex: uuid@domain/resource).',
    MODIFY `reason` VARCHAR(255) NOT NULL DEFAULT ''
        COMMENT 'Motif operateur du reset force (trace fonctionnelle).',
    MODIFY `date_request` DATETIME DEFAULT CURRENT_TIMESTAMP
        COMMENT 'Date/heure de creation de la demande de reset.',
    MODIFY `nb_attempt` INT(11) NOT NULL DEFAULT 0
        COMMENT 'Compteur de tentatives de traitement tant que la machine reste indisponible.';

INSERT INTO `qa_custom_command` (`user`, `os`, `namecmd`, `customcmd`, `description`) VALUES
('allusers', 'windows', 'Reset Medulla Agent base', 'plugin_resetagent@_@Requested from Medulla Quick Action', 'Force reset of Medulla agent base files'),
('allusers', 'linux',   'Reset Medulla Agent base', 'plugin_resetagent@_@Requested from Medulla Quick Action', 'Force reset of Medulla agent base files'),
('allusers', 'macos',   'Reset Medulla Agent base', 'plugin_resetagent@_@Requested from Medulla Quick Action', 'Force reset of Medulla agent base files')
ON DUPLICATE KEY UPDATE
    `customcmd` = VALUES(`customcmd`),
    `description` = VALUES(`description`);

UPDATE version SET Number = 110;

COMMIT;
