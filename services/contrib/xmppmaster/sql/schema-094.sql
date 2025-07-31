--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
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


--  ============================================================================
-- Ce script SQL est conçu pour automatiser le processus de passage des mises à jour logicielles
-- d'une "liste grise" vers une "liste blanche"
-- en fonction de règles d'auto-approbation prédéfinies.
--  ============================================================================
START TRANSACTION;

USE `xmppmaster`;


--
-- Table structure for table `pending_events`
--
DROP TABLE IF EXISTS xmppmaster.pending_events;
CREATE TABLE xmppmaster.pending_events
   LIKE
   xmppmaster.up_white_list;

--  ============================================================================
--  Trigger : xmppmaster.up_gray_list_AFTER_INSERT
--  ----------------------------------------------------------------------------

DROP TRIGGER IF EXISTS xmppmaster.up_gray_list_AFTER_INSERT;

DELIMITER //

CREATE TRIGGER `xmppmaster`.`up_gray_list_AFTER_INSERT`
AFTER INSERT ON xmppmaster.`up_gray_list`
FOR EACH ROW
BEGIN
    /*
    ============================================================================
    Trigger : xmppmaster.up_gray_list_AFTER_INSERT
    ----------------------------------------------------------------------------
    Objectif :
        Lorsqu'une mise à jour est insérée dans la table `up_gray_list`, ce trigger :

        1. Génère une commande de traitement (`medulla_mysql_exec_update.sh`).
        2. Insère cette commande dans `up_action_update_packages` (actions planifiées).
        3. Journalise la création de la commande dans la table `logs`.
        4. Récupère les métadonnées (sévérité et classification) associées à la mise à jour.
        5. Vérifie si une règle d’auto-approbation est active dans `up_auto_approve_rules`.
        6. Si une règle est trouvée :
            - Insère l’entrée dans `pending_events` (en attente d’approbation auto).
            - Sans duplication grâce à `INSERT IGNORE`.

    Remarques :
        - Le traitement vers la liste blanche sera déclenché plus tard par une procédure
          séparée (`up_event_move_to_white_list` ou équivalent).
        - Ce mécanisme permet de différer l’approbation automatique de manière centralisée.
    ============================================================================
    */

    DECLARE v_msrcseverity VARCHAR(255);
    DECLARE v_updateclassification VARCHAR(255);
    DECLARE v_exists_rule INT DEFAULT 0;
    DECLARE v_logtext VARCHAR(500);
    DECLARE v_cmd VARCHAR(500); -- Declare the v_cmd variable

    -- Étape 1 : Générer la commande de traitement
    SET v_cmd = CONCAT("/usr/sbin/medulla_mysql_exec_update.sh ", NEW.updateid, " c");

    -- Étape 2 : Insérer la commande dans la table des actions planifiées
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` (`action`, `packages`, `option`)
    VALUES (v_cmd, NEW.updateid, "-c");

    -- Étape 3 : Journaliser la création de la commande
    SET v_logtext = CONCAT("Creation command : ", v_cmd);
    INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`,
                                     `sessionname`, `how`, `why`, `priority`, `who`)
    VALUES ('automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_INSERT', 'medulla',
            'creation', NEW.updateid, 'auto', 'mariadb', '-1', 'system');

    -- Récupération de la sévérité et classification depuis update_data
    SELECT msrcseverity, updateclassification
    INTO v_msrcseverity, v_updateclassification
    FROM xmppmaster.update_data
    WHERE updateid = NEW.updateid
    LIMIT 1;

    -- Vérification d'une règle active d’auto-approbation
    SELECT COUNT(*)
    INTO v_exists_rule
    FROM xmppmaster.up_auto_approve_rules
    WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
      AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
      AND active_rule = 1;

    -- Si règle trouvée, insertion IGNORE dans pending_events
    IF v_exists_rule > 0 THEN
        INSERT IGNORE INTO xmppmaster.pending_events (updateid,
                                                      kb,
                                                      title,
                                                      description,
                                                      title_short,
                                                      valided)
        VALUES (NEW.updateid,
                NEW.kb,
                NEW.title,
                NEW.description,
                NEW.title_short,
                NEW.valided );
    END IF;
END;
//

DELIMITER ;

--    ============================================================================
--    Procédure : xmppmaster.up_event_move_to_white_list
--    ----------------------------------------------------------------------------


DROP PROCEDURE IF EXISTS xmppmaster.up_event_move_to_white_list;
DELIMITER //

CREATE PROCEDURE xmppmaster.up_event_move_to_white_list()
BEGIN
    /*
    ============================================================================
    Procédure : xmppmaster.up_event_move_to_white_list
    ----------------------------------------------------------------------------
    Objectif :
        Cette procédure traite les mises à jour en attente dans la table
        `pending_events`, identifiées comme éligibles à une approbation
        automatique selon les règles définies.

        Pour chaque entrée dans `pending_events` :
            1. Elle insère la mise à jour dans `up_white_list` (liste blanche),
               en évitant les doublons via `INSERT IGNORE`.
            2. Elle supprime la mise à jour correspondante de `up_gray_list`.
            3. Elle supprime l'entrée de `pending_events` (consommation).

    Fonctionnement :
        - Utilise un curseur pour parcourir toutes les entrées de `pending_events`.
        - La variable `done` permet de sortir proprement de la boucle.
        - Cette procédure est conçue pour être appelée manuellement ou via un trigger.

    Remarque :
        - La logique d'approbation automatique (basée sur la sévérité et classification)
          est effectuée en amont, avant le remplissage de `pending_events`.
    Sécurité :
        - Aucun rollback n’est prévu : chaque ligne est traitée immédiatement.
        - Aucune gestion d’erreur autre que le `NOT FOUND` du curseur.
    ============================================================================
    */

    DECLARE done INT DEFAULT 0;
    DECLARE v_updateid VARCHAR(255);
    DECLARE v_kb VARCHAR(255);
    DECLARE v_title VARCHAR(255);
    DECLARE v_description TEXT;
    DECLARE v_title_short VARCHAR(255);
    DECLARE v_valided INT;

    DECLARE cur CURSOR FOR
        SELECT updateid, kb, title, description, title_short, valided
        FROM xmppmaster.pending_events;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_updateid, v_kb, v_title, v_description, v_title_short, v_valided;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Insert into white list (avoid duplicates)
        INSERT IGNORE INTO xmppmaster.up_white_list (
            updateid, kb, title, description, title_short, valided
        )
        VALUES (
            v_updateid, v_kb, v_title, v_description, v_title_short, v_valided
        );

        -- Delete processed data
        DELETE FROM xmppmaster.up_gray_list WHERE updateid = v_updateid;
        DELETE FROM xmppmaster.pending_events WHERE updateid = v_updateid;
    END LOOP;

    CLOSE cur;
END //

DELIMITER ;

-- ============================================================================
-- Procédure : xmppmaster.move_update_to_white_list
-- ----------------------------------------------------------------------------

DROP PROCEDURE IF EXISTS xmppmaster.move_update_to_white_list;
DELIMITER //

CREATE PROCEDURE xmppmaster.move_update_to_white_list()
BEGIN
    -- ============================================================================
    -- Procédure : xmppmaster.move_update_to_white_list
    -- ----------------------------------------------------------------------------
    -- Objectif :
    --     Parcourir toutes les entrées de la table `up_gray_list` et, si une
    --     règle d'auto-approbation est active (dans `up_auto_approve_rules`)
    --     correspondant à la sévérité et à la classification de la mise à jour :
    --         - Insérer l’entrée dans `up_white_list` (si non déjà présente)
    --
    -- Fonctionnement :
    --     - Récupère `msrcseverity` et `updateclassification` depuis `update_data`
    --     - Vérifie s’il existe une règle active correspondante
    --     - Insère dans `up_white_list` si règle active
    --
    -- Remarques :
    --     - Les `NULL` dans les règles servent de jokers (match any)
    --     - La suppression de la mise à jour dans `up_gray_list` est assurée
    --       automatiquement par un **trigger associé à la table `up_white_list`**
    -- ============================================================================

    DECLARE done INT DEFAULT 0;

    DECLARE v_updateid VARCHAR(255);
    DECLARE v_kb VARCHAR(255);
    DECLARE v_title VARCHAR(255);
    DECLARE v_description TEXT;
    DECLARE v_title_short VARCHAR(255);
    DECLARE v_valided INT;

    DECLARE v_msrcseverity VARCHAR(255);
    DECLARE v_updateclassification VARCHAR(255);
    DECLARE v_exists_rule INT;

    DECLARE cur CURSOR FOR
        SELECT updateid, kb, title, description, title_short, valided
        FROM xmppmaster.up_gray_list;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_updateid, v_kb, v_title, v_description, v_title_short, v_valided;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Récupérer la sévérité et la classification de la mise à jour
        SELECT msrcseverity, updateclassification
        INTO v_msrcseverity, v_updateclassification
        FROM xmppmaster.update_data
        WHERE updateid = v_updateid
        LIMIT 1;

        -- Vérifier s’il existe une règle active qui correspond
        SELECT COUNT(*) INTO v_exists_rule
        FROM xmppmaster.up_auto_approve_rules
        WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
          AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
          AND active_rule = 1;

        -- Si une règle active correspond, insérer en liste blanche
        IF v_exists_rule > 0 THEN
            INSERT IGNORE INTO xmppmaster.up_white_list (
                updateid, kb, title, description, title_short, valided
            ) VALUES (
                v_updateid, v_kb, v_title, v_description, v_title_short, v_valided
            );
        END IF;

    END LOOP;

    CLOSE cur;
END;
//
DELIMITER ;


--    ============================================================================
--    Table structure for table `up_auto_approve_rules`
--    ----------------------------------------------------------------------------


DROP TABLE IF EXISTS `up_auto_approve_rules`;
CREATE TABLE `up_auto_approve_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `msrcseverity` varchar(45) DEFAULT NULL COMMENT 'Exemples : Critical, Important, Moderate, Low. Peut être NULL pour matcher toute sévérité.',
  `updateclassification` varchar(45) DEFAULT NULL COMMENT 'Exemples : Security Updates, Critical Updates, Update Rollups, Service Packs. Peut être NULL pour matcher toute classification.',
  `active_rule` int(11) DEFAULT 0 COMMENT '0 = inactif, 1 = actif. Si actif, la règle est utilisée pour valider automatiquement une mise à jour.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `rule_unique` (`msrcseverity`,`updateclassification`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Définit les règles d’auto-approbation des mises à jour en fonction de leur criticité et classification.';

--
-- Dumping data for table `up_auto_approve_rules`
--

LOCK TABLES `up_auto_approve_rules` WRITE;

INSERT INTO `up_auto_approve_rules` VALUES
(1,'Critical','Security Updates',0),
(2,'Important','Security Updates',0),
(3,'Moderate','Security Updates',0),
(4,'Low','Security Updates',0),
(5,NULL,'Update Rollups',0),
(6,NULL,'Service Packs',0),
(7,NULL,'Security Updates',0),
(8,NULL,'Critical Updates',0),
(9,NULL,'Updates',0);

UNLOCK TABLES;

--    ============================================================================
--    Trigger : xmppmaster.up_auto_approve_rules_AFTER_UPDATE
--    ----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_auto_approve_rules_AFTER_UPDATE`;

DELIMITER $$

CREATE TRIGGER `xmppmaster`.`up_auto_approve_rules_AFTER_UPDATE`
AFTER UPDATE ON `up_auto_approve_rules`
FOR EACH ROW
BEGIN
    /*
      ============================================================================
      Trigger : xmppmaster.up_auto_approve_rules_AFTER_UPDATE
      ----------------------------------------------------------------------------
      Objectif :
        - À chaque modification d'une règle d'auto-approbation :
            → Appeler la procédure stockée `move_update_to_white_list`
              pour appliquer les règles modifiées aux entrées existantes.
    */

    CALL xmppmaster.move_update_to_white_list();

END$$

DELIMITER ;


DROP EVENT IF EXISTS xmppmaster.ev_process_pending_events;
-- Créer l’événement
CREATE EVENT IF NOT EXISTS xmppmaster.ev_process_pending_events
ON SCHEDULE EVERY 1 MINUTE
DO
    CALL xmppmaster.up_event_move_to_white_list();



-- ============================================================================
-- Procédure : xmppmaster.up_windows_malicious_software_tool
-- ----------------------------------------------------------------------------


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_windows_malicious_software_tool`;
;

DELIMITER $$

/*
  Procédure : up_windows_malicious_software_tool

  Description :
    Recherche une mise à jour "Windows Malicious Software Removal Tool" dans la table `update_data`.
    Si une mise à jour avec un titre correspondant à l'architecture et la version spécifiée existe,
    la procédure termine silencieusement.
    Sinon, elle retourne la mise à jour la plus récente non remplacée correspondant au produit et à l'architecture.

  Paramètres :
    - PRODUCTtable (VARCHAR(80)) : Chaîne à rechercher dans le champ `product`. Si vide ou NULL, valeur par défaut = "%Windows%".
    - ARCHItable (VARCHAR(20))   : Chaîne à rechercher dans le champ `title` pour l'architecture. Si vide ou NULL, valeur par défaut = "%x64%".
    - major (VARCHAR(10))        : Numéro de version majeure. Si vide ou NULL, valeur par défaut = '0'.
    - minor (VARCHAR(10))        : Numéro de version mineure. Si vide ou NULL, valeur par défaut = '0'.
*/


CREATE PROCEDURE `up_windows_malicious_software_tool`(
    IN PRODUCTtable VARCHAR(80),
    IN ARCHItable VARCHAR(20),
    IN major VARCHAR(10),
    IN minor VARCHAR(10)
)
proc_Exit: BEGIN
    DECLARE produc_windows VARCHAR(80) DEFAULT '%Windows%';
    DECLARE archi VARCHAR(20) DEFAULT '%x64%';
    DECLARE title_search VARCHAR(200);

    -- Si les paramètres ne sont pas vides ou NULL, les utiliser
    IF PRODUCTtable IS NOT NULL AND PRODUCTtable != '' THEN
        SET produc_windows = CONCAT('%', PRODUCTtable, '%');
    END IF;

    IF ARCHItable IS NOT NULL AND ARCHItable != '' THEN
        SET archi = CONCAT('%', ARCHItable, '%');
    END IF;

    IF major IS NULL OR major = '' THEN
        SET major = '0';
    END IF;

    IF minor IS NULL OR minor = '' THEN
        SET minor = '0';
    END IF;

    SET title_search = CONCAT('Windows Malicious Software Removal Tool ', ARCHItable, ' - v', major, '.', minor, '%');

    -- Vérifie s'il existe au moins une ligne correspondant à la recherche
    IF EXISTS (
        SELECT 1
        FROM xmppmaster.update_data
        WHERE title LIKE title_search
        AND product LIKE produc_windows
    ) THEN
        LEAVE proc_Exit;
    ELSE
        -- Sinon, retourne une ligne alternative
        SELECT *
        FROM xmppmaster.update_data
        WHERE title LIKE '%Windows Malicious Software Removal Tool%'
        AND title LIKE archi
        AND product LIKE produc_windows
        AND supersededby = ''
        ORDER BY revisionid DESC
        LIMIT 1;
    END IF;
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 94;

COMMIT;
