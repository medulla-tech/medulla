-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
--
-- FILE contrib/xmppmaster/sql/schema-111.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Add websocket_url to relayserver: stores the WebSocket endpoint
-- (e.g. wss://host:5443/ws) used by agents when enable_websocket=1.
--

START TRANSACTION;

USE `xmppmaster`;

ALTER TABLE `xmppmaster`.`relayserver`
    ADD COLUMN IF NOT EXISTS `websocket_url` VARCHAR(255) NULL DEFAULT NULL
    AFTER `ssh_public_key`;

UPDATE version SET Number = 111;

COMMIT;
