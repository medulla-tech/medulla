--
-- (c) 2026 Medulla, http://www.medulla-tech.io
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/>.

SET NAMES utf8mb4;

START TRANSACTION;

-- ----------------------------------------------------------------------
-- Reflex Module - Schema 002
-- Une machine est identifiee par son nom d agent (jiduser) : la partie du
-- jid qui precede le premier @, en minuscules. xmppmaster.machines.id ne
-- survit pas a une reinscription complete de l agent, le nom d agent si.
--
-- Rejouable : une conversion qui lit machines_id n est jouee que tant que la
-- colonne existe, et celles qui n ont pas de colonne temoin
-- (probe_assignments, probe_config_changes) que tant que la version du
-- schema est inferieure a 2. Une ligne dont la machine n existe plus dans
-- xmppmaster est supprimee : la rattacher par son nom d hote serait deviner.
-- ----------------------------------------------------------------------


-- ----------------------------------------------------------------------
-- Table: probe_exclusions
-- ----------------------------------------------------------------------
ALTER TABLE `probe_exclusions`
    ADD COLUMN IF NOT EXISTS `jiduser` varchar(255) NOT NULL COMMENT 'Nom d agent : partie du jid avant le premier @, en minuscules. Pas de FK inter-bases' AFTER `probe_id`;

SET @reflex_old = (SELECT COUNT(*) FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'probe_exclusions'
                      AND COLUMN_NAME = 'machines_id');

SET @reflex_sql = IF(@reflex_old > 0,
    'UPDATE `probe_exclusions` t JOIN `xmppmaster`.`machines` xm ON xm.id = t.machines_id SET t.jiduser = LOWER(SUBSTRING_INDEX(xm.jid, ''@'', 1))',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;

DELETE FROM `probe_exclusions` WHERE `jiduser` = '';

DELETE d FROM `probe_exclusions` d
  JOIN `probe_exclusions` k
    ON k.probe_id = d.probe_id AND k.jiduser = d.jiduser AND k.id < d.id;

SET @reflex_sql = IF(@reflex_old > 0,
    'ALTER TABLE `probe_exclusions` DROP INDEX IF EXISTS `uk_probe_machine`, DROP INDEX IF EXISTS `idx_machine`, DROP COLUMN IF EXISTS `machines_id`, ADD UNIQUE KEY `uk_probe_machine` (`probe_id`, `jiduser`) COMMENT ''Une machine n est exclue qu une fois d une sonde'', ADD KEY `idx_machine` (`jiduser`) COMMENT ''Exclusions d une machine, pour sa fiche''',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;


-- ----------------------------------------------------------------------
-- Table: probe_agent_config
-- Deux lignes pour un meme agent : la plus recemment mise a jour reste.
-- ----------------------------------------------------------------------
ALTER TABLE `probe_agent_config`
    ADD COLUMN IF NOT EXISTS `jiduser` varchar(255) NOT NULL COMMENT 'Nom d agent : partie du jid avant le premier @, en minuscules' AFTER `id`;

SET @reflex_old = (SELECT COUNT(*) FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'probe_agent_config'
                      AND COLUMN_NAME = 'machines_id');

SET @reflex_sql = IF(@reflex_old > 0,
    'UPDATE `probe_agent_config` t JOIN `xmppmaster`.`machines` xm ON xm.id = t.machines_id SET t.jiduser = LOWER(SUBSTRING_INDEX(xm.jid, ''@'', 1)), t.updated_at = t.updated_at',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;

DELETE FROM `probe_agent_config` WHERE `jiduser` = '';

DELETE d FROM `probe_agent_config` d
  JOIN `probe_agent_config` k
    ON k.jiduser = d.jiduser
   AND (k.updated_at > d.updated_at
        OR (k.updated_at = d.updated_at AND k.id > d.id));

SET @reflex_sql = IF(@reflex_old > 0,
    'ALTER TABLE `probe_agent_config` DROP INDEX IF EXISTS `uk_machine`, DROP COLUMN IF EXISTS `machines_id`, ADD UNIQUE KEY `uk_machine` (`jiduser`)',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;


-- ----------------------------------------------------------------------
-- Table: probe_measures
-- Un seul ALTER pour retirer la colonne et reposer les deux index : la
-- table est la plus volumineuse du module, elle n est reconstruite qu une
-- fois.
-- ----------------------------------------------------------------------
ALTER TABLE `probe_measures`
    ADD COLUMN IF NOT EXISTS `jiduser` varchar(255) NOT NULL COMMENT 'Nom d agent : partie du jid avant le premier @, en minuscules. Pas de FK inter-bases' AFTER `id`;

SET @reflex_old = (SELECT COUNT(*) FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'probe_measures'
                      AND COLUMN_NAME = 'machines_id');

-- received_at est repose a l identique : la colonne est un timestamp, que
-- le serveur peut vouloir rafraichir a chaque ecriture de la ligne.
SET @reflex_sql = IF(@reflex_old > 0,
    'UPDATE `probe_measures` t JOIN `xmppmaster`.`machines` xm ON xm.id = t.machines_id SET t.jiduser = LOWER(SUBSTRING_INDEX(xm.jid, ''@'', 1)), t.received_at = t.received_at',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;

DELETE FROM `probe_measures` WHERE `jiduser` = '';

SET @reflex_sql = IF(@reflex_old > 0,
    'ALTER TABLE `probe_measures` DROP INDEX IF EXISTS `idx_machine_probe_time`, DROP INDEX IF EXISTS `idx_recent_activity`, DROP COLUMN IF EXISTS `machines_id`, ADD KEY `idx_machine_probe_time` (`jiduser`, `probe_id`, `received_at`) COMMENT ''Series temporelles et derniere mesure par sonde : sur received_at, la seule horloge fiable'', ADD KEY `idx_recent_activity` (`received_at`, `jiduser`, `probe_id`) COMMENT ''Agregats bornes des pages Machines et tableau de bord : sans lui, connaitre l activite recente impose de parcourir tout l historique''',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;


-- ----------------------------------------------------------------------
-- Table: alerts
-- ----------------------------------------------------------------------
ALTER TABLE `alerts`
    ADD COLUMN IF NOT EXISTS `jiduser` varchar(255) NOT NULL COMMENT 'Nom d agent : partie du jid avant le premier @, en minuscules' AFTER `condition_id`;

SET @reflex_old = (SELECT COUNT(*) FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                      AND TABLE_NAME = 'alerts'
                      AND COLUMN_NAME = 'machines_id');

SET @reflex_sql = IF(@reflex_old > 0,
    'UPDATE `alerts` t JOIN `xmppmaster`.`machines` xm ON xm.id = t.machines_id SET t.jiduser = LOWER(SUBSTRING_INDEX(xm.jid, ''@'', 1))',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;

DELETE FROM `alerts` WHERE `jiduser` = '';

SET @reflex_sql = IF(@reflex_old > 0,
    'ALTER TABLE `alerts` DROP INDEX IF EXISTS `idx_machine_status`, DROP INDEX IF EXISTS `idx_open_dedup`, DROP COLUMN IF EXISTS `machines_id`, ADD KEY `idx_machine_status` (`jiduser`, `status`), ADD KEY `idx_open_dedup` (`probe_id`, `condition_id`, `jiduser`, `status`) COMMENT ''Recherche de l alerte ouverte a mettre a jour''',
    'DO 0');
PREPARE reflex_stmt FROM @reflex_sql;
EXECUTE reflex_stmt;
DEALLOCATE PREPARE reflex_stmt;


-- ----------------------------------------------------------------------
-- Table: probe_assignments
-- target_id porte le nom d agent quand target_type = machine. Pas de
-- colonne temoin : la conversion ne touche que les valeurs numeriques, tant
-- que le schema n est pas en version 2. UPDATE IGNORE : deux lignes
-- xmppmaster d un meme agent donneraient deux poses identiques, la seconde
-- reste numerique et part avec les poses non resolues.
-- ----------------------------------------------------------------------
ALTER TABLE `probe_assignments`
    MODIFY `target_id` varchar(255) NOT NULL COMMENT 'Nom d agent (jiduser), id de groupe dyngroup ou id d entite GLPI selon target_type. Jamais NULL : MySQL tient deux NULL pour distincts et uk_probe_target ne verrait pas une seconde pose. Pas de valeur par defaut : l appelant nomme toujours sa cible';

UPDATE IGNORE `probe_assignments` pa
  JOIN `xmppmaster`.`machines` xm
    ON xm.id = CAST(CASE WHEN pa.target_id REGEXP '^[0-9]+$' THEN pa.target_id END AS UNSIGNED)
   SET pa.target_id = LOWER(SUBSTRING_INDEX(xm.jid, '@', 1))
 WHERE pa.target_type = 'machine'
   AND pa.target_id REGEXP '^[0-9]+$'
   AND xm.jid <> ''
   AND (SELECT MAX(`Number`) FROM `version`) < 2;

DELETE FROM `probe_assignments`
 WHERE `target_type` = 'machine'
   AND `target_id` REGEXP '^[0-9]+$'
   AND (SELECT MAX(`Number`) FROM `version`) < 2;


-- ----------------------------------------------------------------------
-- Table: probe_config_changes
-- scope_id porte un nom d agent pour le perimetre machine, un identifiant
-- ecrit en texte pour les autres.
-- ----------------------------------------------------------------------
ALTER TABLE `probe_config_changes`
    MODIFY `scope_id` varchar(255) NULL DEFAULT NULL COMMENT 'Nom d agent (jiduser), id de groupe dyngroup, id d entite GLPI ou probes.id selon scope_type. NULL quand scope_type = all';

UPDATE `probe_config_changes` pcc
  JOIN `xmppmaster`.`machines` xm
    ON xm.id = CAST(CASE WHEN pcc.scope_id REGEXP '^[0-9]+$' THEN pcc.scope_id END AS UNSIGNED)
   SET pcc.scope_id = LOWER(SUBSTRING_INDEX(xm.jid, '@', 1))
 WHERE pcc.scope_type = 'machine'
   AND pcc.scope_id REGEXP '^[0-9]+$'
   AND xm.jid <> ''
   AND (SELECT MAX(`Number`) FROM `version`) < 2;

DELETE FROM `probe_config_changes`
 WHERE `scope_type` = 'machine'
   AND `scope_id` REGEXP '^[0-9]+$'
   AND (SELECT MAX(`Number`) FROM `version`) < 2;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 2;

COMMIT;
