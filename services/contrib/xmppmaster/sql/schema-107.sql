-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
--
-- FILE contrib/xmppmaster/sql/schema-107.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Ajout de la table reset_machine : file d'attente de reinitialisation
-- forcee de la base agent sur les machines problematiques.
--
-- Usage : l'administrateur inscrit un JID dans cette table.
-- Le plugin_resetagent (master substitut) detecte la machine quand elle
-- passe en ligne, envoie l'ordre de reset, puis supprime la ligne.
-- Les machines hors ligne sont conservees avec un compteur de tentatives.
--

START TRANSACTION;

USE `xmppmaster`;

CREATE TABLE IF NOT EXISTS `reset_machine` (
    `id`           INT(11)      NOT NULL AUTO_INCREMENT,
    `jid`          VARCHAR(255) NOT NULL,
    `reason`       VARCHAR(255) NOT NULL DEFAULT '',
    `date_request` DATETIME     DEFAULT CURRENT_TIMESTAMP,
    `nb_attempt`   INT(11)      NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uniq_jid` (`jid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

UPDATE version SET Number = 107;

COMMIT;
