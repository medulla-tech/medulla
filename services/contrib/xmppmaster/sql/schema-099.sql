--
-- (c) 2025, http://www.medulla-tech.io/
--
--
-- This file is part of Pulse 2, http://www.medulla-tech.io/
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.
-- FILE contrib/xmppmaster/sql/schema-096.sql
-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;
USE `xmppmaster`;

-- =======================================
-- Procedure : up_search_kb_update
-- Author    : (ton nom)
-- Database  : xmppmaster
-- Created   : (date du jour)
--
-- Purpose   :
--   Recherche les mises à jour de sécurité (KB) manquantes dans une table
--   spécifique de packages selon la famille du produit (Windows, Office, Visual Studio…).
--   Génère dynamiquement une requête SQL adaptée au type de produit.
--
-- Parameters :
--   IN tablesearch VARCHAR(1024)
--       → Nom de la table produit à interroger (ex : 'up_packages_Win10_X64_22H2')
--   IN KB_LIST VARCHAR(2048)
--       → Liste de KBs (identifiants de correctifs) déjà connus, séparés par des virgules.
--
-- Behavior :
--   - Si KB_LIST est vide ou NULL → la procédure se termine immédiatement.
--   - Selon la table passée en argument :
--       • Windows (Win10, Win11, Server, MSOS) :
--            Recherche les dernières révisions non obsolètes (supersededby = '')
--            et dont les KB ne figurent pas dans KB_LIST.
--       • Office (2003–2016) :
--            Recherche les dernières mises à jour de sécurité uniquement.
--       • Visual Studio (2005–2022) :
--            Idem, limité aux "Security Updates".
--       • Win_Malicious_X64 :
--            Sélectionne le dernier correctif non présent dans KB_LIST.
--       • Autres tables :
--            Retourne le contenu complet de xmppmaster.update_data (fallback).
--
-- Output :
--   - Exécute dynamiquement un SELECT correspondant au produit demandé.
--   - Retourne le ou les enregistrements des mises à jour KB non encore présentes.
--
-- Notes :
--   - Utilise SQL dynamique (PREPARE / EXECUTE) pour exécuter la requête construite.
--   - Les sous-requêtes "max(revisionid)" permettent d’obtenir uniquement
--     les révisions les plus récentes par famille de patch.
--   - Si une table n’est pas reconnue dans les listes prévues, la procédure
--     renvoie par défaut le contenu de xmppmaster.update_data.
--
-- Example usage :
--   CALL up_search_kb_update('up_packages_Win10_X64_22H2', 'KB5030219,KB5030300');
--
-- Expected result :
--   → Retourne toutes les mises à jour KB non présentes dans la liste donnée.
-- =======================================

USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_search_kb_update`;
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_search_kb_update`;

DELIMITER $$

CREATE PROCEDURE `up_search_kb_update`(
    IN tablesearch VARCHAR(1024),
    IN KB_LIST VARCHAR(2048)
)
BEGIN
    DECLARE result VARCHAR(50);

    -- Vérifier si KB_LIST est vide
    end_procedure:
    BEGIN
        IF KB_LIST IS NULL OR KB_LIST = '' THEN
            LEAVE end_procedure;
        END IF;

        CASE
            WHEN tablesearch IN (
                'up_packages_Win10_X64_1903',
                'up_packages_Win10_X64_21H1',
                'up_packages_Win10_X64_21H2',
                'up_packages_Win10_X64_22H2',
                'up_packages_Win11_X64',
                'up_packages_Win11_X64_21H2',
                'up_packages_Win11_X64_22H2',
                'up_packages_Win11_X64_23H2',
                'up_packages_Win11_X64_24H2',
                'up_packages_Win11_X64_25H2',                
                'up_packages_Win11_X64_26H2',
                'up_packages_MSOS_ARM64_24H2',
                'up_packages_MSOS_X64_21H2',
                'up_packages_MSOS_X64_22H2',
                'up_packages_MSOS_X64_23H2',
                'up_packages_MSOS_X64_24H2',
                'up_packages_WS_X64_2003',
                'up_packages_WS_X64_2008',
                'up_packages_WS_X64_2012',
                'up_packages_WS_X64_2016',
                'up_packages_WS_X64_2019'
            ) THEN
                SET @query = CONCAT(
                    "SELECT * FROM ", tablesearch, " vv
                     WHERE revisionid IN (
                        SELECT MAX(revisionid)
                        FROM ", tablesearch, "
                        WHERE supersededby = ''
                        GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 9)
                     )
                     AND vv.KB NOT IN (", KB_LIST, ");"
                );

            WHEN tablesearch IN (
                'up_packages_office_2003_64bit',
                'up_packages_office_2007_64bit',
                'up_packages_office_2010_64bit',
                'up_packages_office_2013_64bit',
                'up_packages_office_2016_64bit'
            ) THEN
                SET @query = CONCAT(
                    "SELECT * FROM ", tablesearch, " vv
                     WHERE revisionid IN (
                        SELECT MAX(revisionid)
                        FROM ", tablesearch, "
                        WHERE supersededby = ''
                        AND updateclassification LIKE 'Security Updates'
                        GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 31)
                     )
                     AND vv.KB NOT IN (", KB_LIST, ");"
                );

            WHEN tablesearch IN (
                'up_packages_Vstudio_2005',
                'up_packages_Vstudio_2008',
                'up_packages_Vstudio_2010',
                'up_packages_Vstudio_2012',
                'up_packages_Vstudio_2013',
                'up_packages_Vstudio_2015',
                'up_packages_Vstudio_2017',
                'up_packages_Vstudio_2019',
                'up_packages_Vstudio_2022'
            ) THEN
                SET @query = CONCAT(
                    "SELECT * FROM ", tablesearch, " vv
                     WHERE revisionid IN (
                        SELECT MAX(revisionid)
                        FROM ", tablesearch, "
                        WHERE supersededby = ''
                        AND updateclassification LIKE 'Security Updates'
                        GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 38)
                     )
                     AND vv.KB NOT IN (", KB_LIST, ");"
                );

            WHEN tablesearch = 'up_packages_Win_Malicious_X64' THEN
                SET @query = CONCAT(
                    "SELECT * FROM xmppmaster.up_packages_Win_Malicious_X64
                     WHERE KB NOT IN (", KB_LIST, ")
                     ORDER BY revisionid DESC
                     LIMIT 1;"
                );
        END CASE;

        PREPARE stmt FROM @query;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END;
END$$

DELIMITER ;

CREATE TABLE IF NOT EXISTS up_windows_kb_uninstall (
    id INT AUTO_INCREMENT,

    -- Identifiant unique de la mise a jour Windows
    updateid VARCHAR(38) NOT NULL,

    -- Nom de la machine concernée
    hostname VARCHAR(45) NOT NULL,

    -- Numéro de la KB (ex: KB1234567)
    kb VARCHAR(45) DEFAULT '',

    -- Identifiant du job (ex: GLPI, Ansible, etc.)
    jid VARCHAR(255),

    -- ID de l'entité (ex: GLPI entities_id)
    entities_id INT DEFAULT 0,

    -- Nombre de tentatives de désinstallation
    count_uninstall INT DEFAULT 0,

    -- Statut de la désinstallation (ex: "FAILED", "SUCCESS", "PENDING")
    status VARCHAR(255),

    -- Clé primaire simple
    PRIMARY KEY (id),

    -- Clé unique métier (pour éviter les doublons updateid+hostname)
    UNIQUE KEY uniq_update_host (updateid, hostname),

    -- Index pour optimiser les requêtes sur updateid et jid
    INDEX idx_updateid (updateid),
    INDEX idx_jid (jid)
)
COMMENT='Cette table permet de suivre les tentatives de desinstallation de mises a jour Windows (KB) sur les machines.
Pour une machine donnee, une desinstallation peut echouer pour plusieurs raisons :
- SSU : Mise a jour systeme critique (Servicing Stack), non desinstallable.
- CUMULATIVE : Mise a jour cumulative, incluse dans une version plus recente.
- GPO : Desinstallation bloquee par strategie de groupe.
- WSUS : Desinstallation bloquee par gestion centralisee des mises a jour.
- CBS_ERROR : echec technique lors de la desinstallation (erreur systeme).
- ISO : Mise a jour integree via image ISO/upgrade systeme, non desinstallable individuellement.';


DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_AFTER_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `xmppmaster`.`up_black_list_AFTER_UPDATE` AFTER UPDATE ON `up_black_list` FOR EACH ROW
BEGIN


    DELETE FROM `xmppmaster`.`up_gray_list`
    WHERE entityid = NEW.entityid
      AND `updateid` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'id'
      );
    
UPDATE `xmppmaster`.`up_gray_list_flop` 
SET 
    `updateid` = LEFT(UUID(), 8),
    `kb` = 'bidon'
WHERE
    entityid = NEW.entityid
        AND `updateid` IN (SELECT 
            updateid_or_kb
        FROM
            xmppmaster.up_black_list
        WHERE
            entityid = NEW.entityid
                AND userjid_regexp = '.*'
                AND type_rule = 'id');

    
DELETE FROM `xmppmaster`.`up_gray_list` 
WHERE
    entityid = NEW.entityid
    AND `kb` IN (SELECT 
        updateid_or_kb
    FROM
        xmppmaster.up_black_list
    
    WHERE
        entityid = NEW.entityid
        AND userjid_regexp = '.*'
        AND type_rule = 'kb');
    
UPDATE `xmppmaster`.`up_gray_list_flop` 
SET 
    `kb` = 'bidon'
WHERE
    entityid = NEW.entityid
        AND `updateid` IN (SELECT 
            updateid_or_kb
        FROM
            xmppmaster.up_black_list
        WHERE
            entityid = NEW.entityid
                AND userjid_regexp = '.*'
                AND type_rule = 'kb');
    
DELETE FROM `xmppmaster`.`up_gray_list_flop` 
WHERE
    entityid = NEW.entityid
    AND (`kb` = 'bidon');
      
	DELETE u FROM xmppmaster.up_windows_kb_uninstall u 
WHERE
    u.entities_id = NEW.entityid
    AND NOT EXISTS( SELECT 
        1
    FROM
        xmppmaster.up_black_list b    
    WHERE
        b.entityid = u.entities_id
        AND b.enable_rule = 1
        AND b.updateid_or_kb = u.updateid
        AND b.type_rule = 'id'
        AND u.jid REGEXP b.userjid_regexp);

END$$
DELIMITER ;


DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `xmppmaster`.`up_black_list_AFTER_INSERT` AFTER INSERT ON `up_black_list` FOR EACH ROW
BEGIN

    DELETE FROM `xmppmaster`.`up_gray_list`
    WHERE entityid = NEW.entityid
      AND `updateid` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'id'
      );
UPDATE `xmppmaster`.`up_gray_list_flop` 
SET 
    `updateid` = LEFT(UUID(), 8),
    `kb` = 'bidon'
WHERE
    entityid = NEW.entityid
        AND `updateid` IN (SELECT 
            updateid_or_kb
        FROM
            xmppmaster.up_black_list
        WHERE
            entityid = NEW.entityid
                AND userjid_regexp = '.*'
                AND type_rule = 'id');
DELETE FROM `xmppmaster`.`up_gray_list` 
WHERE
    entityid = NEW.entityid
    AND `kb` IN (SELECT 
        updateid_or_kb
    FROM
        xmppmaster.up_black_list
    
    WHERE
        entityid = NEW.entityid
        AND userjid_regexp = '.*'
        AND type_rule = 'kb');
UPDATE `xmppmaster`.`up_gray_list_flop` 
SET 
    `kb` = 'bidon'
WHERE
    entityid = NEW.entityid
        AND `updateid` IN (SELECT 
            updateid_or_kb
        FROM
            xmppmaster.up_black_list
        WHERE
            entityid = NEW.entityid
                AND userjid_regexp = '.*'
                AND type_rule = 'kb');
DELETE FROM `xmppmaster`.`up_white_list` 
WHERE
    entityid = NEW.entityid
    AND (`updateid` = NEW.updateid_or_kb
    OR `kb` = NEW.updateid_or_kb);
DELETE FROM `xmppmaster`.`up_gray_list_flop` 
WHERE
    entityid = NEW.entityid
    AND (`kb` = 'bidon');


DELETE u FROM xmppmaster.up_windows_kb_uninstall u 
WHERE
    u.entities_id = NEW.entityid
    AND NOT EXISTS( SELECT 
        1
    FROM
        xmppmaster.up_black_list b
    
    WHERE
        b.entityid = u.entities_id
        AND b.enable_rule = 1
        AND b.updateid_or_kb = u.updateid
        AND b.type_rule = 'id'
        AND u.jid REGEXP b.userjid_regexp);
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 99;


commit;
