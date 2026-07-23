-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
--
-- FILE contrib/xmppmaster/sql/schema-106.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;

USE `xmppmaster`;

ALTER TABLE xmppmaster.up_white_list
DROP PRIMARY KEY,
ADD PRIMARY KEY (updateid, entityid);


ALTER TABLE xmppmaster.up_white_list
DROP INDEX IF EXISTS uniq_update_entity_white;


ALTER TABLE xmppmaster.up_gray_list
DROP PRIMARY KEY,
ADD PRIMARY KEY (updateid, entityid);


ALTER TABLE xmppmaster.up_gray_list
DROP INDEX IF EXISTS uniq_update_entity;


ALTER TABLE xmppmaster.up_gray_list_flop
DROP PRIMARY KEY,
ADD PRIMARY KEY (updateid, entityid);


ALTER TABLE xmppmaster.up_gray_list_flop
DROP INDEX IF EXISTS uniq_update_entity_flop;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 106;

COMMIT;
