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
DELIMITER $$
USE `xmppmaster`$$
DROP PROCEDURE IF EXISTS `up_regenere_list_produit_entity`$$
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

-- PROCEDURE : regenere_liste_produits
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
DELIMITER $$
USE `xmppmaster`$$
DROP PROCEDURE IF EXISTS `up_regenere_list_produit`$$
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

-- PROCEDURE : up_init_packages_Windows_Security_platform
-- Description :
--   Cette procedure cree une table temporaire up_packages_Windows_Security_platform
--   filtrée pour Windows Security platform uniquement (titre et produit)

DELIMITER $$
USE `xmppmaster`$$
DROP PROCEDURE IF EXISTS `up_init_packages_Windows_Security_platform`$$
CREATE PROCEDURE `up_init_packages_Windows_Security_platform`()
BEGIN
DROP TABLE IF EXISTS up_packages_Windows_Security_platform;
CREATE TABLE up_packages_Windows_Security_platform AS
    SELECT
        aa.updateid,
        bb.updateid AS updateid_package,
        aa.revisionid,
        aa.creationdate,
        aa.compagny,
        aa.product,
        aa.productfamily,
        aa.updateclassification,
        aa.prerequisite,
        aa.title,
        aa.description,
        aa.msrcseverity,
        aa.msrcnumber,
        aa.kb,
        aa.languages,
        aa.category,
        aa.supersededby,
        aa.supersedes,
        bb.payloadfiles,
        aa.revisionnumber,
        aa.bundledby_revision,
        aa.isleaf,
        aa.issoftware,
        aa.deploymentaction,
        aa.title_short
    FROM
        xmppmaster.update_data aa
    JOIN
        xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
    WHERE
        (
            -- Cas 1 : Windows Security platform
            (aa.product LIKE '%Windows Security platform%' AND aa.title LIKE '%Windows Security platform%')
            OR
            -- Cas 2 : Microsoft Defender Antivirus
            (aa.product LIKE '%Microsoft Defender Antivirus%' AND aa.title LIKE '%Microsoft Defender Antivirus%' AND aa.updateclassification = 'Definition Updates')
            OR
            -- Cas 3 : System Center Endpoint Protection
            (aa.product LIKE '%System Center Endpoint Protection%' AND aa.title LIKE '%Security Intelligence Update%' AND aa.updateclassification = 'Definition Updates')
        );
END$$

DELIMITER ;


-- Enregistrement de la procédure dans up_list_produit
INSERT IGNORE INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_init_packages_Windows_Security_platform');

-- Enregistrement du produit dans applicationconfig (active par defaut)
INSERT IGNORE INTO `xmppmaster`.`applicationconfig` (
    `key`,
    `value`,
    `comment`,
    `context`,
    `module`,
    `enable`
) VALUES (
    'table produits',
    'up_packages_Windows_Security_platform',
    'Windows Security platform',
    'entity',
    'xmppmaster/update',
    1
);

-- Execution de la procédure centrale d'initialisation
-- La procédure up_create_product_tables (définie dans schema-095.sql)
-- parcourt automatiquement l'information_schema et exécute toutes les
-- procédures commençant par up_init_packages_*, y compris la nouvelle.
CALL `xmppmaster`.`up_create_product_tables`();

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 100;

commit;