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


-- Change event schedule to every 5 minutes instead of every 1 minute to allow previous event to finish before next one starts
DROP EVENT IF EXISTS xmppmaster.ev_process_pending_events;
CREATE EVENT IF NOT EXISTS xmppmaster.ev_process_pending_events
ON SCHEDULE EVERY 5 MINUTE
DO
    CALL xmppmaster.up_event_move_to_white_list();


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 107;

COMMIT;
