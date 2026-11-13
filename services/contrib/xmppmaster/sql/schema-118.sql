-- SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-118.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
--

USE `xmppmaster`;

START TRANSACTION;

-- URL WebSocket (wss://host/ws) du relais XMPP, utilisee par les agents
-- qui se connectent en WebSocket (port 443 via Apache) au lieu de TCP 5222.
-- IF NOT EXISTS rend la migration rejouable sur les bases qui ont deja la colonne.
ALTER TABLE `relayserver`
    ADD COLUMN IF NOT EXISTS `websocket_url` VARCHAR(255) NULL DEFAULT NULL;

UPDATE version SET Number = 118;

COMMIT;
