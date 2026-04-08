--
-- (c) 2026, http://www.medulla-tech.io/
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
-- FILE contrib/xmppmaster/sql/schema-100.sql
-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;
USE `xmppmaster`;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_regenere_list_produit_entity()
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_regenere_list_produit_entity()
-- Description :
--   Cette procedure complete la table xmppmaster.up_list_produit pour une
--   seule entite GLPI specifiee par son glpi_id.
--   Elle conserve les entrees existantes pour cette entite, puis ajoute
--   uniquement les associations manquantes avec les produits definis dans
--   xmppmaster.applicationconfig (key='table produits', context='entity').
--
-- Etapes principales :
--   1. Verification que l'entite existe dans glpi_entity.
--   2. Parcours de la liste des produits definis dans applicationconfig.
--   3. Pour chaque produit manquant, insertion d'une ligne
--      (entity_id, name_procedure, enable=0) pour l'entite specifiee.
--
-- Parametres :
--   - p_entity_id (INT) : Identifiant GLPI de l'entite a completer.
--
-- Effets :
--   - Conserve les entrees existantes pour l'entite specifiee.
--   - Ajoute de nouvelles entrees pour cette entite couvrant l'ensemble
--     des produits definis.
--
-- Contraintes / Remarques :
--   - Le champ enable est toujours initialise a 0 (desactive par defaut).
--   - Si l'entite n'existe pas dans glpi_entity, la procedure ne fait rien.
--   - Cette procedure s'inspire du trigger xmppmasterglpi_entity_AFTER_INSERT
--     mais agit uniquement sur l'entite specifiee, et non sur toutes les entites.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_regenere_list_produit_entity`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_regenere_list_produit_entity`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_regenere_list_produit_entity`(
    IN p_entity_id INT
)
BEGIN

    DECLARE done INT DEFAULT 0;
    DECLARE v_produit VARCHAR(1024);
    DECLARE v_comment VARCHAR(2048);

    DECLARE cur CURSOR FOR
        SELECT `value`, `comment`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    IF EXISTS (SELECT 1 FROM glpi_entity WHERE glpi_id = p_entity_id) THEN
        OPEN cur;

        read_loop: LOOP
            FETCH cur INTO v_produit, v_comment;
            IF done THEN
                LEAVE read_loop;
            END IF;

            INSERT IGNORE INTO xmppmaster.up_list_produit (
                entity_id,
                name_procedure,
                enable,
                comment
            )
            VALUES (
                p_entity_id,
                v_produit,
                0,
                v_comment
            );
        END LOOP;

        CLOSE cur;
    END IF;
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : regenere_liste_produits
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_regenere_list_produit()
-- Description :
--   Cette procedure complete la table xmppmaster.up_list_produit,
--   puis ajoute les associations entite/produit manquantes pour chaque entite
--   presente dans la table xmppmaster.glpi_entity.
--
-- Fonctionnement :
--   - Conserve les lignes existantes dans xmppmaster.up_list_produit.
--   - Recupere la liste des produits configures (cle 'table produits',
--     contexte 'entity') depuis la table xmppmaster.applicationconfig.
--   - Pour chaque entite et pour chaque produit manquant, insere une ligne
--     dans up_list_produit avec enable = 0.
--
-- Tables concernees :
--   - xmppmaster.glpi_entity : source des entites.
--   - xmppmaster.applicationconfig : source des produits configures.
--   - xmppmaster.up_list_produit : table cible completee.
--
-- Remarques :
--   - Le champ enable est toujours initialise a 0, l'activation doit etre faite manuellement.
--   - Les associations existantes sont conservees afin de preserver les activations.
--   - Cette procedure complete la configuration sans remise a zero prealable.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_regenere_list_produit`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_regenere_list_produit`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_regenere_list_produit`()
BEGIN

    DECLARE done INT DEFAULT 0;
    DECLARE v_produit VARCHAR(1024);
    DECLARE v_comment VARCHAR(2048);

    DECLARE cur CURSOR FOR
        SELECT `value`, `comment`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_produit, v_comment;
        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT IGNORE INTO xmppmaster.up_list_produit (
            entity_id,
            name_procedure,
            enable,
            comment
        )
        SELECT
            e.glpi_id,
            v_produit,
            0,
            v_comment
        FROM glpi_entity e;
    END LOOP;

    CLOSE cur;
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 100;

commit;