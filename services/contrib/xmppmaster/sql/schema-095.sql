--
-- (c) 2021 Siveo, http://www.siveo.net/
--
--
-- This file is part of Pulse 2, http://www.siveo.net/
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

-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;
USE `xmppmaster`;


-- =====================================================================
-- Réinitialisation et migration des tables liées à la gestion des listes
-- =====================================================================

-- 1. Vider les tables grises (pas de déclenchement de triggers car TRUNCATE)
TRUNCATE TABLE `xmppmaster`.`up_gray_list`;
TRUNCATE TABLE `xmppmaster`.`up_gray_list_flop`;
TRUNCATE TABLE `xmppmaster`.`up_white_list`;
TRUNCATE TABLE `xmppmaster`.`up_black_list`;
TRUNCATE TABLE `xmppmaster`.`up_auto_approve_rules`;

-- 2. Ajout de la colonne entityid + contrainte unique dans up_gray_list
ALTER TABLE xmppmaster.up_gray_list
   ADD COLUMN IF NOT EXISTS entityid INT(11) NOT NULL AFTER updateid;
ALTER TABLE xmppmaster.up_gray_list
   ADD UNIQUE INDEX IF NOT EXISTS `uniq_update_entity` (`updateid`, `entityid`);

-- 3. Ajout de la colonne entityid + contrainte unique dans up_gray_list_flop
ALTER TABLE `xmppmaster`.`up_gray_list_flop`
  ADD COLUMN IF NOT EXISTS `entityid` INT(11) NOT NULL AFTER `updateid`;
ALTER TABLE `xmppmaster`.`up_gray_list_flop`
  ADD UNIQUE INDEX IF NOT EXISTS `uniq_update_entity_flop` (`updateid`, `entityid`);

-- 4. Ajout de la colonne entityid + contrainte unique dans up_auto_approve_rules
-- remarque la fonction ensure_auto_approve_rules_for_entity(entityid)
-- prepare les regles si elle n'existe pas dans la table up_auto_approve_rules pour l'entity depuis le plugin pluginsmastersubstitute/plugin_update_windows.py
ALTER TABLE `xmppmaster`.`up_auto_approve_rules`
  ADD COLUMN IF NOT EXISTS `entityid` INT(11) NOT NULL AFTER `id`;
ALTER TABLE `xmppmaster`.`up_auto_approve_rules`
  ADD UNIQUE INDEX IF NOT EXISTS `uniq_entity_rule` (`entityid`, `msrcseverity`, `updateclassification`);

-- 5. Ajout de la colonne entityid + contrainte unique
ALTER TABLE `xmppmaster`.`up_white_list`
  ADD COLUMN IF NOT EXISTS `entityid` INT(11) NOT NULL AFTER `updateid`;
ALTER TABLE `xmppmaster`.`up_white_list`
  ADD UNIQUE INDEX IF NOT EXISTS `uniq_update_entity_white` (`updateid`, `entityid`);

-- 6. Ajout de la colonne entityid + contrainte unique
ALTER TABLE `xmppmaster`.`up_black_list`
  ADD COLUMN IF NOT EXISTS `entityid` INT(11) NOT NULL AFTER `updateid_or_kb`;
ALTER TABLE `xmppmaster`.`up_black_list`
  ADD UNIQUE INDEX IF NOT EXISTS `uniq_updatekb_entity_black` (`updateid_or_kb`, `entityid`);

-- supprimer en cascade
-- 1. Supprimer la foreign key (ignore l'erreur si elle n'existe pas)
ALTER TABLE `xmppmaster`.`up_gray_list` DROP FOREIGN KEY IF EXISTS `fk_up_gray_list_entity`;

-- 2. Supprimer l'index si nécessaire
ALTER TABLE `xmppmaster`.`up_gray_list` DROP INDEX IF EXISTS `fk_up_gray_list_entity_idx`;


-- 3. Ajouter l'index
ALTER TABLE `xmppmaster`.`up_gray_list` ADD INDEX IF NOT EXISTS `fk_up_gray_list_entity_idx` (`entityid` ASC);


-- 4. Ajouter la foreign key avec cascade
ALTER TABLE `xmppmaster`.`up_gray_list`
ADD CONSTRAINT `fk_up_gray_list_entity`
FOREIGN KEY (`entityid`)
REFERENCES `xmppmaster`.`glpi_entity` (`glpi_id`)
ON DELETE CASCADE
ON UPDATE CASCADE;


ALTER TABLE `xmppmaster`.`up_machine_windows`
ADD COLUMN IF NOT EXISTS `entityid` INT(11) NULL AFTER `update_id`;

ALTER TABLE `xmppmaster`.`up_machine_windows`
ADD UNIQUE INDEX IF NOT EXISTS `index_uniq_entity_uuid` (`update_id` ASC, `entityid` ASC) VISIBLE;
;


-- =====================================================================
-- Table : applicationconfig
-- Description :
--   Cette table permet de définir des paramètres applicatifs.
--   Chaque paramètre est défini par une clé (key) et une valeur (value),
--   auxquels peuvent être associés un commentaire, un contexte et un module.
--
-- Contraintes :
--   - id : clé primaire auto-incrémentée.
--   - (key, value) doit être unique (empêche les doublons).
--
-- Remarque :
--   Utiliser la colonne "comment" pour documenter la signification du paramètre.
-- =====================================================================

-- Suppression et recréation de la table applicationconfig
DROP TABLE IF EXISTS xmppmaster.applicationconfig;
CREATE TABLE `xmppmaster`.`applicationconfig` (
  `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique de la ligne',
  `key` VARCHAR(45) NOT NULL COMMENT 'Nom du paramètre',
  `value` VARCHAR(1024) NOT NULL COMMENT 'Valeur du paramètre',
  `comment` VARCHAR(400) NULL COMMENT 'Description ou notes explicatives',
  `context` VARCHAR(45) NULL COMMENT 'Contexte d’utilisation (ex: environnement, domaine)',
  `module` VARCHAR(45) NULL COMMENT 'Module ou sous-système concerné',
  `enable` TINYINT(1) NULL DEFAULT 1 COMMENT 'Indique si la configuration est activée',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_key_value` (`key`, `value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Table de configuration applicative (paramètres généraux et contextuels)';

-- Vidage de la table avant insertion
TRUNCATE xmppmaster.applicationconfig;

-- Insertion des données pour les produits Microsoft
INSERT IGNORE INTO `applicationconfig` (`id`, `key`, `value`, `comment`, `context`, `module`, `enable`) VALUES
-- Serveurs Windows
(1,'table produits','up_packages_WS_X64_2003','Microsoft Server 2003 [ fin support 2015/07 ]','entity','xmppmaster/update',1),
(2,'table produits','up_packages_WS_X64_2008','Microsoft Server 2008 [ fin support 2020/01 ]','entity','xmppmaster/update',1),
(3,'table produits','up_packages_WS_X64_2012','Microsoft Server 2012 [ fin support 2023/10 ]','entity','xmppmaster/update',1),
(4,'table produits','up_packages_WS_X64_2016','Microsoft Server 2016 [ fin support 2029/01 ]','entity','xmppmaster/update',1),
(5,'table produits','up_packages_WS_X64_2019','Microsoft Server 2019 [ fin support 2029/01 ]','entity','xmppmaster/update',1),
(6,'table produits','up_packages_MSOS_ARM64_24H2','Microsoft Server 2025 [ fin support 2034/10 ]','entity','xmppmaster/update',1),
(7,'table produits','up_packages_MSOS_X64_21H2','Microsoft Server 2022 [ fin support 2029/01 ]','entity','xmppmaster/update',1),
(8,'table produits','up_packages_MSOS_X64_22H2','Microsoft Server 2022 [ fin support 2031/10 ]','entity','xmppmaster/update',1),
(9,'table produits','up_packages_MSOS_X64_23H2','Microsoft Server 2022 [ fin support 2031/10 ]','entity','xmppmaster/update',1),
(10,'table produits','up_packages_MSOS_X64_24H2','Microsoft Server 2025 [ fin support 2034/10 ]','entity','xmppmaster/update',1),

-- Visual Studio
(11,'table produits','up_packages_Vstudio_2008','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),
(12,'table produits','up_packages_Vstudio_2010','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),
(13,'table produits','up_packages_Vstudio_2012','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),
(14,'table produits','up_packages_Vstudio_2013','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),
(15,'table produits','up_packages_Vstudio_2015','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),
(16,'table produits','up_packages_Vstudio_2017','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),
(17,'table produits','up_packages_Vstudio_2019','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),
(18,'table produits','up_packages_Vstudio_2022','Microsoft Visual Studio IDE complet','entity','xmppmaster/update',0),

-- Office
(19,'table produits','up_packages_office_2003_64bit','Microsoft Office suite bureautique','entity','xmppmaster/update',0),
(20,'table produits','up_packages_office_2007_64bit','Microsoft Office suite bureautique','entity','xmppmaster/update',0),
(21,'table produits','up_packages_office_2010_64bit','Microsoft Office suite bureautique','entity','xmppmaster/update',0),
(22,'table produits','up_packages_office_2013_64bit','Microsoft Office suite bureautique','entity','xmppmaster/update',0),
(23,'table produits','up_packages_office_2016_64bit','Microsoft Office suite bureautique','entity','xmppmaster/update',0),
(23,'table produits','up_packages_office_2019_64bit','Microsoft Office suite bureautique','entity','xmppmaster/update',0),
-- Windows 10/11
(24,'table produits','up_packages_Win10_X64_1903','Microsoft Windows 10 [ fin support 2025/10 ]','entity','xmppmaster/update',1),
(25,'table produits','up_packages_Win10_X64_21H1','Microsoft Windows 10 [ fin support 2025/10 ]','entity','xmppmaster/update',1),
(26,'table produits','up_packages_Win10_X64_21H2','Microsoft Windows 10 [ fin support 2025/10 ]','entity','xmppmaster/update',1),
(27,'table produits','up_packages_Win10_X64_22H2','Microsoft Windows 10 [ fin support 2025/10 ]','entity','xmppmaster/update',1),
(28,'table produits','up_packages_Win11_X64','Microsoft Windows 11 [ fin support 2029/10 ]','entity','xmppmaster/update',1),
(29,'table produits','up_packages_Win11_X64_21H2','Microsoft Windows 11 [ fin support 2029/10 ]','entity','xmppmaster/update',1),
(30,'table produits','up_packages_Win11_X64_22H2','Microsoft Windows 11 [ fin support 2029/10 ]','entity','xmppmaster/update',1),
(31,'table produits','up_packages_Win11_X64_23H2','Microsoft Windows 11 [ fin support 2029/10 ]','entity','xmppmaster/update',1),
(32,'table produits','up_packages_Win11_X64_24H2','Microsoft Windows 11 [ fin support 2029/10 ]','entity','xmppmaster/update',1),
(33,'table produits','up_packages_Win_Malicious_X64','Malicious Software Removal Tool (MSRT)','entity','xmppmaster/update',1),

-- Règles de mise à jour
(34,'Critical Updates','','table rules','entity','xmppmaster/update',1),
(35,'Security Updates','','table rules','entity','xmppmaster/update',1),
(36,'Service Packs','','table rules','entity','xmppmaster/update',1),
(37,'Update Rollups','','table rules','entity','xmppmaster/update',1),
(38,'Updates','','table rules','entity','xmppmaster/update',1),
(39,'Security Updates','Critical','table rules','entity','xmppmaster/update',1),
(40,'Security Updates','Important','table rules','entity','xmppmaster/update',1),
(41,'Security Updates','Low','table rules','entity','xmppmaster/update',1),
(42,'Security Updates','Moderate','table rules','entity','xmppmaster/update',1);



-- =====================================================================
-- Table : up_list_produit
-- Description :
--   Cette table stocke la liste des mise à jour Microsoft associés à chaque entité GLPI.
--   Chaque ligne correspond à un produit activable/désactivable pour une entité.
--
-- Colonnes :
--   - id : Identifiant technique unique (clé primaire auto-incrémentée).
--   - entity_id : Référence vers l’identifiant d’une entité GLPI (glpi_entity.id).
--   - name_procedure : Nom du produit ou de la procédure associé à l’entité.
--   - enable : Indique si le produit est activé (1) ou désactivé (0, par défaut).
--
-- Contraintes :
--   - PRIMARY KEY (id) : identifiant unique technique.
--   - UNIQUE (entity_id, name_procedure) : une entité ne peut pas avoir deux fois
--     le même produit associé.
--
-- Remarques :
--   - Les entrées sont créées automatiquement lors de l’ajout d’une entité
--     via un trigger.
--   - Le champ enable est initialisé à 0, l’activation se fait ensuite manuellement.
-- =====================================================================


-- Suppression et recréation de la table up_list_produit
DROP TABLE IF EXISTS xmppmaster.up_list_produit;
CREATE TABLE xmppmaster.up_list_produit (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identifiant technique',
    entity_id INT NOT NULL COMMENT 'Référence vers glpi_entity.id',
    name_procedure VARCHAR(255) NOT NULL COMMENT 'Nom du produit/procédure associé à l’entité',
    enable TINYINT(1) DEFAULT 0 COMMENT 'Activation (0 = désactivé par défaut)',
    comment VARCHAR(2048) NULL COMMENT 'Description ou notes explicatives',
    UNIQUE KEY uniq_entity_procedure (entity_id, name_procedure)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Liste des produits associés à une entité GLPI';



USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2003_64bit`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_office_2003_64bit`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_office_2003_64bit;

    CREATE TABLE up_packages_office_2003_64bit AS
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
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
        WHERE
            aa.product LIKE '%Office 2003%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%32-Bit%'
            AND aa.title NOT LIKE '%Server%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$
DELIMITER ;

-- =======================================
-- up_init_packages_office_2007_64bit stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2007_64bit`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_office_2007_64bit`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_office_2007_64bit;
       CREATE TABLE up_packages_office_2007_64bit AS
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
            aa.product LIKE '%Office 2007%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%32-Bit%'
            AND aa.title NOT LIKE '%Server%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_office_2010_64bit stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2010_64bit`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_office_2010_64bit`()
BEGIN
   -- Supprime la table si elle existe (sans SQL dynamique)
   DROP TABLE IF EXISTS up_packages_office_2010_64bit;
   CREATE TABLE  up_packages_office_2010_64bit AS
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
            aa.product LIKE '%Office 2010%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%32-Bit%'
            AND aa.title NOT LIKE '%Server%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;

USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2013_64bit`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_office_2013_64bit`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_office_2013_64bit;
    CREATE TABLE  up_packages_office_2013_64bit AS
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
            aa.product LIKE '%Office 2013%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%32-Bit%'
            AND aa.title NOT LIKE '%Server%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_office_2016_64bit stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2016_64bit`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_office_2016_64bit`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_office_2016_64bit;
    CREATE TABLE up_packages_office_2016_64bit AS
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
            aa.product LIKE '%Office 2016%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%32-Bit%'
            AND aa.title NOT LIKE '%Server%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_office_2016_64bit stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_packages_office_2019_64bit`;

DELIMITER $$

CREATE PROCEDURE `up_packages_office_2019_64bit`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_office_2019_64bit;
    CREATE TABLE up_packages_office_2019_64bit AS
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
            aa.product LIKE '%Office 2019%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%32-Bit%'
            AND aa.title NOT LIKE '%Server%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Vstudio_2005 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2005`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2005`()
BEGIN
-- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2005;
    CREATE TABLE up_packages_Vstudio_2005 AS
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
            aa.product LIKE '%Visual Studio 2005%';
END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Vstudio_2008 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2008`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2008`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2008;
    CREATE TABLE up_packages_Vstudio_2008 AS
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
            aa.product LIKE '%Visual Studio 2008%';
END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Vstudio_2010 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2010`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2010`()
BEGIN
-- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2010;
    CREATE TABLE up_packages_Vstudio_2010 AS
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
            aa.product LIKE '%Visual Studio 2010%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_Vstudio_2012 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2012`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2012`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2012;
    CREATE TABLE up_packages_Vstudio_2012 AS
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
            aa.product LIKE '%Visual Studio 2012%';
END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Vstudio_2013 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2013`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2013`()
BEGIN
-- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2013;
    CREATE TABLE up_packages_Vstudio_2013 AS
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
            aa.product LIKE '%Visual Studio 2013%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_Vstudio_2015 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2015`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2015`()
BEGIN
-- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2015;
    CREATE TABLE up_packages_Vstudio_2015 AS
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
            aa.product LIKE '%Visual Studio 2015%';
END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Vstudio_2017 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2017`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2017`()
BEGIN
-- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2017;
    CREATE TABLE up_packages_Vstudio_2017 AS
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
            aa.product LIKE '%Visual Studio 2017%';
END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Vstudio_2019 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2019`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2019`()
BEGIN
-- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2019;
    CREATE TABLE up_packages_Vstudio_2019 AS
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
            aa.product LIKE '%Visual Studio 2019%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_Vstudio_2022 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2022`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Vstudio_2022`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Vstudio_2022;
    CREATE TABLE up_packages_Vstudio_2022 AS
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
            aa.product LIKE '%Visual Studio 2022%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_Win10_X64_1903 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_1903`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win10_X64_1903`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows 10 version 1903 X64
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win10_X64_1903;

    CREATE TABLE up_packages_Win10_X64_1903 AS
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
            aa.title LIKE '%Version 1903%' AND
            aa.product LIKE '%Windows 10, version 1903 and later%' AND
            aa.title NOT LIKE '%ARM64%' AND
            aa.title NOT LIKE '%X86%' AND
            aa.title NOT LIKE '%Dynamic%' AND
            aa.title LIKE '%X64%';
END$$

DELIMITER ;
-- =======================================
-- up_init_packages_Win10_X64_21H1 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_21H1`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win10_X64_21H1`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows 10 version 21H1 X64
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win10_X64_21H1;
    CREATE TABLE up_packages_Win10_X64_21H1 AS
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
            aa.title LIKE '%21H1%' AND
            (aa.product LIKE '%Windows 10, version 1903 and later%' OR aa.product LIKE '%Windows 10 and later GDR-DU%') AND
            aa.title NOT LIKE '%ARM64%' AND
            aa.title NOT LIKE '%X86%' AND
            aa.title NOT LIKE '%Dynamic%' AND
            aa.title LIKE '%X64%';
END$$

DELIMITER ;

-- =======================================
-- up_init_packages_Win10_X64_21H2 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_21H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win10_X64_21H2`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows 10 Version 21H2 X64
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win10_X64_21H2;

    CREATE TABLE up_packages_Win10_X64_21H2 AS
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
            aa.title LIKE '%Windows 10 Version 21H2%' AND
            aa.product LIKE '%Windows 10%' AND
            aa.title NOT LIKE '%ARM64%' AND
            aa.title NOT LIKE '%X86%' AND
            aa.title NOT LIKE '%Dynamic%' AND
            aa.title LIKE '%X64%';
END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Win10_X64_22H2 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_22H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win10_X64_22H2`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows 10 Version 22H2 X64
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win10_X64_22H2;
    CREATE TABLE up_packages_Win10_X64_22H2 AS
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
            aa.title LIKE '%Windows 10 Version 22H2%' AND
            (aa.product LIKE '%Windows 10, version 1903 and later%' OR aa.product LIKE '%Windows 10 and later GDR-DU%') AND
            aa.title NOT LIKE '%ARM64%' AND
            aa.title NOT LIKE '%X86%' AND
            aa.title NOT LIKE '%Dynamic%' AND
            aa.title LIKE '%X64%';
END$$

DELIMITER ;
































-- =======================================
-- up_init_packages_Win11_X64 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows 11 x64 (hors versions H2 spécifiques)
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64;
    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    CREATE TABLE up_packages_Win11_X64 AS
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
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
        WHERE
            aa.product LIKE '%Windows 11%' AND
            aa.title NOT LIKE '%ARM64%' AND
            aa.title NOT LIKE '%X86%' AND
            aa.title NOT LIKE '%Dynamic%' AND
            aa.title NOT LIKE '%22H2%' AND
            aa.title NOT LIKE '%23H2%' AND
            aa.title NOT LIKE '%21H2%';
END$$

DELIMITER ;


USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_21H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_21H2`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows 11 Version 21H2 x64
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_21H2;
    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    CREATE TABLE up_packages_Win11_X64_21H2 AS
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
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
        WHERE
            aa.title LIKE '%Windows 11 Version 21H2%' AND
            aa.product LIKE '%Windows 11%' AND
            aa.title NOT LIKE '%ARM64%' AND
            aa.title NOT LIKE '%X86%' AND
            aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;


USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_22H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_22H2`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows 11 Version 22H2 x64
    -- =======================================

    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_22H2;
    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
        CREATE TABLE up_packages_Win11_X64_22H2 AS
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
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
        WHERE
            aa.title LIKE '%Windows 11 Version 22H2%' AND
            aa.product LIKE '%Windows 11%' AND
            aa.title NOT LIKE '%ARM64%' AND
            aa.title NOT LIKE '%X86%' AND
            aa.title NOT LIKE '%Dynamic%';

END$$

DELIMITER ;

USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_23H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_23H2`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_23H2;

    -- Création de la table avec jointure et filtres spécifiques
    CREATE TABLE up_packages_Win11_X64_23H2 AS
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
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
        WHERE
            aa.title LIKE '%Windows 11 Version 23H2%'
            AND aa.product LIKE '%Windows 11%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;


USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_24H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_24H2`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_24H2;
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    CREATE TABLE up_packages_Win11_X64_24H2 AS
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
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
         WHERE
            aa.title LIKE '%Windows 11 Version 24H2%'
            AND aa.product LIKE '%Windows 11%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';

END$$

DELIMITER ;


-- =======================================
-- up_init_packages_Win_Malicious_X64 stored procedure
-- =======================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win_Malicious_X64`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win_Malicious_X64`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Win_Malicious_X64`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win_Malicious_X64;

    -- Crée la table en résultat d'une sélection (sans SQL dynamique)
    CREATE TABLE up_packages_Win_Malicious_X64 AS
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
        JOIN xmppmaster.update_data bb
            ON bb.bundledby_revision = aa.revisionid
    WHERE
        aa.title LIKE '%Windows Malicious Software Removal Tool x64%'
        AND aa.product LIKE '%Windows 1%'
    ORDER BY aa.revisionid DESC;

END$$

DELIMITER ;
;


-- =======================================
-- up_create_product_tables stored procedure
-- =======================================

-- =======================================
-- Procedure: up_create_product_tables
-- Author   : (ton nom)
-- Purpose  : Parcourt toutes les procédures d’initialisation de packages
--             (nommées up_init_packages_*) dans la base xmppmaster et
--             génère dynamiquement la commande SQL d’appel pour chacune.
--
-- Usage    :
--   CALL up_create_product_tables();
--
-- Output   :
--   Une liste de chaînes du type :
--     CALL up_init_packages_nom();
--   (Non exécutées, simplement affichées)
--
-- Notes    :
--   - Les procédures "up_init_packages_*" doivent exister dans xmppmaster.
--   - Si tu veux qu’elles soient réellement exécutées, remplacer le SELECT
--     par un EXECUTE PREPARE dynamique.
-- =======================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_create_product_tables`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_create_product_tables` ()
BEGIN
 DECLARE done INT DEFAULT FALSE;
  DECLARE proc_name VARCHAR(255);
  DECLARE sql_stmt TEXT;

  DECLARE cur CURSOR FOR
    SELECT ROUTINE_NAME
    FROM information_schema.ROUTINES
    WHERE ROUTINE_SCHEMA = DATABASE()
      AND ROUTINE_TYPE = 'PROCEDURE'
      AND ROUTINE_NAME LIKE 'up_init_packages_%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
  BEGIN
    GET DIAGNOSTICS CONDITION 1
      @sqlstate = RETURNED_SQLSTATE,
      @message = MESSAGE_TEXT;
    SELECT CONCAT('⚠️ Erreur SQL dans ', proc_name, ' → ', @sqlstate, ' : ', @message) AS error_msg;
  END;

  -- Sécurité de session
  SET SESSION wait_timeout = 600;
  SET SESSION max_allowed_packet = 256*1024*1024;

  OPEN cur;

  read_loop: LOOP
    FETCH cur INTO proc_name;
    IF done THEN
      LEAVE read_loop;
    END IF;

    -- Utiliser une variable de session (prépare l'exécution dynamique)
    SET @sql_stmt = CONCAT('CALL ', proc_name, '();');

    -- Exécuter dynamiquement
    PREPARE stmt FROM @sql_stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SELECT CONCAT('✓ Procédure exécutée : ', proc_name) AS success_msg;
  END LOOP;

  CLOSE cur;
END$$

DELIMITER ;



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

            ELSE
                SET @query = "SELECT * FROM xmppmaster.update_data;";
        END CASE;

        PREPARE stmt FROM @query;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END;
END$$

DELIMITER ;






















--
-- 2024-2025 Medulla, http://www.medulla-tech.io
--
-- This file is part of Medulla, https://medulla-tech.io/
--
-- SPDX-License-Identifier: GPL-3.0-or-later
--
-- Medulla is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
--
-- Medulla is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla.  If not, see <https://www.gnu.org/licenses/>.
--
-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------

START TRANSACTION;
USE `xmppmaster`;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : `up_genere_list_rule_entity`()
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : `up_genere_list_rule_entity`()
-- ---------------------------------------------------------------------
-- Description :
--   Cette procédure initialise la table `xmppmaster.up_auto_approve_rules`
--   pour une entité GLPI donnée (`p_entity_id`) uniquement si celle-ci existe.
--   Elle ne supprime rien : si des règles existent déjà pour l’entité,
--   la procédure ne les modifie pas.
--   Si aucune règle n’existe, elle insère celles définies dans
--   `xmppmaster.applicationconfig` (key='table rules', context='entity').
--
-- Étapes principales :
--   1. Vérifie que l'entité existe dans `glpi_entity`.
--   2. Parcourt les entrées `applicationconfig` correspondant aux règles actives.
--   3. Insère pour chaque règle un enregistrement dans `up_auto_approve_rules`
--      avec `active_rule = 0` pour l’entité donnée.
--
-- Paramètres :
--   - p_entity_id (INT) : Identifiant GLPI de l’entité à initialiser.
--
-- Effets :
--   - Ne supprime aucune donnée existante.
--   - Ajoute uniquement les entrées manquantes pour l’entité.
--
-- Contraintes / Remarques :
--   - Le champ `active_rule` est toujours initialisé à 0 (désactivé par défaut).
--   - Si l’entité n’existe pas dans `glpi_entity`, la procédure ne fait rien.
--   - Cette procédure est complémentaire à `up_regenere_list_produit_entity()`,
--     mais limitée à l’initialisation des règles automatiques.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_genere_list_rule_entity`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_genere_list_rule_entity`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_genere_list_rule_entity`(IN p_entity_id INT)
BEGIN

    -- Variables
    DECLARE done INT DEFAULT 0;
    DECLARE v_msrcseverity VARCHAR(1024);
    DECLARE v_updateclassification VARCHAR(1024);

    -- Curseur pour parcourir applicationconfig
    DECLARE cur CURSOR FOR
        SELECT `value`, `key`
        FROM xmppmaster.applicationconfig
        WHERE `comment` = 'table rules'
          AND `context` = 'entity'
          AND `enable` = 1 order by value desc;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Vérifier si l'entité existe
    IF EXISTS (SELECT 1 FROM glpi_entity WHERE glpi_id = p_entity_id) THEN
        -- Ouvrir le curseur
        OPEN cur;

        read_loop: LOOP
            FETCH cur INTO v_msrcseverity, v_updateclassification;
            IF done THEN
                LEAVE read_loop;
            END IF;

            -- Insérer les règles pour l’entité donnée
            INSERT INTO xmppmaster.up_auto_approve_rules
            (`entityid`, `msrcseverity`, `updateclassification`, `active_rule`)
            VALUES
            (p_entity_id, v_msrcseverity, v_updateclassification, 0);
        END LOOP;

        CLOSE cur;
    END IF;
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_genere_list_produit_entity()
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_genere_list_produit_entity()
-- Description :
--   Cette procédure initialise la table xmppmaster.up_list_produit pour une
--   entité GLPI donnée (spécifiée par son glpi_id) uniquement si aucun produit
--   n’y est encore associé.
--   Elle ne supprime rien : si des produits existent déjà pour l’entité,
--   la procédure ne fait aucune modification.
--   Dans le cas contraire, elle insère les produits définis dans
--   xmppmaster.applicationconfig (key='table produits', context='entity').
--
-- Étapes principales :
--   1. Vérification que l'entité existe dans glpi_entity.
--   2. Vérification de la présence d’entrées dans up_list_produit pour cette entité.
--   3. Si aucune entrée n’existe :
--        a. Parcours de la liste des produits définis dans applicationconfig.
--        b. Insertion d’une ligne (entity_id, name_procedure, enable=0)
--           pour chaque produit associé à l’entité spécifiée.
--
-- Paramètres :
--   - p_entity_id (INT) : Identifiant GLPI de l’entité à initialiser.
--
-- Effets :
--   - Ne supprime aucune donnée existante.
--   - Ajoute de nouvelles entrées uniquement si l’entité n’a encore aucun produit.
--
-- Contraintes / Remarques :
--   - Le champ enable est toujours initialisé à 0 (désactivé par défaut).
--   - Si l’entité n’existe pas dans glpi_entity, la procédure ne fait rien.
--   - Cette procédure est complémentaire à up_regenere_list_produit_entity(),
--     mais ne fait l’insertion que si nécessaire.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_genere_list_produit_entity`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_genere_list_produit_entity`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_genere_list_produit_entity`(IN p_entity_id INT)
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_produit VARCHAR(1024);
    DECLARE v_comment VARCHAR(2048);
    DECLARE cur CURSOR FOR
        SELECT `value`, `comment`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity'
          AND `enable` = 1
        ORDER BY `comment`;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    IF EXISTS (SELECT 1 FROM glpi_entity WHERE glpi_id = p_entity_id) THEN
       -- IF NOT EXISTS (
        --    SELECT 1 FROM xmppmaster.up_list_produit
        --    WHERE entity_id = p_entity_id limit 1
      --  ) THEN
            OPEN cur;
            read_loop: LOOP
                FETCH cur INTO v_produit, v_comment;
                IF done THEN
                    LEAVE read_loop;
                END IF;
                INSERT IGNORE INTO xmppmaster.up_list_produit (entity_id, name_procedure, comment, enable)
                VALUES (p_entity_id, v_produit, v_comment, 0);
            END LOOP;

            CLOSE cur;
      --  END IF;
    END IF;
END$$

DELIMITER ;
;


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
--   Cette procédure régénère la table xmppmaster.up_list_produit pour une
--   seule entité GLPI spécifiée par son glpi_id.
--   Elle supprime d’abord les entrées existantes pour cette entité, puis
--   recrée toutes les associations avec les produits définis dans
--   xmppmaster.applicationconfig (key='table produits', context='entity').
--
-- Étapes principales :
--   1. Vérification que l'entité existe dans glpi_entity.
--   2. Suppression des anciennes lignes pour cette entité dans up_list_produit.
--   3. Parcours de la liste des produits définis dans applicationconfig.
--   4. Pour chaque produit, insertion d’une ligne (entity_id, name_procedure, enable=0)
--      pour l’entité spécifiée.
--
-- Paramètres :
--   - p_entity_id (INT) : Identifiant GLPI de l’entité à régénérer.
--
-- Effets :
--   - Supprime toutes les entrées existantes pour l’entité spécifiée.
--   - Ajoute de nouvelles entrées pour cette entité couvrant l’ensemble
--     des produits définis.
--
-- Contraintes / Remarques :
--   - Le champ enable est toujours initialisé à 0 (désactivé par défaut).
--   - Si l’entité n’existe pas dans glpi_entity, la procédure ne fait rien.
--   - Cette procédure s’inspire du trigger xmppmasterglpi_entity_AFTER_INSERT
--     mais agit uniquement sur l’entité spécifiée, et non sur toutes les entités.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_regenere_list_produit_entity`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_regenere_list_produit_entity`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_regenere_list_produit_entity`(
    IN p_entity_id INT
)
BEGIN


    -- Variables pour le curseur
    DECLARE done INT DEFAULT 0;
    DECLARE v_produit VARCHAR(1024);

    -- Déclaration du curseur
    DECLARE cur CURSOR FOR
        SELECT `value`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity';

    -- Gestion fin de curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Vérifier que l'entité existe
    IF EXISTS (SELECT 1 FROM glpi_entity WHERE glpi_id = p_entity_id) THEN

        -- Supprimer les anciennes lignes pour cette entité
        DELETE FROM xmppmaster.up_list_produit
        WHERE entity_id = p_entity_id;

        -- Ouvrir le curseur
        OPEN cur;

        read_loop: LOOP
            FETCH cur INTO v_produit;
            IF done THEN
                LEAVE read_loop;
            END IF;

            -- Réinsérer les produits pour l’entité donnée
            INSERT INTO xmppmaster.up_list_produit (entity_id, name_procedure, enable)
            VALUES (p_entity_id, v_produit, 0);
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
--   Cette procédure régénère entièrement la table xmppmaster.up_list_produit.
--   Elle vide d’abord le contenu existant (TRUNCATE), puis recrée toutes les
--   associations entre les entités GLPI (glpi_entity) et les produits définis
--   dans xmppmaster.applicationconfig (key='table produits', context='entity').
--
-- Étapes principales :
--   1. Remise à zéro de la table up_list_produit (TRUNCATE).
--   2. Parcours de la liste des produits définis dans applicationconfig.
--   3. Pour chaque produit, insertion d’une ligne (entity_id, name_procedure, enable=0)
--      pour toutes les entités présentes dans glpi_entity.
--
-- Paramètres :
--   - Aucun.
--
-- Effets :
--   - Supprime toutes les entrées existantes dans xmppmaster.up_list_produit.
--   - Ajoute de nouvelles entrées pour couvrir l’ensemble des entités et produits.
--
-- Contraintes / Remarques :
--   - Le champ enable est toujours initialisé à 0 (désactivé par défaut).
--   - La procédure peut être appelée manuellement pour forcer une remise à plat
--     de la configuration produits/entités.
--   - Elle s’inspire du trigger xmppmasterglpi_entity_AFTER_INSERT mais agit
--     globalement sur toutes les entités déjà existantes.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_regenere_list_produit`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_regenere_list_produit`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_regenere_list_produit`()
BEGIN

    -- Variables pour le curseur
    DECLARE done INT DEFAULT 0;
    DECLARE v_produit VARCHAR(1024);
    -- Déclaration du curseur
    DECLARE cur CURSOR FOR
        SELECT `value`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity'
          AND `enable` = 1;

    -- Gestion fin de curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- On remet à zéro la liste (doit venir après les DECLARE)
    TRUNCATE TABLE xmppmaster.up_list_produit;

    -- Ouvrir le curseur
    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_produit;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Insérer pour chaque entité trouvée
        INSERT INTO xmppmaster.up_list_produit (entity_id, name_procedure, enable)
        SELECT e.glpi_id, v_produit, 0
        FROM glpi_entity e;
    END LOOP;

    CLOSE cur;
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
-- PROCEDURE : regenere_liste_produits
-- Description :
--   Réinitialise complètement la table xmppmaster.up_list_produit,
--   puis régénère les associations entité/produit pour chaque entité
--   présente dans la table xmppmaster.glpi_entity.
--
-- Fonctionnement :
--   - Vide la table xmppmaster.up_list_produit.
--   - Récupère la liste des produits configurés (clé 'tables produits', contexte 'entity')
--     depuis la table xmppmaster.applicationconfig.
--   - Pour chaque entité et pour chaque produit, insère une ligne dans up_list_produit
--     avec enable = 0.
--
-- Tables concernées :
--   - xmppmaster.glpi_entity : source des entités.
--   - xmppmaster.applicationconfig : source des produits configurés.
--   - xmppmaster.up_list_produit : table cible (reconstruite).
--
-- Remarques :
--   - Le champ enable est toujours initialisé à 0, l’activation doit être faite manuellement.
--   - Toutes les anciennes associations sont supprimées avant reconstruction.
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

    -- Variables pour le curseur
    DECLARE done INT DEFAULT 0;
    DECLARE v_produit VARCHAR(1024);
    -- Déclaration du curseur
    DECLARE cur CURSOR FOR
        SELECT `value`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity';

    -- Gestion fin de curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- On remet à zéro la liste (doit venir après les DECLARE)
    TRUNCATE TABLE xmppmaster.up_list_produit;

    -- Ouvrir le curseur
    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_produit;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Insérer pour chaque entité trouvée
        INSERT INTO xmppmaster.up_list_produit (entity_id, name_procedure, enable)
        SELECT e.glpi_id, v_produit, 0
        FROM glpi_entity e;
    END LOOP;

    CLOSE cur;
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : glpi_entity_AFTER_INSERT
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : glpi_entity_AFTER_INSERT
-- Description :
--   Ce trigger s’exécute après l’insertion d’une nouvelle entité dans la table glpi_entity.
--   Il initialise automatiquement la liste des produits associés à cette entité,
--   en se basant sur la configuration stockée dans la table applicationconfig.
--
-- Fonctionnement :
--   - Récupère la liste des produits configurés (clé 'tables produits', contexte 'entity')
--     depuis la table xmppmaster.applicationconfig.
--   - Pour chaque produit trouvé, insère une ligne dans xmppmaster.up_list_produit,
--     associée à la nouvelle entité, avec enable=0 (désactivé par défaut).
--   - Ne duplique pas les entrées : vérifie l’absence de (entity_id, name_procedure) avant insertion.
--
-- Tables concernées :
--   - xmppmaster.glpi_entity : table source (déclenche le trigger).
--   - xmppmaster.applicationconfig : source de la liste des produits à associer.
--   - xmppmaster.up_list_produit : table cible (stocke les associations entité/produit).
--
-- Remarques :
--   - Utilise un curseur pour parcourir dynamiquement les produits configurés.
--   - Le champ enable est toujours initialisé à 0, l’activation doit être faite manuellement.
--   - Le trigger garantit qu’une entité ne peut pas avoir deux fois le même produit associé.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`glpi_entity_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`glpi_entity_AFTER_INSERT`
AFTER INSERT ON `glpi_entity`
FOR EACH ROW
BEGIN


    DECLARE done INT DEFAULT 0;
    DECLARE v_produit VARCHAR(1024);

    DECLARE cur CURSOR FOR
        SELECT `value`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'tables produits'
          AND `context` = 'entity';
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_produit;
        IF done THEN
            LEAVE read_loop;
        END IF;

        IF NOT EXISTS (
            SELECT 1
            FROM xmppmaster.up_list_produit
            WHERE entity_id = NEW.glpi_id
              AND name_procedure = v_produit
        ) THEN
            INSERT INTO xmppmaster.up_list_produit (entity_id, name_procedure, enable)
            VALUES (NEW.glpi_id, v_produit, 0);
        END IF;
    END LOOP;

    CLOSE cur;
END$$
DELIMITER ;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : glpi_entity_AFTER_UPDATE
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : glpi_entity_AFTER_UPDATE
-- Description :
--   Ce trigger s’exécute après la mise à jour d’une ligne dans la table glpi_entity.
--   Il permet de maintenir la cohérence des associations entité/produit dans la table
--   xmppmaster.up_list_produit lorsque l’identifiant (glpi_id) d’une entité est modifié.
--
-- Fonctionnement :
--   - Si la valeur de glpi_id change (OLD.glpi_id ≠ NEW.glpi_id) :
--     - Supprime les éventuelles entrées déjà existantes dans xmppmaster.up_list_produit
--       pour le nouvel identifiant (NEW.glpi_id), afin d’éviter les doublons.
--     - Met à jour toutes les entrées avec l’ancien identifiant (OLD.glpi_id)
--       pour les associer au nouvel identifiant (NEW.glpi_id).
--
-- Tables concernées :
--   - xmppmaster.glpi_entity : table source (déclenche le trigger).
--   - xmppmaster.up_list_produit : table cible (contient les associations entité/produit).
--
-- Remarques :
--   - Ce trigger suppose que glpi_id peut être modifié manuellement, bien que cela soit rare.
--   - Il agit uniquement si la valeur de glpi_id change effectivement.
--   - Les suppressions sont faites avant la mise à jour pour éviter toute collision d’ID.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`glpi_entity_AFTER_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`glpi_entity_AFTER_UPDATE`
AFTER UPDATE ON `glpi_entity`
FOR EACH ROW
BEGIN

    IF OLD.glpi_id <> NEW.glpi_id THEN
        DELETE FROM xmppmaster.up_list_produit
        WHERE entity_id = NEW.glpi_id;
        UPDATE xmppmaster.up_list_produit
        SET entity_id = NEW.glpi_id
        WHERE entity_id = OLD.glpi_id;
    END IF;
END$$
DELIMITER ;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : glpi_entity_AFTER_DELETE
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : glpi_entity_AFTER_DELETE
-- Description :
--   Ce trigger s’exécute après la suppression d’une entité dans la table glpi_entity.
--   Il supprime automatiquement toutes les associations de produits liées à cette entité
--   dans la table xmppmaster.up_list_produit, afin d’éviter les données orphelines.
--
-- Fonctionnement :
--   - Récupère l’identifiant de l’entité supprimée (OLD.glpi_id).
--   - Supprime toutes les lignes de xmppmaster.up_list_produit où entity_id correspond à glpi_id.
--
-- Tables concernées :
--   - xmppmaster.glpi_entity : table source (déclenche le trigger).
--   - xmppmaster.up_list_produit : table cible (nettoyée lors de la suppression d’une entité).
--
-- Remarques :
--   - Ce trigger évite que des produits restent liés à des entités inexistantes.
--   - Aucun contrôle supplémentaire n’est effectué : la suppression est inconditionnelle.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`glpi_entity_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`glpi_entity_AFTER_DELETE`
AFTER DELETE ON `glpi_entity`
FOR EACH ROW
BEGIN

  DELETE FROM xmppmaster.up_list_produit
  WHERE entity_id = OLD.glpi_id;
END$$
DELIMITER ;

-- =====================================================================
-- =====================================================================
-- =====================================================================

--
-- Dumping data for table `up_auto_approve_rules`
--
/*
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
*/


-- ----------------------------------------------------------------------
-- Database cretion table produit Server
-- ----------------------------------------------------------------------
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- on cree la table avec les mise a jour des produits par des procedures.
-- =====================================================================
-- =====================================================================
-- =====================================================================


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_ARM64_24H2
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- création table up_packages_MSOS_ARM64_24H2
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_ARM64_24H2
-- Description :
--   Cette procédure initialise la table `up_packages_MSOS_ARM64_24H2` en extrayant
--   les mises à jour spécifiques au **système d'exploitation serveur Microsoft
--   version 24H2 (ARM64)** depuis la table `xmppmaster.update_data`.
--   Elle prépare les données nécessaires pour le déploiement des packages
--   liés à cette version et architecture du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_ARM64_24H2` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 24H2".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'inclusion exclusive de l'architecture ARM64.
--     * L'exclusion des architectures X86 et X64.
--     * L'exclusion des titres contenant "Dynamic".
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques au **système d'exploitation serveur Microsoft version 24H2 (ARM64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_server_MSOS_ARM64_24H2`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_MSOS_ARM64_24H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_MSOS_ARM64_24H2`()
BEGIN

DROP TABLE IF EXISTS up_packages_MSOS_ARM64_24H2;
CREATE TABLE up_packages_MSOS_ARM64_24H2 AS
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
		aa.title LIKE '%Microsoft server operating system version 24H2%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title not LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_21H2
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_21H2
-- Description :
--   Cette procédure initialise la table `up_packages_MSOS_X64_21H2` en extrayant
--   les mises à jour spécifiques au **système d'exploitation serveur Microsoft
--   version 21H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prépare les données nécessaires pour le déploiement des packages
--   liés à cette version du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_21H2` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 21H2".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques au **système d'exploitation serveur Microsoft version 21H2 (x64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_MSOS_X64_21H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_MSOS_X64_21H2`()
BEGIN


DROP TABLE IF EXISTS up_packages_MSOS_X64_21H2;
-- création table up_packages_MSOS_X64_21H2
CREATE TABLE up_packages_MSOS_X64_21H2 AS
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
		aa.title LIKE '%Microsoft server operating system version 21H2%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_22H2
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_22H2
-- Description :
--   Cette procédure initialise la table `up_packages_MSOS_X64_22H2` en extrayant
--   les mises à jour spécifiques au **système d'exploitation serveur Microsoft
--   version 22H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prépare les données nécessaires pour le déploiement des packages
--   liés à cette version du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_22H2` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 22H2".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques au **système d'exploitation serveur Microsoft version 22H2 (x64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_MSOS_X64_22H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_MSOS_X64_22H2`()
BEGIN

DROP TABLE IF EXISTS up_packages_MSOS_X64_22H2;
-- creation table up_packages_MSOS_X64_22H2
CREATE TABLE up_packages_MSOS_X64_22H2 AS
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
		aa.title LIKE '%Microsoft server operating system version 22H2%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_23H2
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- création table up_packages_MSOS_X64_23H2

-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_23H2
-- Description :
--   Cette procédure initialise la table `up_packages_MSOS_X64_23H2` en extrayant
--   les mises à jour spécifiques au **système d'exploitation serveur Microsoft
--   version 23H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prépare les données nécessaires pour le déploiement des packages
--   liés à cette version du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_23H2` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 23H2".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques au **système d'exploitation serveur Microsoft version 23H2 (x64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_MSOS_X64_23H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_MSOS_X64_23H2`()
BEGIN


DROP TABLE IF EXISTS up_packages_MSOS_X64_23H2;
CREATE TABLE up_packages_MSOS_X64_23H2 AS
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
		aa.title LIKE '%Microsoft server operating system version 23H2%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_24H2
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_24H2
-- Description :
--   Cette procédure initialise la table `up_packages_MSOS_X64_24H2` en extrayant
--   les mises à jour spécifiques au **système d'exploitation serveur Microsoft
--   version 24H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prépare les données nécessaires pour le déploiement des packages
--   liés à cette version du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_24H2` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 24H2".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques au **système d'exploitation serveur Microsoft version 24H2 (x64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_MSOS_X64_24H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_MSOS_X64_24H2`()
BEGIN


DROP TABLE IF EXISTS up_packages_MSOS_X64_24H2;
-- création table up_packages_MSOS_X64_24H2
CREATE TABLE up_packages_MSOS_X64_24H2 AS
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
		aa.title LIKE '%Microsoft server operating system version 24H2%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2003
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2003
-- Description :
--   Cette procédure initialise la table `up_packages_WS_X64_2003` en extrayant
--   les mises à jour spécifiques à **Windows Server 2003 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle prépare les données nécessaires pour le déploiement
--   des packages liés à cette version du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_WS_X64_2003` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2003".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques à **Windows Server 2003 (x64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_server_WS_X64_2003`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_WS_X64_2003`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_WS_X64_2003`()
BEGIN

DROP TABLE IF EXISTS up_packages_WS_X64_2003;
-- création table up_packages_WS_X64_2003  Server windows
CREATE TABLE up_packages_WS_X64_2003 AS
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
		aa.title LIKE '%Windows Server 2003%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2008
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2008
-- Description :
--   Cette procédure initialise la table `up_packages_WS_X64_2008` en extrayant
--   les mises à jour spécifiques à **Windows Server 2008 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle prépare les données nécessaires pour le déploiement
--   des packages liés à cette version du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_WS_X64_2008` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2008".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques à **Windows Server 2008 (x64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_server_WS_X64_2008`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_WS_X64_2008`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_WS_X64_2008`()
BEGIN

DROP TABLE IF EXISTS up_packages_WS_X64_2008;
-- création table up_packages_WS_X64_2008 serveur window
CREATE TABLE up_packages_WS_X64_2008 AS
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
		aa.title LIKE '%Windows Server 2008%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2012
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2012
-- Description :
--   Cette procédure initialise la table `up_packages_WS_X64_2012` en extrayant
--   les mises à jour spécifiques à **Windows Server 2012 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle prépare les données nécessaires pour le déploiement
--   des packages liés à cette version du système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_WS_X64_2012` si elle existe déjà.
--   - Crée une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2012".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table résultante est conçue pour faciliter la gestion des mises à jour
--     spécifiques à **Windows Server 2012 (x64)**.
--   - Les critères de filtrage garantissent que seuls les packages pertinents
--     sont inclus dans la table finale.
-- =====================================================================


USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_server_WS_X64_2012`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_WS_X64_2012`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_WS_X64_2012`()
BEGIN

DROP TABLE IF EXISTS up_packages_WS_X64_2012;
-- création table up_packages_WS_X64_2012 serveur windows
CREATE TABLE up_packages_WS_X64_2012 AS
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
		aa.title LIKE '%Windows Server 2012%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2016
-- =====================================================================
-- =====================================================================
-- =====================================================================

-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2016
-- Description :
--   Cette procédure initialise la table `up_packages_WS_X64_2016` en extrayant
--   les mises à jour spécifiques à **Windows Server 2016 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle permet de préparer les données nécessaires
--   pour le déploiement des packages liés à cette version de système d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table `up_packages_WS_X64_2016` si elle existe déjà.
--   - Crée une nouvelle table à partir d'une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), où `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2016".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Métadonnées : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de déploiement : `deploymentaction`, `title_short`, etc.
--
-- Remarques :
--   - La table générée est optimisée pour les déploiements de mises à jour
--     spécifiques à **Windows Server 2016 (x64)**.
--   - Les données sont filtrées pour garantir leur pertinence par rapport à
--     cette version et architecture.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_server_WS_X64_2016`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_WS_X64_2016`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_WS_X64_2016`()
BEGIN

DROP TABLE IF EXISTS up_packages_WS_X64_2016;
-- création table up_packages_WS_X64_2016 serveur windows
CREATE TABLE up_packages_WS_X64_2016 AS
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
		aa.title LIKE '%Windows Server 2016%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2019
-- =====================================================================
-- =====================================================================
-- =====================================================================

-- =====================================================================
-- PROCEDURE : up_init_packages_server_WS_X64_2019
-- Description :
--   Cette procédure initialise la table `up_packages_WS_X64_2019` en sélectionnant
--   les mises à jour spécifiques à **Windows Server 2019 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle filtre les données pour ne conserver que les
--   packages pertinents pour cette version et architecture.
--
-- Fonctionnement :
--   - Supprime la table existante si elle existe.
--   - Crée une nouvelle table `up_packages_WS_X64_2019` à partir d'une jointure
--     entre `update_data` (alias `aa`) et `update_data` (alias `bb`), où :
--     * `bb.bundledby_revision` correspond à `aa.revisionid`.
--   - Applique des filtres stricts sur :
--     * Le titre (`title`) contenant "Windows Server 2019".
--     * La famille de produit (`productfamily`) égale à "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes sélectionnées :
--   - Informations générales : `updateid`, `revisionid`, `creationdate`, `compagny`, etc.
--   - Détails techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Métadonnées de déploiement : `deploymentaction`, `title_short`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--
-- Remarques :
--   - La table résultante est optimisée pour les déploiements de mises à jour
--     spécifiques à **Windows Server 2019 (x64)**.
--   - Les données sont extraites en fonction des critères de filtrage définis.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_WS_X64_2019`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_WS_X64_2019`()
BEGIN

DROP TABLE IF EXISTS up_packages_WS_X64_2019;
-- création table up_packages_WS_X64_2019 serveur windows
CREATE TABLE up_packages_WS_X64_2019 AS
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
		aa.title LIKE '%Windows Server 2019%'
        AND aa.productfamily LIKE 'Windows'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : up_create_product_tables
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- USE `xmppmaster`;
-- DROP procedure IF EXISTS `xmppmaster`.`up_create_product_tables`;
-- ;
--
-- DELIMITER $$
-- USE `xmppmaster`$$
-- CREATE PROCEDURE `up_create_product_tables`()
-- BEGIN
-- 	-- Generation des tables de mise à jour produits
--     -- office mise à jour
--
--     -- =====================================================================
--     -- PROCEDURE : up_create_product_tables
--     -- Description :
--     --   Cette procédure permet de générer les tables de packages pour les produits
--     --   Microsoft (Office, Visual Studio, Windows, Windows Server, et mises à jour
--     --   de sécurité). Elle appelle une série de procédures dédiées pour initialiser
--     --   les packages correspondants dans la base de données.
--     --
--     -- PROCEDURES appelées :
--     --   - Office (2003 à 2016, 64 bits)
--     --   - Visual Studio (2005 à 2022)
--     --   - Windows 10 (versions 1903, 21H1, 21H2, 22H2)
--     --   - Windows 11 (versions 21H2, 22H2, 23H2, 24H2)
--     --   - Mises à jour de sécurité (Malicious X64)
--     --   - Windows Server (versions 21H2 à 24H2, x64 et ARM64)
--     --   - Anciens serveurs Windows (2012, 2016, 2019)
--     --
--     -- Remarques :
--     --   - Les procédures pour les anciens serveurs (2003, 2008) sont commentées
--     --     et non exécutées.
--     --   - Après l'exécution, les produits sont référencés dans la table
--     --     `up_list_produit` avec un statut initial désactivé (`enable = 0`).
--     --   - Chaque procédure appelée est responsable de la création des packages
--     --     spécifiques à sa version de produit.
--     --
--     -- Tables impactées :
--     --   - Tables de packages générées par les procédures appelées.
--     --   - `up_list_produit` : insertion des produits référencés.
--     -- =====================================================================
--     call up_init_packages_office_2003_64bit();
--     call up_init_packages_office_2007_64bit();
--     call up_init_packages_office_2010_64bit();
--     call up_init_packages_office_2013_64bit();
--     call up_init_packages_office_2016_64bit();
--
--     -- visual studio mise à jour
--     call up_init_packages_Vstudio_2005();
--     call up_init_packages_Vstudio_2008();
--     call up_init_packages_Vstudio_2010();
--     call up_init_packages_Vstudio_2012();
--     call up_init_packages_Vstudio_2013();
--     call up_init_packages_Vstudio_2015();
--     call up_init_packages_Vstudio_2017();
--     call up_init_packages_Vstudio_2019();
--     call up_init_packages_Vstudio_2022();
--
--     -- Operating system
--     -- WIN 10 mise à jour
--     call up_init_packages_Win10_X64_1903();
--     call up_init_packages_Win10_X64_21H2();
--     call up_init_packages_Win10_X64_21H1();
--     call up_init_packages_Win10_X64_22H2();
--
--     -- Win 11 mise à jour
--     call up_init_packages_Win11_X64();
--     call up_init_packages_Win11_X64_21H2();
--     call up_init_packages_Win11_X64_22H2();
--     call up_init_packages_Win11_X64_23H2();
--     call up_init_packages_Win11_X64_24H2();
--
--     -- securité mise à jour
--     call up_init_packages_Win_Malicious_X64();
--
--     -- SERVER mise à jour
--     call up_init_packages_server_MSOS_X64_21H2();
--     call up_init_packages_server_MSOS_X64_22H2();
--     call up_init_packages_server_MSOS_X64_23H2();
--     call up_init_packages_server_MSOS_X64_24H2();
--     call up_init_packages_server_MSOS_ARM64_24H2();
--
--         -- OLD SERVEUR WINDOWS
--
--         -- call up_init_packages_server_WS_X64_2003();
--         -- call up_init_packages_server_WS_X64_2008();
--         call up_init_packages_server_WS_X64_2012();
--         call up_init_packages_server_WS_X64_2016();
--         call up_init_packages_server_WS_X64_2019();
-- END$$
--
-- DELIMITER ;
-- ;
/*
-- prise en compte  produit
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_21H2','0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_22H2','0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_23H2','0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_24H2','0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_ARM64_24H2','0');*/




-- =====================================================================
-- =====================================================================
-- =====================================================================
-- PROCEDURE : move_update_to_white_list
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================

-- PROCEDURE : move_update_to_white_list
-- Paramètres :
--   - p_entity_id (INT) : Identifiant de l'entité concernée.
--
-- Description :
--   Cette procédure est appelée par le trigger `up_auto_approve_rules_AFTER_UPDATE`.
--   Elle parcourt les mises à jour présentes dans la table `up_gray_list`
--   pour une entité donnée, vérifie si elles correspondent à une règle
--   d’approbation automatique définie dans `up_auto_approve_rules`, et si
--   c’est le cas, elle les insère dans la `up_white_list`.
--
-- Tables impactées :
--   - xmppmaster.up_gray_list : source des mises à jour candidates.
--   - xmppmaster.update_data : permet de récupérer la sévérité (msrcseverity)
--     et la classification (updateclassification) associées à une mise à jour.
--   - xmppmaster.up_auto_approve_rules : contient les règles d’approbation
--     automatique (actives) propres à une entité.
--   - xmppmaster.up_white_list : destination des mises à jour validées par
--     les règles.
--
-- Logique de traitement :
--   1. Parcours des mises à jour de `up_gray_list` pour l’entité.
--   2. Pour chaque mise à jour :
--      * Récupération de ses attributs (sévérité et classification).
--      * Vérification de l’existence d’une règle active applicable
--        (même sévérité et/ou classification, ou règle générique).
--   3. Si au moins une règle correspondante existe :
--      * Insertion de la mise à jour dans `up_white_list` (via `INSERT IGNORE`
--        pour éviter les doublons).
--
-- Remarque :
--   Cette procédure automatise le passage de mises à jour de la "gray list"
--   vers la "white list" lorsqu’elles sont couvertes par des règles
--   d’approbation automatique, garantissant un déploiement simplifié et
--   cohérent au niveau de l’entité.
--   La suppression de la mise à jour dans `up_gray_list` est assurée
--       automatiquement par un **trigger associé à la table `up_white_list`**
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `move_update_to_white_list`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`move_update_to_white_list`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `move_update_to_white_list`(IN p_entity_id INT)
BEGIN

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
        FROM xmppmaster.up_gray_list
        WHERE entityid = p_entity_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_updateid, v_kb, v_title, v_description, v_title_short, v_valided;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Cherche une règle applicable pour cette entité
        SELECT msrcseverity, updateclassification
        INTO v_msrcseverity, v_updateclassification
        FROM xmppmaster.update_data
        WHERE updateid = v_updateid
        LIMIT 1;

        SELECT COUNT(*) INTO v_exists_rule
        FROM xmppmaster.up_auto_approve_rules
        WHERE entityid = p_entity_id
          AND (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
          AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
          AND active_rule = 1;

        -- On copie dans la white_list avec l’entityid
        IF v_exists_rule > 0 THEN
            INSERT IGNORE INTO xmppmaster.up_white_list (
                updateid, kb, title, description, title_short, valided, entityid
            ) VALUES (
                v_updateid, v_kb, v_title, v_description, v_title_short, v_valided, p_entity_id
            );
        END IF;
    END LOOP;
    CLOSE cur;
END$$

DELIMITER ;
;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_auto_approve_rules_AFTER_UPDATE
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Passe l'entityid de la ligne mise à jour à la procédure

-- =====================================================================
-- Trigger : up_auto_approve_rules_AFTER_UPDATE
-- Événement : AFTER UPDATE sur la table xmppmaster.up_auto_approve_rules
--
-- Description :
--   Ce trigger est exécuté automatiquement après la mise à jour
--   d’une règle d’approbation automatique dans la table
--   `up_auto_approve_rules`.
--
-- Objectif :
--   - Transmettre l’identifiant de l’entité (`entityid`) de la règle
--     mise à jour à la procédure `move_update_to_white_list`.
--   - Cette procédure se charge ensuite de parcourir la `up_gray_list`
--     et de déplacer les mises à jour correspondant aux règles actives
--     vers la `up_white_list`.
--
-- Logique de traitement :
--   1. Détection de la mise à jour d’une règle dans `up_auto_approve_rules`.
--   2. Appel de la procédure `move_update_to_white_list(NEW.entityid)`.
--   3. La procédure applique les règles d’auto-approbation pour l’entité
--      et met à jour les listes (`gray_list` → `white_list`).
--
-- Impact :
--   Garantit que toute modification sur une règle d’auto-approbation est
--   immédiatement prise en compte pour l’entité correspondante, sans
--   intervention manuelle supplémentaire.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_auto_approve_rules_AFTER_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_auto_approve_rules_AFTER_UPDATE`
AFTER UPDATE ON `up_auto_approve_rules`
FOR EACH ROW
BEGIN

    CALL xmppmaster.move_update_to_white_list(NEW.entityid);
END$$
DELIMITER ;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_black_list_BEFORE_INSERT
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_black_list_BEFORE_INSERT
-- Description :
--   Ce trigger est exécuté avant l'insertion d'une nouvelle entrée dans
--   la table `up_black_list`. Il permet de :
--   1. Supprimer les entrées correspondantes dans la table `xmppmaster.deploy`
--      pour les déploiements en cours ou en attente, liés à l'entité et à l'ID
--      de mise à jour spécifiés dans la nouvelle entrée.
--   2. Mettre à jour la date de fin (`end_date`) des commandes associées dans
--      la table `msc.commands`, en les marquant comme obsolètes (55 minutes en arrière).
--
-- Tables impactées :
--   - xmppmaster.deploy : suppression des déploiements en cours ou en attente.
--   - msc.commands : mise à jour de la date de fin des commandes associées.
--
-- Conditions :
--   - Les déploiements supprimés doivent correspondre à :
--     * Un titre commençant par le label du package associé à l'ID de mise à jour.
--     * Une date de fin de commande (`endcmd`) postérieure à l'instant actuel.
--     * Un état (`state`) correspondant à "WOL 1", "WOL 2", "WOL 3",
--       "DEPLOYMENT START" ou "WAITING MACHINE ONLINE".
--     * Une entité (`entityid`) correspondant à celle de la nouvelle entrée.
--   - Les commandes mises à jour doivent correspondre à :
--     * Un `package_id` commençant par l'ID de mise à jour (`updateid_or_kb`).
--     * Un hôte (`target`) dont l'identifiant inventaire correspond à l'entité
--       de la nouvelle entrée, ce qui est déterminé par :
--          SUBSTRING(target.target_uuid, 5) = NEW.entityid
--
-- Remarque :
--   Ce trigger est conçu pour éviter les conflits ou les doublons lors de
--   l'ajout d'une entrée dans la liste noire des mises à jour.
--   Il supprime ainsi les mises à jour interdites et invalide les commandes
--   déjà programmées ou en cours pour la même entité.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_BEFORE_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_black_list_BEFORE_INSERT`
BEFORE INSERT ON `up_black_list`
FOR EACH ROW
BEGIN

    DELETE
    FROM xmppmaster.deploy
    WHERE xmppmaster.deploy.id IN (
        SELECT t1.id
        FROM xmppmaster.deploy t1
        JOIN pkgs.packages t2
          ON t1.title LIKE CONCAT(t2.label, '%')
        WHERE t2.uuid = NEW.updateid_or_kb
          AND t1.endcmd > NOW()
          AND t1.state REGEXP 'WOL 1|WOL 2|WOL 3|DEPLOYMENT START|WAITING MACHINE ONLINE'
          AND SUBSTRING(t1.inventoryuuid, 5) = NEW.entityid
    );


    UPDATE msc.commands c
    INNER JOIN msc.commands_on_host coh ON coh.fk_commands = c.id
    INNER JOIN msc.target t ON t.id = coh.fk_target
    SET c.end_date = DATE_SUB(NOW(), INTERVAL 55 MINUTE)
    WHERE c.package_id LIKE NEW.updateid_or_kb
      AND SUBSTRING(t.target_uuid, 5) = NEW.entityid;
END$$
DELIMITER ;



-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_black_list_AFTER_INSERT
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_black_list_AFTER_INSERT
-- Description :
--   Ce trigger est exécuté après l'insertion d'une nouvelle entrée dans
--   la table `up_black_list`. Il permet de synchroniser et nettoyer les
--   listes de mises à jour (gray list, white list et flop) afin d’éviter
--   les conflits, doublons ou exécutions non souhaitées.
--
-- Tables impactées :
--   - xmppmaster.up_gray_list :
--       * Suppression des entrées correspondant à l’ID ou au KB de la mise
--         à jour nouvellement blacklistée.
--   - xmppmaster.up_gray_list_flop :
--       * Mise à jour temporaire des entrées liées à une mise à jour
--         blacklistée (remplacement par des valeurs "bidon").
--       * Suppression des entrées "bidon" pour nettoyer la table.
--   - xmppmaster.up_white_list :
--       * Suppression des entrées liées à la mise à jour blacklistée.
--
-- Conditions :
--   - Pour le type "id" :
--       * Les entrées gray list / flop sont ciblées sur la colonne `updateid`
--         correspondant au champ `updateid_or_kb` de la nouvelle entrée.
--   - Pour le type "kb" :
--       * Les entrées gray list / flop sont ciblées sur la colonne `kb`
--         correspondant au champ `updateid_or_kb` de la nouvelle entrée.
--   - Dans tous les cas, le filtre se fait aussi sur `entityid = NEW.entityid`.
--
-- Remarque :
--   Ce trigger assure qu’une mise à jour nouvellement blacklistée est
--   immédiatement retirée des listes de gestion (`gray_list`, `white_list`)
--   et neutralisée dans la `gray_list_flop`.
--   Il garantit ainsi la cohérence des règles de déploiement et empêche
--   toute exécution indésirable d’une mise à jour interdite.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`up_black_list_AFTER_INSERT` AFTER INSERT ON `up_black_list` FOR EACH ROW
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
    SET `updateid` = LEFT(UUID(), 8),
        `kb` = 'bidon'
    WHERE entityid = NEW.entityid
      AND `updateid` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'id'
      );
    DELETE FROM `xmppmaster`.`up_gray_list`
    WHERE entityid = NEW.entityid
      AND `kb` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'kb'
      );
    UPDATE `xmppmaster`.`up_gray_list_flop`
    SET `kb` = 'bidon'
    WHERE entityid = NEW.entityid
      AND `updateid` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'kb'
      );
 DELETE FROM `xmppmaster`.`up_white_list`
     WHERE entityid = NEW.entityid
       AND (`updateid` = NEW.updateid_or_kb OR `kb` = NEW.updateid_or_kb);
     DELETE FROM `xmppmaster`.`up_gray_list_flop`
    WHERE entityid = NEW.entityid
      AND (`kb` = 'bidon');
END$$
DELIMITER ;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_black_list_AFTER_UPDATE
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_black_list_AFTER_UPDATE
-- Description :
--   Ce trigger est exécuté après la mise à jour d'une entrée dans la table
--   `up_black_list`. Il assure la synchronisation des listes de mises à jour
--   afin que toute modification de règle de blacklist soit immédiatement
--   répercutée dans les tables associées (`gray_list`, `gray_list_flop`).
--
-- Tables impactées :
--   - xmppmaster.up_gray_list :
--       * Suppression des entrées correspondant à l’ID ou au KB de la mise
--         à jour désormais blacklistée.
--   - xmppmaster.up_gray_list_flop :
--       * Mise à jour des entrées correspondantes avec des valeurs neutres
--         (remplacement `updateid` par une UUID tronquée, `kb` = 'bidon').
--       * Suppression des entrées marquées "bidon" pour nettoyer la table.
--
-- Conditions :
--   - Pour le type "id" :
--       * Les entrées gray list / flop sont ciblées sur la colonne `updateid`
--         correspondant au champ `updateid_or_kb` de la ligne mise à jour.
--   - Pour le type "kb" :
--       * Les entrées gray list / flop sont ciblées sur la colonne `kb`
--         correspondant au champ `updateid_or_kb` de la ligne mise à jour.
--   - Dans tous les cas, le filtre s’applique aussi sur `entityid = NEW.entityid`.
--
-- Remarque :
--   Ce trigger garantit qu'une modification d'une règle de blacklist est
--   immédiatement appliquée aux listes associées, empêchant toute exécution
--   future d'une mise à jour interdite et assurant la cohérence des données.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_AFTER_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_black_list_AFTER_UPDATE` AFTER UPDATE ON `up_black_list` FOR EACH ROW
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
    -- Mise à jour flop par updateid
    UPDATE `xmppmaster`.`up_gray_list_flop`
    SET `updateid` = LEFT(UUID(), 8),
        `kb` = 'bidon'
    WHERE entityid = NEW.entityid
      AND `updateid` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'id'
      );

    -- Suppression dans la gray list par kb
    DELETE FROM `xmppmaster`.`up_gray_list`
    WHERE entityid = NEW.entityid
      AND `kb` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'kb'
      );
    -- Mise à jour flop par kb
    UPDATE `xmppmaster`.`up_gray_list_flop`
    SET `kb` = 'bidon'
    WHERE entityid = NEW.entityid
      AND `updateid` IN (
            SELECT updateid_or_kb
            FROM xmppmaster.up_black_list
            WHERE entityid = NEW.entityid
              AND userjid_regexp = '.*'
              AND type_rule = 'kb'
      );
    -- Suppression des "bidons"
    DELETE FROM `xmppmaster`.`up_gray_list_flop`
    WHERE entityid = NEW.entityid
      AND (`kb` = 'bidon');
END$$
DELIMITER ;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_AFTER_INSERT
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_AFTER_INSERT
-- Description :
--   Ce trigger est exécuté après l'insertion d'une nouvelle entrée dans la table
--   `up_gray_list`. Il gère l'ajout de commandes de mise à jour et vérifie si
--   l'entrée doit être automatiquement approuvée selon des règles prédéfinies.
--
-- Fonctionnement :
--   - Construit une commande pour le script `medulla_mysql_exec_update.sh` avec le `updateid`.
--   - Insère une action dans `up_action_update_packages` pour déclencher la commande.
--   - Enregistre un log dans la table `logs` pour tracer la création de la commande.
--   - Récupère les métadonnées (`msrcseverity`, `updateclassification`) depuis `update_data`.
--   - Vérifie si une règle d'approbation automatique (`up_auto_approve_rules`) s'applique :
--     * La règle doit être active (`active_rule = 1`).
--     * La règle doit correspondre aux métadonnées récupérées ou être générique (valeur NULL).
--   - Si une règle est trouvée, insère l'entrée dans `pending_events` pour traitement ultérieur.
--
-- Tables impactées :
--   - `up_action_update_packages` : insertion de commandes de mise à jour.
--   - `logs` : insertion de logs pour tracer les actions effectuées.
--   - `pending_events` : insertion des entrées approuvées automatiquement.
--
-- Remarques :
--   - Utilise `INSERT IGNORE` pour éviter les erreurs de doublons.
--   - Les logs sont détaillés pour assurer une traçabilité complète des actions.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_gray_list_AFTER_INSERT`
AFTER INSERT ON xmppmaster.`up_gray_list`
FOR EACH ROW
BEGIN

    DECLARE v_msrcseverity VARCHAR(255);
    DECLARE v_updateclassification VARCHAR(255);
    DECLARE v_exists_rule INT DEFAULT 0;
    DECLARE v_logtext VARCHAR(500);
    DECLARE v_cmd VARCHAR(500);

    -- Construction de la commande
    SET v_cmd = CONCAT("/usr/sbin/medulla_mysql_exec_update.sh ", NEW.updateid, " c");

    -- Ajout action (lié à entityid)
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` ( `action`, `packages`, `option`)
    VALUES ( v_cmd, NEW.updateid, "-c");

    -- Log
    SET v_logtext = CONCAT("Creation command : ", v_cmd);
    INSERT INTO `xmppmaster`.`logs` ( `type`, `module`, `text`, `fromuser`, `touser`, `action`,
                                     `sessionname`, `how`, `why`, `priority`, `who`)
    VALUES ('automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_INSERT', 'medulla',
            'creation', NEW.updateid, 'auto', 'mariadb', '-1', 'system');

    -- Récupération des métadonnées update
    SELECT msrcseverity, updateclassification
    INTO v_msrcseverity, v_updateclassification
    FROM xmppmaster.update_data
    WHERE updateid = NEW.updateid
    LIMIT 1;

    -- Vérification auto-approve rules
    SELECT COUNT(*)
    INTO v_exists_rule
    FROM xmppmaster.up_auto_approve_rules
    WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
      AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
      AND active_rule = 1
      AND entityid = NEW.entityid;
    -- Si règle trouvée → ajout à pending_events
    IF v_exists_rule > 0 THEN
        INSERT IGNORE INTO xmppmaster.pending_events (
                                                      updateid,
                                                      kb,
                                                      title,
                                                      description,
                                                      title_short,
                                                      valided)
        VALUES (
                NEW.updateid,
                NEW.kb,
                NEW.title,
                NEW.description,
                NEW.title_short,
                NEW.valided );
    END IF;
END$$
DELIMITER ;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_AFTER_DELETE
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_AFTER_DELETE
-- Description :
--   Ce trigger est exécuté après la suppression d'une entrée dans la table
--   `up_gray_list`. Il gère la suppression des packages en fonction de leur
--   présence dans la liste blanche (`up_white_list`) et de leur type (UUID ou non).
--
-- Fonctionnement :
--   - Déclare des variables pour stocker la commande, le texte de log, et un booléen
--     indiquant si le package est en liste blanche.
--   - Construit une commande de suppression pour le script `medulla_mysql_exec_update.sh`.
--   - Vérifie si le `updateid` supprimé est présent dans la liste blanche pour la même `entityid`.
--   - Si le package n'est pas en liste blanche :
--     * Insère une commande dans `up_action_update_packages` pour suppression.
--     * Enregistre un log dans la table `logs` pour tracer la création de la commande.
--   - Si le `updateid` est un UUID (longueur = 36) :
--     * Enregistre un log pour indiquer le recyclage dans `up_gray_list_flop`.
--     * Insère l'entrée supprimée dans `up_gray_list_flop` pour conservation.
--   - Si le `updateid` n'est pas un UUID :
--     * Enregistre un log pour indiquer la suppression définitive du package.
--
-- Tables impactées :
--   - `up_action_update_packages` : insertion de commandes de suppression.
--   - `logs` : insertion de logs pour tracer les actions effectuées.
--   - `up_gray_list_flop` : insertion des entrées recyclées (UUID uniquement).
--
-- Remarques :
--   - Utilise `INSERT IGNORE` pour éviter les erreurs de doublons.
--   - Les logs sont détaillés pour assurer une traçabilité complète des actions.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`up_gray_list_AFTER_DELETE` AFTER DELETE ON `up_gray_list` FOR EACH ROW
BEGIN

    DECLARE v_updatidpackage BOOLEAN DEFAULT FALSE;
    DECLARE v_cmd VARCHAR(500);
    DECLARE v_logtext VARCHAR(500);
    -- Construction commande suppression
    SET v_cmd = CONCAT("/usr/sbin/medulla_mysql_exec_update.sh ", OLD.updateid, " s");

    -- Vérifie si updateid est en whitelist (même entityid)
    SELECT TRUE INTO v_updatidpackage
    FROM `xmppmaster`.`up_white_list`
    WHERE updateid = OLD.updateid
      AND entityid = OLD.entityid
    LIMIT 1;

    -- Si non whitelist → enregistrement commande & log
    IF v_updatidpackage IS NULL OR v_updatidpackage = FALSE THEN
        INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` (`action`, `packages`, `option`)
        VALUES ( v_cmd, OLD.updateid, "-c");

        SET v_logtext = CONCAT("Creation command : ", v_cmd);
        INSERT IGNORE INTO `xmppmaster`.`logs` ( `type`, `module`, `text`, `fromuser`, `touser`,
                                                `action`, `sessionname`, `how`, `why`, `priority`, `who`)
        VALUES ( 'automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_DELETE',
                'medulla', 'delete', OLD.updateid, 'auto', 'mariadb', '-1', 'system');
    END IF;

    -- Si UUID → recyclage flop
    IF LENGTH(OLD.updateid) = 36 THEN
        SET v_logtext = CONCAT("replace dans la table up_gray_list_flop package : ", OLD.updateid);
        INSERT IGNORE INTO `xmppmaster`.`logs` ( `type`, `module`, `text`, `fromuser`, `touser`,
                                                `action`, `sessionname`, `how`, `why`, `priority`, `who`)
        VALUES ( 'automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_DELETE',
                'medulla', 'delete', OLD.updateid, 'auto', 'mariadb', '-1', 'system');

        INSERT IGNORE INTO `xmppmaster`.`up_gray_list_flop` (`entityid`,
                                                             `updateid`,
                                                             `kb`,
                                                             `revisionid`,
                                                             `title`,
                                                             `description`,
                                                             `updateid_package`,
                                                             `payloadfiles`,
                                                             `supersededby`,
                                                             `creationdate`,
                                                             `title_short`,
                                                             `valided`,
                                                             `validity_date`)
        VALUES (OLD.entityid,
                OLD.updateid,
                OLD.kb,
                OLD.revisionid,
                OLD.title,
                OLD.description,
                OLD.updateid_package,
                OLD.payloadfiles,
                OLD.supersededby,
                OLD.creationdate,
                OLD.title_short,
                OLD.valided,
                OLD.validity_date);
    ELSE
        -- Sinon suppression définitive
        SET v_logtext = CONCAT("Suppression definitive package : ", OLD.updateid);
        INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`,
                                         `action`, `sessionname`, `how`, `why`, `priority`, `who`)
        VALUES ( 'automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_DELETE',
                'medulla', 'delete', OLD.updateid, 'auto', 'mariadb', '-1', 'system');
    END IF;
END$$
DELIMITER ;




-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_AFTER_INSERT
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_AFTER_INSERT
-- Description :
--   Ce trigger est exécuté après l'insertion d'une nouvelle entrée dans la table
--   `up_gray_list`. Il gère l'ajout de commandes de mise à jour et vérifie si
--   l'entrée doit être automatiquement approuvée selon des règles prédéfinies.
--
-- Fonctionnement :
--   - Construit une commande pour le script `medulla_mysql_exec_update.sh` avec le `updateid`.
--   - Insère une action dans `up_action_update_packages` pour déclencher la commande.
--   - Enregistre un log dans la table `logs` pour tracer la création de la commande.
--   - Récupère les métadonnées (`msrcseverity`, `updateclassification`) depuis `update_data`.
--   - Vérifie si une règle d'approbation automatique (`up_auto_approve_rules`) s'applique :
--     * La règle doit être active (`active_rule = 1`).
--     * La règle doit correspondre aux métadonnées récupérées ou être générique (valeur NULL).
--   - Si une règle est trouvée, insère l'entrée dans `pending_events` pour traitement ultérieur.
--
-- Tables impactées :
--   - `up_action_update_packages` : insertion de commandes de mise à jour.
--   - `logs` : insertion de logs pour tracer les actions effectuées.
--   - `pending_events` : insertion des entrées approuvées automatiquement.
--
-- Remarques :
--   - Utilise `INSERT IGNORE` pour éviter les erreurs de doublons.
--   - Les logs sont détaillés pour assurer une traçabilité complète des actions.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`up_gray_list_AFTER_INSERT`
AFTER INSERT ON xmppmaster.`up_gray_list`
FOR EACH ROW
BEGIN

    DECLARE v_msrcseverity VARCHAR(255);
    DECLARE v_updateclassification VARCHAR(255);
    DECLARE v_exists_rule INT DEFAULT 0;
    DECLARE v_logtext VARCHAR(500);
    DECLARE v_cmd VARCHAR(500);

    -- Construction de la commande
    SET v_cmd = CONCAT("/usr/sbin/medulla_mysql_exec_update.sh ", NEW.updateid, " c");

    -- Ajout action (lié à entityid)
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` ( `action`, `packages`, `option`)
    VALUES ( v_cmd, NEW.updateid, "-c");

    -- Log
    SET v_logtext = CONCAT("Creation command : ", v_cmd);
    INSERT INTO `xmppmaster`.`logs` ( `type`, `module`, `text`, `fromuser`, `touser`, `action`,
                                     `sessionname`, `how`, `why`, `priority`, `who`)
    VALUES ('automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_INSERT', 'medulla',
            'creation', NEW.updateid, 'auto', 'mariadb', '-1', 'system');

    -- Récupération des métadonnées update
    SELECT msrcseverity, updateclassification
    INTO v_msrcseverity, v_updateclassification
    FROM xmppmaster.update_data
    WHERE updateid = NEW.updateid
    LIMIT 1;

    -- Vérification auto-approve rules
    SELECT COUNT(*)
    INTO v_exists_rule
    FROM xmppmaster.up_auto_approve_rules
    WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
      AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
      AND active_rule = 1
      AND entityid = NEW.entityid;
    -- Si règle trouvée → ajout à pending_events
    IF v_exists_rule > 0 THEN
        INSERT IGNORE INTO xmppmaster.pending_events (
                                                      updateid,
                                                      kb,
                                                      title,
                                                      description,
                                                      title_short,
                                                      valided)
        VALUES (
                NEW.updateid,
                NEW.kb,
                NEW.title,
                NEW.description,
                NEW.title_short,
                NEW.valided );
    END IF;
END$$
DELIMITER ;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_flop_AFTER_DELETE
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_gray_list_flop_AFTER_DELETE
-- Événement : AFTER DELETE sur la table xmppmaster.up_gray_list_flop
--
-- Description :
--   Ce trigger est exécuté après la suppression d'une entrée dans la table
--   `up_gray_list_flop`. Il gère la réinjection des entrées supprimées dans
--   `up_gray_list` si l'`updateid` est un UUID de longeur 36. on modifie updateid a bidon avant la
--   suppression cela empeche la recopie dans  tale flop car uuid incorrect.
--
-- Logique de traitement :
--   1. Si l’`updateid` a une longueur de 36 caractères :
--       * Génération d’un log de réinjection dans la table `logs`.
--       * Réinsertion de la mise à jour dans la table `up_gray_list` pour
--         la même entité (`entityid`), avec une `validity_date` étendue
--         de 10 jours.
--       * Si l’entrée existe déjà, mise à jour de la `validity_date`.
--   2. Si l’`updateid` n’a pas 36 caractères :
--       * Génération d’un log indiquant la suppression définitive dans
--         la table `logs`.
--
-- Tables impactées :
--   - xmppmaster.up_gray_list_flop : table déclencheur (ligne supprimée).
--   - xmppmaster.up_gray_list : réinsertion des mises à jour valides.
--   - xmppmaster.logs : journalisation de la suppression ou réinsertion.
--
-- Remarque :
--   Ce trigger assure que les mises à jour importantes (UUID de 36 caractères)
--   ne sont pas perdues et sont réinsérées automatiquement dans la
--   `up_gray_list`, tandis que les mises à jour mineures ou invalides
--   sont simplement consignées dans les logs avant suppression définitive.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_flop_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`up_gray_list_flop_AFTER_DELETE` AFTER DELETE ON `up_gray_list_flop` FOR EACH ROW
BEGIN


	   IF LENGTH(OLD.updateid) = 36 THEN
        -- Log de réinjection
        SET @logtext = CONCAT("replace dans la table up_gray_list update : ", OLD.updateid);
        INSERT INTO `xmppmaster`.`logs` (
                                         `type`,
                                         `module`,
                                         `text`,
                                         `fromuser`,
                                         `touser`,
                                         `action`,
                                         `sessionname`,
                                         `how`,
                                         `why`,
                                         `priority`,
                                         `who`)
        VALUES (
                'automate_Maria',
                'update',
                @logtext,
                'up_gray_list_flop_AFTER_DELETE',
                'medulla',
                'delete',
                OLD.updateid,
                'auto',
                'mariadb',
                '-1',
                'system');

        -- Réinsertion dans up_gray_list avec même entityid
        INSERT IGNORE INTO `xmppmaster`.`up_gray_list` (`entityid`,
                                                        `updateid`,
                                                        `kb`,
                                                        `revisionid`,
                                                        `title`,
                                                        `description`,
                                                        `updateid_package`,
                                                        `payloadfiles`,
                                                        `supersededby`,
                                                        `creationdate`,
                                                        `title_short`,
                                                        `valided`,
                                                        `validity_date`)
        VALUES (OLD.entityid,
                OLD.updateid,
                OLD.kb,
                OLD.revisionid,
                OLD.title,
                OLD.description,
                OLD.updateid_package,
                OLD.payloadfiles,
                OLD.supersededby,
                OLD.creationdate,
                OLD.title_short,
                OLD.valided,
                NOW() + INTERVAL 10 DAY)
        ON DUPLICATE KEY UPDATE validity_date = NOW() + INTERVAL 10 DAY;

    ELSE
        -- Log suppression définitive
        SET @logtext = CONCAT("supprime definitivement de la table up_gray_list_flop update : ", OLD.updateid);
        INSERT INTO `xmppmaster`.`logs` (
                                         `type`,
                                         `module`,
                                         `text`,
                                         `fromuser`,
                                         `touser`,
                                         `action`,
                                         `sessionname`,
                                         `how`,
                                         `why`,
                                         `priority`,
                                         `who`)
        VALUES (
                'automate_Maria',
                'update',
                @logtext,
                'up_gray_list_flop_AFTER_DELETE',
                'medulla',
                'delete',
                OLD.updateid,
                'auto',
                'mariadb',
                '-1',
                'system');
    END IF;
END$$
DELIMITER ;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_white_list_AFTER_INSERT
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_white_list_AFTER_INSERT
-- Description :
--   Ce trigger est exécuté après l'insertion d'une nouvelle entrée dans la table
--   `up_white_list`. Il garantit la cohérence des données en supprimant toute
--   entrée correspondante dans la table `up_gray_list`.
--
-- Fonctionnement :
--   - Supprime automatiquement les entrées de `up_gray_list` où :
--     * `updateid` correspond à celui de la nouvelle entrée en liste blanche.
--     * `entityid` correspond à celui de la nouvelle entrée en liste blanche.
--
-- Tables impactées :
--   - `up_gray_list` : suppression des entrées correspondantes.
--
-- Remarques :
--   - Assure que les packages approuvés (liste blanche) ne restent pas en
--     liste grise, évitant ainsi les conflits de gestion des mises à jour.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_white_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_white_list_AFTER_INSERT` AFTER INSERT ON `up_white_list` FOR EACH ROW
BEGIN

DELETE
    FROM xmppmaster.up_gray_list
    WHERE updateid = NEW.updateid
      AND entityid = NEW.entityid;
END$$
DELIMITER ;

-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_white_list_AFTER_DELETE
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- Trigger : up_white_list_AFTER_DELETE
-- Description :
--   Ce trigger est exécuté après la suppression d'une entrée dans la table
--   `up_white_list`. Il nettoie les entrées correspondantes dans la table
--   `up_gray_list_flop` pour maintenir la cohérence des données.
--
-- Fonctionnement :
--   - Supprime automatiquement les entrées de `up_gray_list_flop` où :
--     * `updateid` correspond à celui de l'entrée supprimée de la liste blanche.
--     * `entityid` correspond à celui de l'entrée supprimée de la liste blanche.
--
-- Tables impactées :
--   - `up_gray_list_flop` : suppression des entrées correspondantes.
--
-- Remarques :
--   - Permet de s'assurer que les entrées supprimées de la liste blanche ne
--     persistent pas dans la liste grise des échecs, évitant ainsi les incohérences.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_white_list_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`up_white_list_AFTER_DELETE`
AFTER DELETE ON `up_white_list`
FOR EACH ROW
BEGIN

    DELETE
    FROM xmppmaster.up_gray_list_flop
    WHERE updateid = OLD.updateid
      AND entityid = OLD.entityid;
END$$
DELIMITER ;


-- =====================================================================
-- =====================================================================
-- =====================================================================
-- VUE : up_machine_activated
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- =====================================================================
-- VUE : up_machine_activated
-- =====================================================================
-- Description :
--    Cette vue permet de lister les machines Windows activées pour les mises à jour,
--    en tenant compte des listes blanche (white list) et grise (gray list).
--    Elle fournit des informations sur les machines, leurs identifiants, leur statut de déploiement,
--    et leur appartenance à une liste (blanche ou grise).
--
-- Fonctionnement :
--    1. Jointure des tables :
--       - up_machine_windows (umw) : Contient les informations sur les mises à jour des machines Windows.
--       - machines (m) : Contient les informations générales sur les machines (UUID, hostname, JID).
--       - local_glpi_machines (lgm) : Contient les informations locales des machines (entités, statut de suppression, etc.).
--       - up_white_list (uwl) : Liste blanche des mises à jour validées.
--       - up_gray_list (ugl) : Liste grise des mises à jour validées.
--
--    2. Logique de sélection :
--       - Seules les machines non supprimées (lgm.is_deleted = 0) et non templates (lgm.is_template = 0) sont incluses.
--       - Seules les machines sous plateforme "Microsoft Windows" sont prises en compte.
--       - Les machines doivent être validées dans au moins une des listes (blanche ou grise).
--
--    3. Champs retournés :
--       - kb : Priorise la valeur de la liste grise (ugl.kb) si elle existe, sinon utilise la valeur de la liste blanche (uwl.kb).
--       - id_machine : Identifiant de la machine.
--       - glpi_id : Identifiant GLPI extrait de l'UUID de la machine.
--       - hostname : Nom d'hôte de la machine.
--       - jid : Identifiant JID de la machine.
--       - entities_id : Identifiant de l'entité associée à la machine.
--       - update_id : Identifiant de la mise à jour.
--       - curent_deploy : Déploiement actuel.
--       - required_deploy : Déploiement requis.
--       - start_date : Date de début de la mise à jour.
--       - end_date : Date de fin de la mise à jour.
--       - intervals : Intervalle de la mise à jour.
--       - msrcseverity : Niveau de sévérité MSRC.
--       - list : Indique si la machine est dans la liste blanche ("white") ou grise ("gray").
--
-- Remarques :
--    - Cette vue est utile pour identifier les machines éligibles aux mises à jour,
--      en fonction des règles définies dans les listes blanche et grise.
--    - Les machines sans entrée dans la liste grise (ugl.kb IS NULL) sont marquées comme "gray" par défaut.
--    - Assurez-vous que les tables sources sont à jour pour des résultats précis.
-- =====================================================================


USE `xmppmaster`;
CREATE  OR REPLACE
VIEW `up_machine_activated` AS
    SELECT
        CASE
            WHEN ugl.kb IS NULL THEN uwl.kb
            ELSE ugl.kb
        END AS kb,
        umw.id_machine AS id_machine,
        SUBSTR(m.uuid_inventorymachine, 5) AS glpi_id,
        m.hostname AS hostname,
        m.jid AS jid,
        lgm.entities_id AS entities_id,
        umw.update_id AS update_id,
        umw.curent_deploy AS curent_deploy,
        umw.required_deploy AS required_deploy,
        umw.start_date AS start_date,
        umw.end_date AS end_date,
        umw.intervals AS intervals,
        umw.msrcseverity AS msrcseverity,
        CASE
            WHEN uwl.kb IS NULL THEN 'gray'
            ELSE 'white'
        END AS list
    FROM
        up_machine_windows umw
        JOIN machines m ON m.id = umw.id_machine
        JOIN local_glpi_machines lgm ON CONCAT('UUID', lgm.id) = m.uuid_inventorymachine
        LEFT JOIN up_white_list uwl ON uwl.updateid = umw.update_id
        LEFT JOIN up_gray_list ugl ON ugl.updateid = umw.update_id
    WHERE
        (ugl.valided = 1 OR uwl.valided = 1)
        AND lgm.is_deleted = 0
        AND lgm.is_template = 0
        AND m.platform LIKE 'Microsoft Windows%';;



--
-- Table structure for table `up_packages_major_Lang_code`
--

DROP TABLE IF EXISTS `up_packages_major_Lang_code`;
CREATE TABLE `up_packages_major_Lang_code` (
  `major`  varchar(5) NOT NULL DEFAULT 11,
  `lang_code` varchar(10) NOT NULL,
  `num_code` varchar(6) NOT NULL,
  `country` varchar(45) NOT NULL,
  `enabled` tinyint(4) NOT NULL DEFAULT 0,
  `iso_filename` varchar(250) NOT NULL,
  `package_uuid` varchar(64) NOT NULL,
  PRIMARY KEY (`lang_code`,`major`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `up_packages_major_Lang_code` for windows 10
--
INSERT INTO up_packages_major_Lang_code (major, lang_code, num_code, country, enabled, iso_filename, package_uuid) VALUES
('10', 'ar-SA', '0401', 'Arabic', 0, 'Win10_22H2_Arabic_x64.iso', 'Win10upd_22H2_Arabicx64_pbqbowfj6h9l'),
('10', 'bg-BG', '0402', 'Bulgarian', 0, 'Win10_22H2_Bulgarian_x64.iso', 'Win10upd_22H2_Bulgarianx64_pbqbowfj6'),
('10', 'cs-CZ', '0405', 'Czech', 0, 'Win10_22H2_Czech_x64.iso', 'Win10upd_22H2_Czechx64_pbqbowfj6h9lo'),
('10', 'da-DK', '0406', 'Danish', 0, 'Win10_22H2_Danish_x64.iso', 'Win10upd_22H2_Danishx64_pbqbowfj6h9l'),
('10', 'de-DE', '0407', 'German', 0, 'Win10_22H2_German_x64.iso', 'Win10upd_22H2_Germanx64_pbqbowfj6h9l'),
('10', 'el-GR', '0408', 'Greek', 0, 'Win10_22H2_Greek_x64.iso', 'Win10upd_22H2_Greekx64_pbqbowfj6h9lo'),
('10', 'en-GB', '0809', 'English - United Kingdom', 1, 'Win10_22H2_English_x64.iso', 'Win10upd_22H2_Englishx64_pbqbowfj6h9'),
('10', 'en-US', '0409', 'English', 1, 'Win10_22H2_EnglishInternational_x64.iso', 'Win10upd_22H2_EnglishInternationalx6'),
('10', 'es-ES', '040A', 'Spanish', 0, 'Win10_22H2_Spanish_x64.iso', 'Win10upd_22H2_Spanishx64_pbqbowfj6h9'),
('10', 'es-MX', '080A', 'Spanish - Mexico', 0, 'Win10_22H2_Spanish_Mexico_x64.iso', 'Win10upd_22H2_Spanish_Mexicox64_pbqb'),
('10', 'et-EE', '0425', 'Estonian - Estonia', 0, 'Win10_22H2_Estonian_x64.iso', 'Win10upd_22H2_Estonianx64_pbqbowfj6h'),
('10', 'fi-FI', '040E', 'Finnish', 0, 'Win10_22H2_Finnish_x64.iso', 'Win10upd_22H2_Finnishx64_pbqbowfj6h9'),
('10', 'fr-CA', '0C0C', 'French - Canada', 0, 'Win10_22H2_FrenchCanadian_x64.iso', 'Win10upd_22H2_FrenchCanadianx64_pbqb'),
('10', 'fr-FR', '040C', 'French', 1, 'Win10_22H2_French_x64.iso', 'Win10upd_22H2_Frenchx64_pbqbowfj6h9l'),
('10', 'he-IL', '040D', 'Hebrew', 0, 'Win10_22H2_Hebrew_x64.iso', 'Win10upd_22H2_Hebrewx64_pbqbowfj6h9l'),
('10', 'hi-IN', '0439', 'Hindi', 0, 'Win10_22H2_Hindi_x64.iso', 'Win10upd_22H2_Hindix64_pbqbowfj6h9lo'),
('10', 'hr-HR', '041A', 'Croatian', 0, 'Win10_22H2_Croatian_x64.iso', 'Win10upd_22H2_Croatianx64_pbqbowfj6h'),
('10', 'hu-HU', '040E', 'Hungarian', 0, 'Win10_22H2_Hungarian_x64.iso', 'Win10upd_22H2_Hungarianx64_pbqbowfj6'),
('10', 'it-IT', '0410', 'Italian', 0, 'Win10_22H2_Italian_x64.iso', 'Win10upd_22H2_Italianx64_pbqbowfj6h9'),
('10', 'ja-JP', '0411', 'Japanese', 0, 'Win10_22H2_Japanese_x64.iso', 'Win10upd_22H2_Japanesex64_pbqbowfj6h'),
('10', 'ko-KR', '0412', 'Korean', 0, 'Win10_22H2_Korean_x64.iso', 'Win10upd_22H2_Koreanx64_pbqbowfj6h9l'),
('10', 'lt-LT', '0427', 'Lithuanian', 0, 'Win10_22H2_Lithuanian_x64.iso', 'Win10upd_22H2_Lithuanianx64_pbqbowfj'),
('10', 'lv-LV', '0426', 'Latvian', 0, 'Win10_22H2_Latvian_x64.iso', 'Win10upd_22H2_Latvianx64_pbqbowfj6h9'),
('10', 'nb-NO', '0414', 'Norwegian', 0, 'Win10_22H2_Norwegian_x64.iso', 'Win10upd_22H2_Norwegianx64_pbqbowfj6'),
('10', 'nl-NL', '0413', 'Dutch', 0, 'Win10_22H2_Dutch_x64.iso', 'Win10upd_22H2_Dutchx64_pbqbowfj6h9lo'),
('10', 'pl-PL', '0415', 'Polish', 0, 'Win10_22H2_Polish_x64.iso', 'Win10upd_22H2_Polishx64_pbqbowfj6h9l'),
('10', 'pt-PT', '0416', 'Portuguese - Portugal', 0, 'Win10_22H2_Portuguese_x64.iso', 'Win10upd_22H2_Portuguesex64_pbqbowfj'),
('10', 'ru-RU', '0419', 'Russian', 0, 'Win10_22H2_Russian_x64.iso', 'Win10upd_22H2_Russianx64_pbqbowfj6h9'),
('10', 'sv-SE', '041D', 'Swedish', 0, 'Win10_22H2_Swedish_x64.iso', 'Win10upd_22H2_Swedishx64_pbqbowfj6h9'),
('10', 'th-TH', '041E', 'Thai', 0, 'Win10_22H2_Thai_x64.iso', 'Win10upd_22H2_Thaix64_pbqbowfj6h9lom'),
('10', 'tr-TR', '041F', 'Turkish', 0, 'Win10_22H2_Turkish_x64.iso', 'Win10upd_22H2_Turkishx64_pbqbowfj6h9'),
('10', 'uk-UA', '0422', 'Ukrainian', 0, 'Win10_22H2_Ukrainian_x64.iso', 'Win10upd_22H2_Ukrainian_x64_pbqbowfj'),
('10', 'zh-CHT', '7C04', 'Chinese - Traditional', 0, 'Win10_22H2_Chinese_Traditional_x64.iso', 'Win10upd_22H2_Chinese_Traditionalx64'),
('10', 'zh-CN', '0804', 'Chinese (Simplified) - China', 0, 'Win10_22H2_Chinese_Simplified_x64.iso', 'Win10upd_22H2_Chinese_Simplifiedx64_');

--
-- Dumping data for table `up_packages_major_Lang_code` for windows 11
--
INSERT INTO `up_packages_major_Lang_code` VALUES
('11','ar-SA','0401','Arabic',0,'Win11_24H2_Arabic_x64.iso','Win11upd_24H2_Arabicx64_pbqbowfj6h9l'),
('11','bg-BG','0402','Bulgarian',0,'Win11_24H2_Bulgarian_x64.iso','Win11upd_24H2_Bulgarianx64_pbqbowfj6'),
('11','cs-CZ','0405','Czech',0,'Win11_24H2_Czech_x64.iso','Win11upd_24H2_Czechx64_pbqbowfj6h9lo'),
('11','da-DK','0406','Danish',0,'Win11_24H2_Danish_x64.iso','Win11upd_24H2_Danishx64_pbqbowfj6h9l'),
('11','de-DE','0407','German',0,'Win11_24H2_German_x64.iso','Win11upd_24H2_Germanx64_pbqbowfj6h9l'),
('11','el-GR','0408','Greek',0,'Win11_24H2_Greek_x64.iso','Win11upd_24H2_Greekx64_pbqbowfj6h9lo'),
('11','en-GB','0809','English - United Kingdom',1,'Win11_24H2_English_x64.iso','Win11upd_24H2_Englishx64_pbqbowfj6h9'),
('11','en-US','0409','English',1,'Win11_24H2_EnglishInternational_x64.iso','Win11upd_24H2_EnglishInternationalx6'),
('11','es-ES','040A','Spanish',0,'Win11_24H2_Spanish_x64.iso','Win11upd_24H2_Spanishx64_pbqbowfj6h9'),
('11','es-MX','080A','Spanish - Mexico',0,'Win11_24H2_Spanish_Mexico_x64.iso','Win11upd_24H2_Spanish_Mexicox64_pbqb'),
('11','et-EE','0425','Estonian - Estonia',0,'Win11_24H2_Estonian_x64.iso','Win11upd_24H2_Estonianx64_pbqbowfj6h'),
('11','fi-FI','040E','Finnish',0,'Win11_24H2_Finnish_x64.iso','Win11upd_24H2_Finnishx64_pbqbowfj6h9'),
('11','fr-CA','0C0C','French - Canada',0,'Win11_24H2_FrenchCanadian_x64.iso','Win11upd_24H2_FrenchCanadianx64_pbqb'),
('11','fr-FR','040C','French',1,'Win11_24H2_French_x64.iso','Win11upd_24H2_Frenchx64_pbqbowfj6h9l'),
('11','he-IL','040D','Hebrew',0,'Win11_24H2_Hebrew_x64.iso','Win11upd_24H2_Hebrewx64_pbqbowfj6h9l'),
('11','hi-IN','0439','Hindi',0,'Win11_24H2_Hindi_x64.iso','Win11upd_24H2_Hindix64_pbqbowfj6h9lo'),
('11','hr-HR','041A','Croatian',0,'Win11_24H2_Croatian_x64.iso','Win11upd_24H2_Croatianx64_pbqbowfj6h'),
('11','hu-HU','040E','Hungarian',0,'Win11_24H2_Hungarian_x64.iso','Win11upd_24H2_Hungarianx64_pbqbowfj6'),
('11','it-IT','0410','Italian',0,'Win11_24H2_Italian_x64.iso','Win11upd_24H2_Italianx64_pbqbowfj6h9'),
('11','ja-JP','0411','Japanese',0,'Win11_24H2_Japanese_x64.iso','Win11upd_24H2_Japanesex64_pbqbowfj6h'),
('11','ko-KR','0412','Korean',0,'Win11_24H2_Korean_x64.iso','Win11upd_24H2_Koreanx64_pbqbowfj6h9l'),
('11','lt-LT','0427','Lithuanian',0,'Win11_24H2_Lithuanian_x64.iso','Win11upd_24H2_Lithuanianx64_pbqbowfj'),
('11','lv-LV','0426','Latvian',0,'Win11_24H2_Latvian_x64.iso','Win11upd_24H2_Latvianx64_pbqbowfj6h9'),
('11','nb-NO','0414','Norwegian',0,'Win11_24H2_Norwegian_x64.iso','Win11upd_24H2_Norwegianx64_pbqbowfj6'),
('11','nl-NL','0413','Dutch',0,'Win11_24H2_Dutch_x64.iso','Win11upd_24H2_Dutchx64_pbqbowfj6h9lo'),
('11','pl-PL','0415','Polish',0,'Win11_24H2_Polish_x64.iso','Win11upd_24H2_Polishx64_pbqbowfj6h9l'),
('11','pt-PT','0416','Portuguese - Portugal',0,'Win11_24H2_Portuguese_x64.iso','Win11upd_24H2_Portuguesex64_pbqbowfj'),
('11','ru-RU','0419','Russian',0,'Win11_24H2_Russian_x64.iso','Win11upd_24H2_Russianx64_pbqbowfj6h9'),
('11','sv-SE','041D','Swedish',0,'Win11_24H2_Swedish_x64.iso','Win11upd_24H2_Swedishx64_pbqbowfj6h9'),
('11','th-TH','041E','Thai',0,'Win11_24H2_Thai_x64.iso','Win11upd_24H2_Thaix64_pbqbowfj6h9lom'),
('11','tr-TR','041F','Turkish',0,'Win11_24H2_Turkish_x64.iso','Win11upd_24H2_Turkishx64_pbqbowfj6h9'),
('11','uk-UA','0422','Ukrainian',0,'Win11_24H2_Ukrainian_x64.iso','Win11upd_24H2_Ukrainian_x64_pbqbowfj'),
('11','zh-CHT','7C04','Chinese - Traditional',0,'Win11_24H2_Chinese_Traditional_x64.iso','Win11upd_24H2_Chinese_Traditionalx64'),
('11','zh-CN','0804','Chinese (Simplified) - China',0,'Win11_24H2_Chinese_Simplified_x64.iso','Win11upd_24H2_Chinese_Simplifiedx64_');


--
-- Dumping data for table `up_packages_major_Lang_code` for windows server 2025
--

INSERT INTO up_packages_major_Lang_code (major, lang_code, num_code, country, enabled, iso_filename, package_uuid) VALUES
('MSO25', 'ar-SA', '0401', 'Arabic', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Arabic_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Arabicx64_pbqbowfj6h9l'),
('MSO25', 'bg-BG', '0402', 'Bulgarian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Bulgarian_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Bulgarianx64_pbqbowfj6'),
('MSO25', 'cs-CZ', '0405', 'Czech', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Czech_DC_STD_MLF_X23-81889.ISO', 'MSO25upd_24H2_Czechx64_pbqbowfj6h9lo'),
('MSO25', 'da-DK', '0406', 'Danish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Danish_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Danishx64_pbqbowfj6h9l'),
('MSO25', 'de-DE', '0407', 'German', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_German_DC_STD_MLF_X23-81893.ISO', 'MSO25upd_24H2_Germanx64_pbqbowfj6h9l'),
('MSO25', 'el-GR', '0408', 'Greek', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Greek_DC_STD_MLF_X23-81893.ISO', 'MSO25upd_24H2_Greekx64_pbqbowfj6h9lo'),
('MSO25', 'en-GB', '0809', 'English - United Kingdom', 1,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_English_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Englishx64_pbqbowfj6h9'),
('MSO25', 'en-US', '0409', 'English', 1, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_English_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_EnglishInternationalx6'),
('MSO25', 'es-ES', '040A', 'Spanish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Spanish_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Spanishx64_pbqbowfj6h9'),
('MSO25', 'es-MX', '080A', 'Spanish - Mexico', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Spanish_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Spanish_Mexicox64_pbqb'),
('MSO25', 'et-EE', '0425', 'Estonian - Estonia', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Estonian_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Estonianx64_pbqbowfj6h'),
('MSO25', 'fi-FI', '040E', 'Finnish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Finnish_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Finnishx64_pbqbowfj6h9'),
('MSO25', 'fr-CA', '0C0C', 'French - Canada', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_French_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_FrenchCanadianx64_pbqb'),
('MSO25', 'fr-FR', '040C', 'French', 1, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_French_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Frenchx64_pbqbowfj6h9l'),
('MSO25', 'he-IL', '040D', 'Hebrew', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Hebrew_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Hebrewx64_pbqbowfj6h9l'),
('MSO25', 'hi-IN', '0439', 'Hindi', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Hindi_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Hindix64_pbqbowfj6h9lo'),
('MSO25', 'hr-HR', '041A', 'Croatian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Croatian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Croatianx64_pbqbowfj6h'),
('MSO25', 'hu-HU', '040E', 'Hungarian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Hungarian_DC_STD_MLF_X23-81894.ISO', 'MSO25upd_24H2_Hungarianx64_pbqbowfj6'),
('MSO25', 'it-IT', '0410', 'Italian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Italian_DC_STD_MLF_X23-81895.ISO', 'MSO25upd_24H2_Italianx64_pbqbowfj6h9'),
('MSO25', 'ja-JP', '0411', 'Japanese', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Japanese_DC_STD_MLF_X23-81896.ISO', 'MSO25upd_24H2_Japanesex64_pbqbowfj6h'),
('MSO25', 'ko-KR', '0412', 'Korean', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Korean_DC_STD_MLF_X23-81897.ISO', 'MSO25upd_24H2_Koreanx64_pbqbowfj6h9l'),
('MSO25', 'lt-LT', '0427', 'Lithuanian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Lithuanian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Lithuanianx64_pbqbowfj'),
('MSO25', 'lv-LV', '0426', 'Latvian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Latvian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Latvianx64_pbqbowfj6h9'),
('MSO25', 'nb-NO', '0414', 'Norwegian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Norwegian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Norwegianx64_pbqbowfj6'),
('MSO25', 'nl-NL', '0413', 'Dutch', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Dutch_DC_STD_MLF_X23-81890.ISO', 'MSO25upd_24H2_Dutchx64_pbqbowfj6h9lo'),
('MSO25', 'pl-PL', '0415', 'Polish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Polish_DC_STD_MLF_X23-81898.ISO', 'MSO25upd_24H2_Polishx64_pbqbowfj6h9l'),
('MSO25', 'pt-PT', '0416', 'Portuguese - Portugal', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Portuguese_DC_STD_MLF_X23-81899.ISO', 'MSO25upd_24H2_Portuguesex64_pbqbowfj'),
('MSO25', 'pt-BR', '0416', 'Portuguese - Brazil', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Brazilian_DC_STD_MLF_X23-81886.ISO', 'MSO25upd_24H2_Brazilianx64_pbqbowfj6'),
('MSO25', 'ru-RU', '0419', 'Russian', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Russian_DC_STD_MLF_X23-81900.ISO', 'MSO25upd_24H2_Russianx64_pbqbowfj6h9'),
('MSO25', 'sv-SE', '041D', 'Swedish', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Swedish_DC_STD_MLF_X23-81902.ISO', 'MSO25upd_24H2_Swedishx64_pbqbowfj6h9'),
('MSO25', 'th-TH', '041E', 'Thai', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Thai_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Thaix64_pbqbowfj6h9lom'),
('MSO25', 'tr-TR', '041F', 'Turkish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Turkish_DC_STD_MLF_X23-81903.ISO', 'MSO25upd_24H2_Turkishx64_pbqbowfj6h9'),
('MSO25', 'uk-UA', '0422', 'Ukrainian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Ukrainian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Ukrainian_x64_pbqbowfj'),
('MSO25', 'zh-CHT','7C04', 'Chinese - Traditional', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_ChnTrad_DC_STD_MLF_X23-81888.ISO', 'MSO25upd_24H2_Chinese_Traditionalx64'),
('MSO25', 'zh-CN', '0804', 'Chinese (Simplified) - China', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_ChnSimp_DC_STD_MLF_X23-81887.ISO', 'MSO25upd_24H2_Chinese_Simplifiedx64_');



-- ----------------------------------------------------------------------
-- REGENERE LES TABLES PRODUITS
-- ----------------------------------------------------------------------
call up_create_product_tables();
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 95;

COMMIT;




