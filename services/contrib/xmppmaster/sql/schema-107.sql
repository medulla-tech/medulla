--
-- (c) 2026, http://www.medulla-tech.io/
--
-- FILE contrib/xmppmaster/sql/schema-107.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- Elargissement de deploy.result : TEXT -> MEDIUMTEXT
--

START TRANSACTION;

USE `xmppmaster`;

-- Le recap JSON depasse ~65000 caracteres (limite TEXT) sur les paquets a
-- nombreuses dependances : tronque -> JSON invalide -> faux "PARTIAL SUCCESS".
ALTER TABLE `xmppmaster`.`deploy`
    CHANGE COLUMN `result` `result` MEDIUMTEXT NULL DEFAULT NULL;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 107;

COMMIT;
