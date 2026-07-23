--
-- (c) 2026, http://www.medulla-tech.io/
--
-- FILE contrib/xmppmaster/sql/schema-107.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- 1. Elargissement de deploy.result : TEXT -> MEDIUMTEXT
-- 2. Correctif : propagation de entityid dans pending_events
-- 3. Correctif : PK composite (updateid, entityid) sur up_white_list,
--                up_gray_list et up_gray_list_flop (blocage silencieux
--                des approbations Windows Update en multi-entite).
--

START TRANSACTION;

USE `xmppmaster`;

-- =====================================================================
-- 1. Elargissement de deploy.result : TEXT -> MEDIUMTEXT
-- =====================================================================
-- Le recap JSON depasse ~65000 caracteres (limite TEXT) sur les paquets a
-- nombreuses dependances : tronque -> JSON invalide -> faux "PARTIAL SUCCESS".
ALTER TABLE `xmppmaster`.`deploy`
    CHANGE COLUMN `result` `result` MEDIUMTEXT NULL DEFAULT NULL;

-- 2a. Ajout de entityid dans pending_events
ALTER TABLE `xmppmaster`.`pending_events`
    ADD COLUMN IF NOT EXISTS `entityid` INT(11) NOT NULL AFTER `updateid`;

ALTER TABLE `xmppmaster`.`pending_events`
    ADD UNIQUE INDEX IF NOT EXISTS `uniq_update_entity_pending` (`updateid`, `entityid`);

-- 2b. Correctif du trigger up_gray_list_AFTER_INSERT
--     Ajout de NEW.entityid dans l'INSERT vers pending_events
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_gray_list_AFTER_INSERT`
AFTER INSERT ON xmppmaster.`up_gray_list`
FOR EACH ROW
BEGIN
    -- =====================================================================
    -- Trigger : up_gray_list_AFTER_INSERT
    -- Description :
    --   Execute apres l'insertion d'une nouvelle entree dans `up_gray_list`.
    --   Gere l'ajout de commandes de mise a jour et verifie si l'entree
    --   doit etre automatiquement approuvee selon des regles predefinies.
    --
    -- Fonctionnement :
    --   - Construit une commande pour `medulla_mysql_exec_update.sh`.
    --   - Insere l'action dans `up_action_update_packages`.
    --   - Enregistre un log dans `logs`.
    --   - Recupere les metadonnees (msrcseverity, updateclassification).
    --   - Verifie les regles actives dans `up_auto_approve_rules` pour l'entite.
    --   - Si regle trouvee : INSERT IGNORE dans `pending_events` AVEC entityid.
    --
    -- Correctif schema-107 :
    --   NEW.entityid est maintenant inclus dans l'INSERT vers pending_events.
    -- =====================================================================

    DECLARE v_msrcseverity VARCHAR(255);
    DECLARE v_updateclassification VARCHAR(255);
    DECLARE v_exists_rule INT DEFAULT 0;
    DECLARE v_logtext VARCHAR(500);
    DECLARE v_cmd VARCHAR(500);

    -- Construction de la commande
    SET v_cmd = CONCAT("/usr/sbin/medulla_mysql_exec_update.sh ", NEW.updateid, " c");

    -- Ajout action
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` (`action`, `packages`, `option`)
    VALUES (v_cmd, NEW.updateid, "-c");

    -- Log
    SET v_logtext = CONCAT("Creation command : ", v_cmd);
    INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`,
                                     `sessionname`, `how`, `why`, `priority`, `who`)
    VALUES ('automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_INSERT', 'medulla',
            'creation', NEW.updateid, 'auto', 'mariadb', '-1', 'system');

    -- Recuperation des metadonnees update
    SELECT msrcseverity, updateclassification
    INTO v_msrcseverity, v_updateclassification
    FROM xmppmaster.update_data
    WHERE updateid = NEW.updateid
    LIMIT 1;

    -- Verification auto-approve rules pour l'entite
    SELECT COUNT(*)
    INTO v_exists_rule
    FROM xmppmaster.up_auto_approve_rules
    WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
      AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
      AND active_rule = 1
      AND entityid = NEW.entityid;

    -- Si regle trouvee -> ajout a pending_events AVEC entityid (correctif schema-107)
    IF v_exists_rule > 0 THEN
        INSERT IGNORE INTO xmppmaster.pending_events (
            updateid,
            entityid,
            kb,
            title,
            description,
            title_short,
            valided
        )
        VALUES (
            NEW.updateid,
            NEW.entityid,
            NEW.kb,
            NEW.title,
            NEW.description,
            NEW.title_short,
            NEW.valided
        );
    END IF;
END$$
DELIMITER ;

-- 2c. Correctif de la procedure up_event_move_to_white_list
--     Lecture et propagation de entityid depuis pending_events
DROP PROCEDURE IF EXISTS xmppmaster.up_event_move_to_white_list;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE xmppmaster.up_event_move_to_white_list()
BEGIN
    -- =====================================================================
    -- Procedure : xmppmaster.up_event_move_to_white_list
    -- Description :
    --   Traite les mises a jour en attente dans `pending_events` et les
    --   transfere vers `up_white_list`.
    --
    --   Pour chaque entree dans `pending_events` :
    --     1. Insert dans `up_white_list` avec entityid (INSERT IGNORE).
    --     2. Delete dans `up_gray_list` filtre par updateid ET entityid.
    --     3. Delete dans `pending_events` filtre par updateid ET entityid.
    --
    -- Correctif schema-107 :
    --   - entityid est maintenant lu depuis le curseur.
    --   - entityid est propage dans l'INSERT vers up_white_list.
    --   - Les DELETE sont filtres par (updateid, entityid) pour eviter
    --     de supprimer des entrees d'autres entites portant le meme updateid.
    -- =====================================================================

    DECLARE done INT DEFAULT 0;
    DECLARE v_updateid VARCHAR(255);
    DECLARE v_entityid INT;
    DECLARE v_kb VARCHAR(255);
    DECLARE v_title VARCHAR(255);
    DECLARE v_description TEXT;
    DECLARE v_title_short VARCHAR(255);
    DECLARE v_valided INT;

    DECLARE cur CURSOR FOR
        SELECT updateid, entityid, kb, title, description, title_short, valided
        FROM xmppmaster.pending_events;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_updateid, v_entityid, v_kb, v_title, v_description, v_title_short, v_valided;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Transfert vers la liste blanche avec entityid
        INSERT IGNORE INTO xmppmaster.up_white_list (
            updateid,
            entityid,
            kb,
            title,
            description,
            title_short,
            valided
        ) VALUES (
            v_updateid,
            v_entityid,
            v_kb,
            v_title,
            v_description,
            v_title_short,
            v_valided
        );

        -- Suppression ciblee dans up_gray_list (filtrage par entite)
        DELETE FROM xmppmaster.up_gray_list
        WHERE updateid = v_updateid
          AND entityid = v_entityid;

        -- Consommation de pending_events (filtrage par entite)
        DELETE FROM xmppmaster.pending_events
        WHERE updateid = v_updateid
          AND entityid = v_entityid;

    END LOOP;

    CLOSE cur;
END$$
DELIMITER ;

-- =====================================================================
-- 3. Correctif : PK composite (updateid, entityid) sur les tables
--    up_white_list, up_gray_list et up_gray_list_flop
-- =====================================================================
-- Depuis schema-095, la colonne `entityid` a ete ajoutee a ces tables
-- avec un index UNIQUE (updateid, entityid), mais la PRIMARY KEY est
-- restee sur `updateid` seul (heritee de schema-073). Consequences :
--   * un meme updateid ne peut exister que pour UNE seule entite ;
--   * les INSERT IGNORE emis par les triggers
--     up_auto_approve_rules_AFTER_UPDATE, up_white_list_AFTER_INSERT et
--     par la procedure move_update_to_white_list sont silencieusement
--     ecrases pour toute entite supplementaire ;
--   * le trigger up_gray_list_AFTER_INSERT (schema-105) ne fire pas sur
--     un INSERT IGNORE ignore, donc pending_events n'est pas alimente et
--     up_gray_list n'est jamais nettoye. Les packages restent bloques
--     indefiniment (constate en production : 80 packages a cheval sur
--     3 entites).
--
-- Fix : remplacer la PK par une PK composite (updateid, entityid) et
-- supprimer l'index UNIQUE devenu redondant.
--
-- Pour debloquer les packages deja coinces APRES l'application du
-- schema, executer manuellement (snapshot + toggle des regles, non
-- destructif) :
--   CREATE TEMPORARY TABLE tmp_rules_snapshot AS
--     SELECT id FROM xmppmaster.up_auto_approve_rules WHERE active_rule = 1;
--   UPDATE xmppmaster.up_auto_approve_rules SET active_rule = 0
--     WHERE id IN (SELECT id FROM tmp_rules_snapshot);
--   UPDATE xmppmaster.up_auto_approve_rules SET active_rule = 1
--     WHERE id IN (SELECT id FROM tmp_rules_snapshot);
--   DROP TEMPORARY TABLE tmp_rules_snapshot;
-- =====================================================================

ALTER TABLE `xmppmaster`.`up_white_list`
    DROP PRIMARY KEY,
    ADD PRIMARY KEY (`updateid`, `entityid`);
ALTER TABLE `xmppmaster`.`up_white_list`
    DROP INDEX IF EXISTS `uniq_update_entity_white`;

ALTER TABLE `xmppmaster`.`up_gray_list`
    DROP PRIMARY KEY,
    ADD PRIMARY KEY (`updateid`, `entityid`);
ALTER TABLE `xmppmaster`.`up_gray_list`
    DROP INDEX IF EXISTS `uniq_update_entity`;

ALTER TABLE `xmppmaster`.`up_gray_list_flop`
    DROP PRIMARY KEY,
    ADD PRIMARY KEY (`updateid`, `entityid`);
ALTER TABLE `xmppmaster`.`up_gray_list_flop`
    DROP INDEX IF EXISTS `uniq_update_entity_flop`;

-- Trace applicative de la migration
INSERT INTO `xmppmaster`.`logs`
    (`type`, `module`, `text`, `fromuser`, `touser`, `action`,
     `sessionname`, `how`, `why`, `priority`, `who`)
VALUES
    ('automate_Maria', 'update',
     'schema-107: PK composite (updateid, entityid) posee sur up_white_list, up_gray_list et up_gray_list_flop -- fin du blocage silencieux multi-entite',
     'schema-107', 'medulla', 'migration',
     'schema-107', 'auto', 'mariadb', '-1', 'system');

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 107;

COMMIT;
