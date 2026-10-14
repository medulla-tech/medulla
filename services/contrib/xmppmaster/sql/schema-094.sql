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
-- Ce script SQL est conçu pour automatiser le processus de passage des mises a jour logicielles
-- d'une "liste grise" vers une "liste blanche"
-- en fonction de regles d'auto-approbation predefinies.
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
        Lorsqu'une mise a jour est inseree dans la table `up_gray_list`, ce trigger :

        1. Genere une commande de traitement (`medulla_mysql_exec_update.sh`).
        2. Insere cette commande dans `up_action_update_packages` (actions planifiees).
        3. Journalise la creation de la commande dans la table `logs`.
        4. Recupere les metadonnees (severite et classification) associees a la mise a jour.
        5. Verifie si une regle d’auto-approbation est active dans `up_auto_approve_rules`.
        6. Si une regle est trouvee :
            - Insere l’entree dans `pending_events` (en attente d’approbation auto).
            - Sans duplication grâce a `INSERT IGNORE`.

    Remarques :
        - Le traitement vers la liste blanche sera declenche plus tard par une procedure
          separee (`up_event_move_to_white_list` ou equivalent).
        - Ce mecanisme permet de differer l’approbation automatique de maniere centralisee.
    ============================================================================
    */

    DECLARE v_msrcseverity VARCHAR(255);
    DECLARE v_updateclassification VARCHAR(255);
    DECLARE v_exists_rule INT DEFAULT 0;
    DECLARE v_logtext VARCHAR(500);
    DECLARE v_cmd VARCHAR(500); -- Declare the v_cmd variable

    -- etape 1 : Generer la commande de traitement
    SET v_cmd = CONCAT("/usr/sbin/medulla_mysql_exec_update.sh ", NEW.updateid, " c");

    -- etape 2 : Inserer la commande dans la table des actions planifiees
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` (`action`, `packages`, `option`)
    VALUES (v_cmd, NEW.updateid, "-c");

    -- etape 3 : Journaliser la creation de la commande
    SET v_logtext = CONCAT("Creation command : ", v_cmd);
    INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`,
                                     `sessionname`, `how`, `why`, `priority`, `who`)
    VALUES ('automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_INSERT', 'medulla',
            'creation', NEW.updateid, 'auto', 'mariadb', '-1', 'system');

    -- Recuperation de la severite et classification depuis update_data
    SELECT msrcseverity, updateclassification
    INTO v_msrcseverity, v_updateclassification
    FROM xmppmaster.update_data
    WHERE updateid = NEW.updateid
    LIMIT 1;

    -- Verification d'une regle active d’auto-approbation
    SELECT COUNT(*)
    INTO v_exists_rule
    FROM xmppmaster.up_auto_approve_rules
    WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
      AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
      AND active_rule = 1;

    -- Si regle trouvee, insertion IGNORE dans pending_events
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
--    Procedure : xmppmaster.up_event_move_to_white_list
--    ----------------------------------------------------------------------------


DROP PROCEDURE IF EXISTS xmppmaster.up_event_move_to_white_list;
DELIMITER //

CREATE PROCEDURE xmppmaster.up_event_move_to_white_list()
BEGIN
    /*
    ============================================================================
    Procedure : xmppmaster.up_event_move_to_white_list
    ----------------------------------------------------------------------------
    Objectif :
        Cette procedure traite les mises a jour en attente dans la table
        `pending_events`, identifiees comme eligibles a une approbation
        automatique selon les regles definies.

        Pour chaque entree dans `pending_events` :
            1. Elle insere la mise a jour dans `up_white_list` (liste blanche),
               en evitant les doublons via `INSERT IGNORE`.
            2. Elle supprime la mise a jour correspondante de `up_gray_list`.
            3. Elle supprime l'entree de `pending_events` (consommation).

    Fonctionnement :
        - Utilise un curseur pour parcourir toutes les entrees de `pending_events`.
        - La variable `done` permet de sortir proprement de la boucle.
        - Cette procedure est conçue pour être appelee manuellement ou via un trigger.

    Remarque :
        - La logique d'approbation automatique (basee sur la severite et classification)
          est effectuee en amont, avant le remplissage de `pending_events`.
    Securite :
        - Aucun rollback n’est prevu : chaque ligne est traitee immediatement.
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
-- Procedure : xmppmaster.move_update_to_white_list
-- ----------------------------------------------------------------------------

DROP PROCEDURE IF EXISTS xmppmaster.move_update_to_white_list;
DELIMITER //

CREATE PROCEDURE xmppmaster.move_update_to_white_list()
BEGIN
    -- ============================================================================
    -- Procedure : xmppmaster.move_update_to_white_list
    -- ----------------------------------------------------------------------------
    -- Objectif :
    --     Parcourir toutes les entrees de la table `up_gray_list` et, si une
    --     regle d'auto-approbation est active (dans `up_auto_approve_rules`)
    --     correspondant a la severite et a la classification de la mise a jour :
    --         - Inserer l’entree dans `up_white_list` (si non deja presente)
    --
    -- Fonctionnement :
    --     - Recupere `msrcseverity` et `updateclassification` depuis `update_data`
    --     - Verifie s’il existe une regle active correspondante
    --     - Insere dans `up_white_list` si regle active
    --
    -- Remarques :
    --     - Les `NULL` dans les regles servent de jokers (match any)
    --     - La suppression de la mise a jour dans `up_gray_list` est assuree
    --       automatiquement par un **trigger associe a la table `up_white_list`**
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

        -- Recuperer la severite et la classification de la mise a jour
        SELECT msrcseverity, updateclassification
        INTO v_msrcseverity, v_updateclassification
        FROM xmppmaster.update_data
        WHERE updateid = v_updateid
        LIMIT 1;

        -- Verifier s’il existe une regle active qui correspond
        SELECT COUNT(*) INTO v_exists_rule
        FROM xmppmaster.up_auto_approve_rules
        WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
          AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
          AND active_rule = 1;

        -- Si une regle active correspond, inserer en liste blanche
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
  `msrcseverity` varchar(45) DEFAULT NULL COMMENT 'Exemples : Critical, Important, Moderate, Low. Peut être NULL pour matcher toute severite.',
  `updateclassification` varchar(45) DEFAULT NULL COMMENT 'Exemples : Security Updates, Critical Updates, Update Rollups, Service Packs. Peut être NULL pour matcher toute classification.',
  `active_rule` int(11) DEFAULT 0 COMMENT '0 = inactif, 1 = actif. Si actif, la regle est utilisee pour valider automatiquement une mise a jour.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `rule_unique` (`msrcseverity`,`updateclassification`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Definit les regles d’auto-approbation des mises a jour en fonction de leur criticite et classification.';

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
        - a chaque modification d'une regle d'auto-approbation :
            → Appeler la procedure stockee `move_update_to_white_list`
              pour appliquer les regles modifiees aux entrees existantes.
    */

    CALL xmppmaster.move_update_to_white_list();

END$$

DELIMITER ;


DROP EVENT IF EXISTS xmppmaster.ev_process_pending_events;
-- Creer l’evenement
CREATE EVENT IF NOT EXISTS xmppmaster.ev_process_pending_events
ON SCHEDULE EVERY 1 MINUTE
DO
    CALL xmppmaster.up_event_move_to_white_list();



-- ============================================================================
-- Procedure : xmppmaster.up_windows_malicious_software_tool
-- ----------------------------------------------------------------------------


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_windows_malicious_software_tool`;
;

DELIMITER $$

/*
  Procedure : up_windows_malicious_software_tool

  Description :
    Recherche une mise a jour "Windows Malicious Software Removal Tool" dans la table `update_data`.
    Si une mise a jour avec un titre correspondant a l'architecture et la version specifiee existe,
    la procedure termine silencieusement.
    Sinon, elle retourne la mise a jour la plus recente non remplacee correspondant au produit et a l'architecture.

  Parametres :
    - PRODUCTtable (VARCHAR(80)) : Chaîne a rechercher dans le champ `product`. Si vide ou NULL, valeur par defaut = "%Windows%".
    - ARCHItable (VARCHAR(20))   : Chaîne a rechercher dans le champ `title` pour l'architecture. Si vide ou NULL, valeur par defaut = "%x64%".
    - major (VARCHAR(10))        : Numero de version majeure. Si vide ou NULL, valeur par defaut = '0'.
    - minor (VARCHAR(10))        : Numero de version mineure. Si vide ou NULL, valeur par defaut = '0'.
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

    -- Si les parametres ne sont pas vides ou NULL, les utiliser
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

    -- Verifie s'il existe au moins une ligne correspondant a la recherche
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
