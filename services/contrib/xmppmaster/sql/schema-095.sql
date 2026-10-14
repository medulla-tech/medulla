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
-- Reinitialisation et migration des tables liees a la gestion des listes
-- =====================================================================

-- 1. Vider les tables grises (pas de declenchement de triggers car TRUNCATE)
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

-- 2. Supprimer l'index si necessaire
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
--   Cette table permet de definir des parametres applicatifs.
--   Chaque parametre est defini par une cle (key) et une valeur (value),
--   auxquels peuvent être associes un commentaire, un contexte et un module.
--
-- Contraintes :
--   - id : cle primaire auto-incrementee.
--   - (key, value) doit être unique (empêche les doublons).
--
-- Remarque :
--   Utiliser la colonne "comment" pour documenter la signification du parametre.
-- =====================================================================

-- Suppression et recreation de la table applicationconfig
DROP TABLE IF EXISTS xmppmaster.applicationconfig;
CREATE TABLE `xmppmaster`.`applicationconfig` (
  `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique de la ligne',
  `key` VARCHAR(45) NOT NULL COMMENT 'Nom du parametre',
  `value` VARCHAR(1024) NOT NULL COMMENT 'Valeur du parametre',
  `comment` VARCHAR(400) NULL COMMENT 'Description ou notes explicatives',
  `context` VARCHAR(45) NULL COMMENT 'Contexte d’utilisation (ex: environnement, domaine)',
  `module` VARCHAR(45) NULL COMMENT 'Module ou sous-systeme concerne',
  `enable` TINYINT(1) NULL DEFAULT 1 COMMENT 'Indique si la configuration est activee',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_key_value` (`key`, `value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Table de configuration applicative (parametres generaux et contextuels)';

-- Vidage de la table avant insertion
TRUNCATE xmppmaster.applicationconfig;

-- Insertion des donnees pour les produits Microsoft
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

-- Regles de mise a jour
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
--   Cette table stocke la liste des mise a jour Microsoft associes a chaque entite GLPI.
--   Chaque ligne correspond a un produit activable/desactivable pour une entite.
--
-- Colonnes :
--   - id : Identifiant technique unique (cle primaire auto-incrementee).
--   - entity_id : Reference vers l’identifiant d’une entite GLPI (glpi_entity.id).
--   - name_procedure : Nom du produit ou de la procedure associe a l’entite.
--   - enable : Indique si le produit est active (1) ou desactive (0, par defaut).
--
-- Contraintes :
--   - PRIMARY KEY (id) : identifiant unique technique.
--   - UNIQUE (entity_id, name_procedure) : une entite ne peut pas avoir deux fois
--     le même produit associe.
--
-- Remarques :
--   - Les entrees sont creees automatiquement lors de l’ajout d’une entite
--     via un trigger.
--   - Le champ enable est initialise a 0, l’activation se fait ensuite manuellement.
-- =====================================================================


-- Suppression et recreation de la table up_list_produit
DROP TABLE IF EXISTS xmppmaster.up_list_produit;
CREATE TABLE xmppmaster.up_list_produit (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identifiant technique',
    entity_id INT NOT NULL COMMENT 'Reference vers glpi_entity.id',
    name_procedure VARCHAR(255) NOT NULL COMMENT 'Nom du produit/procedure associe a l’entite',
    enable TINYINT(1) DEFAULT 0 COMMENT 'Activation (0 = desactive par defaut)',
    comment VARCHAR(2048) NULL COMMENT 'Description ou notes explicatives',
    UNIQUE KEY uniq_entity_procedure (entity_id, name_procedure)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Liste des produits associes a une entite GLPI';



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
    -- Nom de la table dediee au produit Windows 10 version 1903 X64
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
    -- Nom de la table dediee au produit Windows 10 version 21H1 X64
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
    -- Nom de la table dediee au produit Windows 10 Version 21H2 X64
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
    -- Nom de la table dediee au produit Windows 10 Version 22H2 X64
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
    -- Nom de la table dediee au produit Windows 11 x64 (hors versions H2 specifiques)
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64;
    -- =======================================
    -- Creation de la table avec jointure pour payloadfiles et updateid_package
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
    -- Nom de la table dediee au produit Windows 11 Version 21H2 x64
    -- =======================================
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_21H2;
    -- =======================================
    -- Creation de la table avec jointure pour payloadfiles et updateid_package
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
    -- Nom de la table dediee au produit Windows 11 Version 22H2 x64
    -- =======================================

    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_22H2;
    -- =======================================
    -- Creation de la table avec jointure pour payloadfiles et updateid_package
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

    -- Creation de la table avec jointure et filtres specifiques
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
    -- Creation de la table avec jointure pour payloadfiles et updateid_package
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

    -- Cree la table en resultat d'une selection (sans SQL dynamique)
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
-- Purpose  : Parcourt toutes les procedures d’initialisation de packages
--             (nommees up_init_packages_*) dans la base xmppmaster et
--             genere dynamiquement la commande SQL d’appel pour chacune.
--
-- Usage    :
--   CALL up_create_product_tables();
--
-- Output   :
--   Une liste de chaînes du type :
--     CALL up_init_packages_nom();
--   (Non executees, simplement affichees)
--
-- Notes    :
--   - Les procedures "up_init_packages_*" doivent exister dans xmppmaster.
--   - Si tu veux qu’elles soient reellement executees, remplacer le SELECT
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

  -- Securite de session
  SET SESSION wait_timeout = 600;
  SET SESSION max_allowed_packet = 256*1024*1024;

  OPEN cur;

  read_loop: LOOP
    FETCH cur INTO proc_name;
    IF done THEN
      LEAVE read_loop;
    END IF;

    -- Utiliser une variable de session (prepare l'execution dynamique)
    SET @sql_stmt = CONCAT('CALL ', proc_name, '();');

    -- Executer dynamiquement
    PREPARE stmt FROM @sql_stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    SELECT CONCAT('✓ Procedure executee : ', proc_name) AS success_msg;
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
--   Recherche les mises a jour de securite (KB) manquantes dans une table
--   specifique de packages selon la famille du produit (Windows, Office, Visual Studio…).
--   Genere dynamiquement une requête SQL adaptee au type de produit.
--
-- Parameters :
--   IN tablesearch VARCHAR(1024)
--       → Nom de la table produit a interroger (ex : 'up_packages_Win10_X64_22H2')
--   IN KB_LIST VARCHAR(2048)
--       → Liste de KBs (identifiants de correctifs) deja connus, separes par des virgules.
--
-- Behavior :
--   - Si KB_LIST est vide ou NULL → la procedure se termine immediatement.
--   - Selon la table passee en argument :
--       • Windows (Win10, Win11, Server, MSOS) :
--            Recherche les dernieres revisions non obsoletes (supersededby = '')
--            et dont les KB ne figurent pas dans KB_LIST.
--       • Office (2003–2016) :
--            Recherche les dernieres mises a jour de securite uniquement.
--       • Visual Studio (2005–2022) :
--            Idem, limite aux "Security Updates".
--       • Win_Malicious_X64 :
--            Selectionne le dernier correctif non present dans KB_LIST.
--       • Autres tables :
--            Retourne le contenu complet de xmppmaster.update_data (fallback).
--
-- Output :
--   - Execute dynamiquement un SELECT correspondant au produit demande.
--   - Retourne le ou les enregistrements des mises a jour KB non encore presentes.
--
-- Notes :
--   - Utilise SQL dynamique (PREPARE / EXECUTE) pour executer la requête construite.
--   - Les sous-requêtes "max(revisionid)" permettent d’obtenir uniquement
--     les revisions les plus recentes par famille de patch.
--   - Si une table n’est pas reconnue dans les listes prevues, la procedure
--     renvoie par defaut le contenu de xmppmaster.update_data.
--
-- Example usage :
--   CALL up_search_kb_update('up_packages_Win10_X64_22H2', 'KB5030219,KB5030300');
--
-- Expected result :
--   → Retourne toutes les mises a jour KB non presentes dans la liste donnee.
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

    -- Verifier si KB_LIST est vide
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
--   Cette procedure initialise la table `xmppmaster.up_auto_approve_rules`
--   pour une entite GLPI donnee (`p_entity_id`) uniquement si celle-ci existe.
--   Elle ne supprime rien : si des regles existent deja pour l’entite,
--   la procedure ne les modifie pas.
--   Si aucune regle n’existe, elle insere celles definies dans
--   `xmppmaster.applicationconfig` (key='table rules', context='entity').
--
-- etapes principales :
--   1. Verifie que l'entite existe dans `glpi_entity`.
--   2. Parcourt les entrees `applicationconfig` correspondant aux regles actives.
--   3. Insere pour chaque regle un enregistrement dans `up_auto_approve_rules`
--      avec `active_rule = 0` pour l’entite donnee.
--
-- Parametres :
--   - p_entity_id (INT) : Identifiant GLPI de l’entite a initialiser.
--
-- Effets :
--   - Ne supprime aucune donnee existante.
--   - Ajoute uniquement les entrees manquantes pour l’entite.
--
-- Contraintes / Remarques :
--   - Le champ `active_rule` est toujours initialise a 0 (desactive par defaut).
--   - Si l’entite n’existe pas dans `glpi_entity`, la procedure ne fait rien.
--   - Cette procedure est complementaire a `up_regenere_list_produit_entity()`,
--     mais limitee a l’initialisation des regles automatiques.
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

    -- Verifier si l'entite existe
    IF EXISTS (SELECT 1 FROM xmppmaster.local_glpi_entities WHERE id = p_entity_id)
    THEN
        -- Ouvrir le curseur
        OPEN cur;

        read_loop: LOOP
            FETCH cur INTO v_msrcseverity, v_updateclassification;
            IF done THEN
                LEAVE read_loop;
            END IF;

            -- Inserer les regles pour l’entite donnee
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
--   Cette procedure initialise la table xmppmaster.up_list_produit pour une
--   entite GLPI donnee (specifiee par son glpi_id) uniquement si aucun produit
--   n’y est encore associe.
--   Elle ne supprime rien : si des produits existent deja pour l’entite,
--   la procedure ne fait aucune modification.
--   Dans le cas contraire, elle insere les produits definis dans
--   xmppmaster.applicationconfig (key='table produits', context='entity').
--
-- etapes principales :
--   1. Verification que l'entite existe dans glpi_entity.
--   2. Verification de la presence d’entrees dans up_list_produit pour cette entite.
--   3. Si aucune entree n’existe :
--        a. Parcours de la liste des produits definis dans applicationconfig.
--        b. Insertion d’une ligne (entity_id, name_procedure, enable=0)
--           pour chaque produit associe a l’entite specifiee.
--
-- Parametres :
--   - p_entity_id (INT) : Identifiant GLPI de l’entite a initialiser.
--
-- Effets :
--   - Ne supprime aucune donnee existante.
--   - Ajoute de nouvelles entrees uniquement si l’entite n’a encore aucun produit.
--
-- Contraintes / Remarques :
--   - Le champ enable est toujours initialise a 0 (desactive par defaut).
--   - Si l’entite n’existe pas dans glpi_entity, la procedure ne fait rien.
--   - Cette procedure est complementaire a up_regenere_list_produit_entity(),
--     mais ne fait l’insertion que si necessaire.
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
    IF EXISTS (SELECT 1 FROM xmppmaster.local_glpi_entities WHERE id = p_entity_id)
    THEN
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
--   Cette procedure complete la table xmppmaster.up_list_produit pour une
--   seule entite GLPI specifiee par son glpi_id.
--   Elle conserve les entrees existantes pour cette entite, puis ajoute
--   uniquement les associations manquantes avec les produits definis dans
--   xmppmaster.applicationconfig (key='table produits', context='entity').
--
-- etapes principales :
--   1. Verification que l'entite existe dans glpi_entity.
--   2. Parcours de la liste des produits definis dans applicationconfig.
--   3. Parcours de la liste des produits definis dans applicationconfig.
--   4. Pour chaque produit manquant, insertion d’une ligne
--      (entity_id, name_procedure, enable=0) pour l’entite specifiee.
--
-- Parametres :
--   - p_entity_id (INT) : Identifiant GLPI de l’entite a regenerer.
--
-- Effets :
--   - Conserve les entrees existantes pour l’entite specifiee.
--   - Ajoute de nouvelles entrees pour cette entite couvrant l’ensemble
--     des produits definis.
--
-- Contraintes / Remarques :
--   - Le champ enable est toujours initialise a 0 (desactive par defaut).
--   - Si l’entite n’existe pas dans glpi_entity, la procedure ne fait rien.
--   - Cette procedure s’inspire du trigger xmppmasterglpi_entity_AFTER_INSERT
--     mais agit uniquement sur l’entite specifiee, et non sur toutes les entites.
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
    DECLARE v_comment VARCHAR(2048);

    -- Declaration du curseur
    DECLARE cur CURSOR FOR
        SELECT `value`, `comment`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity';

    -- Gestion fin de curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Verifier que l'entite existe
    IF EXISTS (SELECT 1 FROM glpi_entity WHERE glpi_id = p_entity_id) THEN

        -- Ouvrir le curseur
        OPEN cur;

        read_loop: LOOP
            FETCH cur INTO v_produit, v_comment;
            IF done THEN
                LEAVE read_loop;
            END IF;

            -- Ajouter uniquement les produits manquants pour l’entite donnee
            INSERT IGNORE INTO xmppmaster.up_list_produit (entity_id, name_procedure, enable, comment)
            VALUES (p_entity_id, v_produit, 0, v_comment);
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
-- PROCEDURE : regenere_liste_produits
-- Description :
--   Complete la table xmppmaster.up_list_produit,
--   puis ajoute les associations entite/produit manquantes pour chaque entite
--   presente dans la table xmppmaster.glpi_entity.
--
-- Fonctionnement :
--   - Conserve les lignes existantes dans xmppmaster.up_list_produit.
--   - Recupere la liste des produits configures (cle 'tables produits', contexte 'entity')
--     depuis la table xmppmaster.applicationconfig.
--   - Pour chaque entite et pour chaque produit manquant, insere une ligne dans
--     up_list_produit avec enable = 0.
--
-- Tables concernees :
--   - xmppmaster.glpi_entity : source des entites.
--   - xmppmaster.applicationconfig : source des produits configures.
--   - xmppmaster.up_list_produit : table cible (reconstruite).
--
-- Remarques :
--   - Le champ enable est toujours initialise a 0, l’activation doit être faite manuellement.
--   - Les associations existantes sont conservees afin de preserver les activations.
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
    DECLARE v_comment VARCHAR(2048);
    -- Declaration du curseur
    DECLARE cur CURSOR FOR
        SELECT `value`, `comment`
        FROM xmppmaster.applicationconfig
        WHERE `key` = 'table produits'
          AND `context` = 'entity';

    -- Gestion fin de curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- Ouvrir le curseur
    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO v_produit, v_comment;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Inserer uniquement les associations manquantes pour chaque entite trouvee
        INSERT IGNORE INTO xmppmaster.up_list_produit (entity_id, name_procedure, enable, comment)
        SELECT e.glpi_id, v_produit, 0, v_comment
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
--   Ce trigger s’execute apres l’insertion d’une nouvelle entite dans la table glpi_entity.
--   Il initialise automatiquement la liste des produits associes a cette entite,
--   en se basant sur la configuration stockee dans la table applicationconfig.
--
-- Fonctionnement :
--   - Recupere la liste des produits configures (cle 'tables produits', contexte 'entity')
--     depuis la table xmppmaster.applicationconfig.
--   - Pour chaque produit trouve, insere une ligne dans xmppmaster.up_list_produit,
--     associee a la nouvelle entite, avec enable=0 (desactive par defaut).
--   - Ne duplique pas les entrees : verifie l’absence de (entity_id, name_procedure) avant insertion.
--
-- Tables concernees :
--   - xmppmaster.glpi_entity : table source (declenche le trigger).
--   - xmppmaster.applicationconfig : source de la liste des produits a associer.
--   - xmppmaster.up_list_produit : table cible (stocke les associations entite/produit).
--
-- Remarques :
--   - Utilise un curseur pour parcourir dynamiquement les produits configures.
--   - Le champ enable est toujours initialise a 0, l’activation doit être faite manuellement.
--   - Le trigger garantit qu’une entite ne peut pas avoir deux fois le même produit associe.
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
--   Ce trigger s’execute apres la mise a jour d’une ligne dans la table glpi_entity.
--   Il permet de maintenir la coherence des associations entite/produit dans la table
--   xmppmaster.up_list_produit lorsque l’identifiant (glpi_id) d’une entite est modifie.
--
-- Fonctionnement :
--   - Si la valeur de glpi_id change (OLD.glpi_id ≠ NEW.glpi_id) :
--     - Supprime les eventuelles entrees deja existantes dans xmppmaster.up_list_produit
--       pour le nouvel identifiant (NEW.glpi_id), afin d’eviter les doublons.
--     - Met a jour toutes les entrees avec l’ancien identifiant (OLD.glpi_id)
--       pour les associer au nouvel identifiant (NEW.glpi_id).
--
-- Tables concernees :
--   - xmppmaster.glpi_entity : table source (declenche le trigger).
--   - xmppmaster.up_list_produit : table cible (contient les associations entite/produit).
--
-- Remarques :
--   - Ce trigger suppose que glpi_id peut être modifie manuellement, bien que cela soit rare.
--   - Il agit uniquement si la valeur de glpi_id change effectivement.
--   - Les suppressions sont faites avant la mise a jour pour eviter toute collision d’ID.
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
--   Ce trigger s’execute apres la suppression d’une entite dans la table glpi_entity.
--   Il supprime automatiquement toutes les associations de produits liees a cette entite
--   dans la table xmppmaster.up_list_produit, afin d’eviter les donnees orphelines.
--
-- Fonctionnement :
--   - Recupere l’identifiant de l’entite supprimee (OLD.glpi_id).
--   - Supprime toutes les lignes de xmppmaster.up_list_produit ou entity_id correspond a glpi_id.
--
-- Tables concernees :
--   - xmppmaster.glpi_entity : table source (declenche le trigger).
--   - xmppmaster.up_list_produit : table cible (nettoyee lors de la suppression d’une entite).
--
-- Remarques :
--   - Ce trigger evite que des produits restent lies a des entites inexistantes.
--   - Aucun contrôle supplementaire n’est effectue : la suppression est inconditionnelle.
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
-- creation table up_packages_MSOS_ARM64_24H2
-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_ARM64_24H2
-- Description :
--   Cette procedure initialise la table `up_packages_MSOS_ARM64_24H2` en extrayant
--   les mises a jour specifiques au **systeme d'exploitation serveur Microsoft
--   version 24H2 (ARM64)** depuis la table `xmppmaster.update_data`.
--   Elle prepare les donnees necessaires pour le deploiement des packages
--   lies a cette version et architecture du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_ARM64_24H2` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 24H2".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'inclusion exclusive de l'architecture ARM64.
--     * L'exclusion des architectures X86 et X64.
--     * L'exclusion des titres contenant "Dynamic".
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques au **systeme d'exploitation serveur Microsoft version 24H2 (ARM64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
--   Cette procedure initialise la table `up_packages_MSOS_X64_21H2` en extrayant
--   les mises a jour specifiques au **systeme d'exploitation serveur Microsoft
--   version 21H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prepare les donnees necessaires pour le deploiement des packages
--   lies a cette version du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_21H2` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 21H2".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques au **systeme d'exploitation serveur Microsoft version 21H2 (x64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
-- creation table up_packages_MSOS_X64_21H2
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
--   Cette procedure initialise la table `up_packages_MSOS_X64_22H2` en extrayant
--   les mises a jour specifiques au **systeme d'exploitation serveur Microsoft
--   version 22H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prepare les donnees necessaires pour le deploiement des packages
--   lies a cette version du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_22H2` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 22H2".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques au **systeme d'exploitation serveur Microsoft version 22H2 (x64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
-- creation table up_packages_MSOS_X64_23H2

-- =====================================================================
-- PROCEDURE : up_init_packages_server_MSOS_X64_23H2
-- Description :
--   Cette procedure initialise la table `up_packages_MSOS_X64_23H2` en extrayant
--   les mises a jour specifiques au **systeme d'exploitation serveur Microsoft
--   version 23H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prepare les donnees necessaires pour le deploiement des packages
--   lies a cette version du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_23H2` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 23H2".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques au **systeme d'exploitation serveur Microsoft version 23H2 (x64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
--   Cette procedure initialise la table `up_packages_MSOS_X64_24H2` en extrayant
--   les mises a jour specifiques au **systeme d'exploitation serveur Microsoft
--   version 24H2 (x64)** depuis la table `xmppmaster.update_data`.
--   Elle prepare les donnees necessaires pour le deploiement des packages
--   lies a cette version du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_MSOS_X64_24H2` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Microsoft server operating system version 24H2".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques au **systeme d'exploitation serveur Microsoft version 24H2 (x64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
-- creation table up_packages_MSOS_X64_24H2
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
--   Cette procedure initialise la table `up_packages_WS_X64_2003` en extrayant
--   les mises a jour specifiques a **Windows Server 2003 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle prepare les donnees necessaires pour le deploiement
--   des packages lies a cette version du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_WS_X64_2003` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2003".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques a **Windows Server 2003 (x64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
-- creation table up_packages_WS_X64_2003  Server windows
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
--   Cette procedure initialise la table `up_packages_WS_X64_2008` en extrayant
--   les mises a jour specifiques a **Windows Server 2008 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle prepare les donnees necessaires pour le deploiement
--   des packages lies a cette version du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_WS_X64_2008` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2008".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques a **Windows Server 2008 (x64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
-- creation table up_packages_WS_X64_2008 serveur window
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
--   Cette procedure initialise la table `up_packages_WS_X64_2012` en extrayant
--   les mises a jour specifiques a **Windows Server 2012 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle prepare les donnees necessaires pour le deploiement
--   des packages lies a cette version du systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table existante `up_packages_WS_X64_2012` si elle existe deja.
--   - Cree une nouvelle table en effectuant une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2012".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`.
--
-- Remarques :
--   - La table resultante est conçue pour faciliter la gestion des mises a jour
--     specifiques a **Windows Server 2012 (x64)**.
--   - Les criteres de filtrage garantissent que seuls les packages pertinents
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
-- creation table up_packages_WS_X64_2012 serveur windows
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
--   Cette procedure initialise la table `up_packages_WS_X64_2016` en extrayant
--   les mises a jour specifiques a **Windows Server 2016 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle permet de preparer les donnees necessaires
--   pour le deploiement des packages lies a cette version de systeme d'exploitation.
--
-- Fonctionnement :
--   - Supprime la table `up_packages_WS_X64_2016` si elle existe deja.
--   - Cree une nouvelle table a partir d'une jointure entre `update_data` (alias `aa`)
--     et `update_data` (alias `bb`), ou `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts pour cibler uniquement :
--     * Les titres (`title`) contenant "Windows Server 2016".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Identifiants : `updateid`, `revisionid`, `updateid_package`.
--   - Metadonnees : `creationdate`, `compagny`, `product`, `productfamily`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--   - Informations de deploiement : `deploymentaction`, `title_short`, etc.
--
-- Remarques :
--   - La table generee est optimisee pour les deploiements de mises a jour
--     specifiques a **Windows Server 2016 (x64)**.
--   - Les donnees sont filtrees pour garantir leur pertinence par rapport a
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
-- creation table up_packages_WS_X64_2016 serveur windows
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
--   Cette procedure initialise la table `up_packages_WS_X64_2019` en selectionnant
--   les mises a jour specifiques a **Windows Server 2019 (x64)** depuis la table
--   `xmppmaster.update_data`. Elle filtre les donnees pour ne conserver que les
--   packages pertinents pour cette version et architecture.
--
-- Fonctionnement :
--   - Supprime la table existante si elle existe.
--   - Cree une nouvelle table `up_packages_WS_X64_2019` a partir d'une jointure
--     entre `update_data` (alias `aa`) et `update_data` (alias `bb`), ou :
--     * `bb.bundledby_revision` correspond a `aa.revisionid`.
--   - Applique des filtres stricts sur :
--     * Le titre (`title`) contenant "Windows Server 2019".
--     * La famille de produit (`productfamily`) egale a "Windows".
--     * L'exclusion des architectures ARM64 et X86.
--     * L'exclusion des titres contenant "Dynamic".
--     * L'inclusion exclusive de l'architecture X64.
--
-- Colonnes selectionnees :
--   - Informations generales : `updateid`, `revisionid`, `creationdate`, `compagny`, etc.
--   - Details techniques : `msrcseverity`, `msrcnumber`, `kb`, `languages`, etc.
--   - Metadonnees de deploiement : `deploymentaction`, `title_short`, etc.
--   - Relations entre packages : `supersededby`, `supersedes`, `bundledby_revision`.
--
-- Remarques :
--   - La table resultante est optimisee pour les deploiements de mises a jour
--     specifiques a **Windows Server 2019 (x64)**.
--   - Les donnees sont extraites en fonction des criteres de filtrage definis.
-- =====================================================================
USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_WS_X64_2019`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_WS_X64_2019`()
BEGIN

DROP TABLE IF EXISTS up_packages_WS_X64_2019;
-- creation table up_packages_WS_X64_2019 serveur windows
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
-- 	-- Generation des tables de mise a jour produits
--     -- office mise a jour
--
--     -- =====================================================================
--     -- PROCEDURE : up_create_product_tables
--     -- Description :
--     --   Cette procedure permet de generer les tables de packages pour les produits
--     --   Microsoft (Office, Visual Studio, Windows, Windows Server, et mises a jour
--     --   de securite). Elle appelle une serie de procedures dediees pour initialiser
--     --   les packages correspondants dans la base de donnees.
--     --
--     -- PROCEDURES appelees :
--     --   - Office (2003 a 2016, 64 bits)
--     --   - Visual Studio (2005 a 2022)
--     --   - Windows 10 (versions 1903, 21H1, 21H2, 22H2)
--     --   - Windows 11 (versions 21H2, 22H2, 23H2, 24H2, 25H2)
--     --   - Mises a jour de securite (Malicious X64)
--     --   - Windows Server (versions 21H2 a 24H2, x64 et ARM64)
--     --   - Anciens serveurs Windows (2012, 2016, 2019)
--     --
--     -- Remarques :
--     --   - Les procedures pour les anciens serveurs (2003, 2008) sont commentees
--     --     et non executees.
--     --   - Apres l'execution, les produits sont references dans la table
--     --     `up_list_produit` avec un statut initial desactive (`enable = 0`).
--     --   - Chaque procedure appelee est responsable de la creation des packages
--     --     specifiques a sa version de produit.
--     --
--     -- Tables impactees :
--     --   - Tables de packages generees par les procedures appelees.
--     --   - `up_list_produit` : insertion des produits references.
--     -- =====================================================================
--     call up_init_packages_office_2003_64bit();
--     call up_init_packages_office_2007_64bit();
--     call up_init_packages_office_2010_64bit();
--     call up_init_packages_office_2013_64bit();
--     call up_init_packages_office_2016_64bit();
--
--     -- visual studio mise a jour
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
--     -- WIN 10 mise a jour
--     call up_init_packages_Win10_X64_1903();
--     call up_init_packages_Win10_X64_21H2();
--     call up_init_packages_Win10_X64_21H1();
--     call up_init_packages_Win10_X64_22H2();
--
--     -- Win 11 mise a jour
--     call up_init_packages_Win11_X64();
--     call up_init_packages_Win11_X64_21H2();
--     call up_init_packages_Win11_X64_22H2();
--     call up_init_packages_Win11_X64_23H2();
--     call up_init_packages_Win11_X64_24H2();
--     call up_init_packages_Win11_X64_25H2();
--
--     -- securite mise a jour
--     call up_init_packages_Win_Malicious_X64();
--
--     -- SERVER mise a jour
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
-- Parametres :
--   - p_entity_id (INT) : Identifiant de l'entite concernee.
--
-- Description :
--   Cette procedure est appelee par le trigger `up_auto_approve_rules_AFTER_UPDATE`.
--   Elle parcourt les mises a jour presentes dans la table `up_gray_list`
--   pour une entite donnee, verifie si elles correspondent a une regle
--   d’approbation automatique definie dans `up_auto_approve_rules`, et si
--   c’est le cas, elle les insere dans la `up_white_list`.
--
-- Tables impactees :
--   - xmppmaster.up_gray_list : source des mises a jour candidates.
--   - xmppmaster.update_data : permet de recuperer la severite (msrcseverity)
--     et la classification (updateclassification) associees a une mise a jour.
--   - xmppmaster.up_auto_approve_rules : contient les regles d’approbation
--     automatique (actives) propres a une entite.
--   - xmppmaster.up_white_list : destination des mises a jour validees par
--     les regles.
--
-- Logique de traitement :
--   1. Parcours des mises a jour de `up_gray_list` pour l’entite.
--   2. Pour chaque mise a jour :
--      * Recuperation de ses attributs (severite et classification).
--      * Verification de l’existence d’une regle active applicable
--        (même severite et/ou classification, ou regle generique).
--   3. Si au moins une regle correspondante existe :
--      * Insertion de la mise a jour dans `up_white_list` (via `INSERT IGNORE`
--        pour eviter les doublons).
--
-- Remarque :
--   Cette procedure automatise le passage de mises a jour de la "gray list"
--   vers la "white list" lorsqu’elles sont couvertes par des regles
--   d’approbation automatique, garantissant un deploiement simplifie et
--   coherent au niveau de l’entite.
--   La suppression de la mise a jour dans `up_gray_list` est assuree
--       automatiquement par un **trigger associe a la table `up_white_list`**
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

        -- Cherche une regle applicable pour cette entite
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
-- Passe l'entityid de la ligne mise a jour a la procedure

-- =====================================================================
-- Trigger : up_auto_approve_rules_AFTER_UPDATE
-- evenement : AFTER UPDATE sur la table xmppmaster.up_auto_approve_rules
--
-- Description :
--   Ce trigger est execute automatiquement apres la mise a jour
--   d’une regle d’approbation automatique dans la table
--   `up_auto_approve_rules`.
--
-- Objectif :
--   - Transmettre l’identifiant de l’entite (`entityid`) de la regle
--     mise a jour a la procedure `move_update_to_white_list`.
--   - Cette procedure se charge ensuite de parcourir la `up_gray_list`
--     et de deplacer les mises a jour correspondant aux regles actives
--     vers la `up_white_list`.
--
-- Logique de traitement :
--   1. Detection de la mise a jour d’une regle dans `up_auto_approve_rules`.
--   2. Appel de la procedure `move_update_to_white_list(NEW.entityid)`.
--   3. La procedure applique les regles d’auto-approbation pour l’entite
--      et met a jour les listes (`gray_list` → `white_list`).
--
-- Impact :
--   Garantit que toute modification sur une regle d’auto-approbation est
--   immediatement prise en compte pour l’entite correspondante, sans
--   intervention manuelle supplementaire.
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
--   Ce trigger est execute avant l'insertion d'une nouvelle entree dans
--   la table `up_black_list`. Il permet de :
--   1. Supprimer les entrees correspondantes dans la table `xmppmaster.deploy`
--      pour les deploiements en cours ou en attente, lies a l'entite et a l'ID
--      de mise a jour specifies dans la nouvelle entree.
--   2. Mettre a jour la date de fin (`end_date`) des commandes associees dans
--      la table `msc.commands`, en les marquant comme obsoletes (55 minutes en arriere).
--
-- Tables impactees :
--   - xmppmaster.deploy : suppression des deploiements en cours ou en attente.
--   - msc.commands : mise a jour de la date de fin des commandes associees.
--
-- Conditions :
--   - Les deploiements supprimes doivent correspondre a :
--     * Un titre commençant par le label du package associe a l'ID de mise a jour.
--     * Une date de fin de commande (`endcmd`) posterieure a l'instant actuel.
--     * Un etat (`state`) correspondant a "WOL 1", "WOL 2", "WOL 3",
--       "DEPLOYMENT START" ou "WAITING MACHINE ONLINE".
--     * Une entite (`entityid`) correspondant a celle de la nouvelle entree.
--   - Les commandes mises a jour doivent correspondre a :
--     * Un `package_id` commençant par l'ID de mise a jour (`updateid_or_kb`).
--     * Un hôte (`target`) dont l'identifiant inventaire correspond a l'entite
--       de la nouvelle entree, ce qui est determine par :
--          SUBSTRING(target.target_uuid, 5) = NEW.entityid
--
-- Remarque :
--   Ce trigger est conçu pour eviter les conflits ou les doublons lors de
--   l'ajout d'une entree dans la liste noire des mises a jour.
--   Il supprime ainsi les mises a jour interdites et invalide les commandes
--   deja programmees ou en cours pour la même entite.
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
--   Ce trigger est execute apres l'insertion d'une nouvelle entree dans
--   la table `up_black_list`. Il permet de synchroniser et nettoyer les
--   listes de mises a jour (gray list, white list et flop) afin d’eviter
--   les conflits, doublons ou executions non souhaitees.
--
-- Tables impactees :
--   - xmppmaster.up_gray_list :
--       * Suppression des entrees correspondant a l’ID ou au KB de la mise
--         a jour nouvellement blacklistee.
--   - xmppmaster.up_gray_list_flop :
--       * Mise a jour temporaire des entrees liees a une mise a jour
--         blacklistee (remplacement par des valeurs "bidon").
--       * Suppression des entrees "bidon" pour nettoyer la table.
--   - xmppmaster.up_white_list :
--       * Suppression des entrees liees a la mise a jour blacklistee.
--
-- Conditions :
--   - Pour le type "id" :
--       * Les entrees gray list / flop sont ciblees sur la colonne `updateid`
--         correspondant au champ `updateid_or_kb` de la nouvelle entree.
--   - Pour le type "kb" :
--       * Les entrees gray list / flop sont ciblees sur la colonne `kb`
--         correspondant au champ `updateid_or_kb` de la nouvelle entree.
--   - Dans tous les cas, le filtre se fait aussi sur `entityid = NEW.entityid`.
--
-- Remarque :
--   Ce trigger assure qu’une mise a jour nouvellement blacklistee est
--   immediatement retiree des listes de gestion (`gray_list`, `white_list`)
--   et neutralisee dans la `gray_list_flop`.
--   Il garantit ainsi la coherence des regles de deploiement et empêche
--   toute execution indesirable d’une mise a jour interdite.
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
--   Ce trigger est execute apres la mise a jour d'une entree dans la table
--   `up_black_list`. Il assure la synchronisation des listes de mises a jour
--   afin que toute modification de regle de blacklist soit immediatement
--   repercutee dans les tables associees (`gray_list`, `gray_list_flop`).
--
-- Tables impactees :
--   - xmppmaster.up_gray_list :
--       * Suppression des entrees correspondant a l’ID ou au KB de la mise
--         a jour desormais blacklistee.
--   - xmppmaster.up_gray_list_flop :
--       * Mise a jour des entrees correspondantes avec des valeurs neutres
--         (remplacement `updateid` par une UUID tronquee, `kb` = 'bidon').
--       * Suppression des entrees marquees "bidon" pour nettoyer la table.
--
-- Conditions :
--   - Pour le type "id" :
--       * Les entrees gray list / flop sont ciblees sur la colonne `updateid`
--         correspondant au champ `updateid_or_kb` de la ligne mise a jour.
--   - Pour le type "kb" :
--       * Les entrees gray list / flop sont ciblees sur la colonne `kb`
--         correspondant au champ `updateid_or_kb` de la ligne mise a jour.
--   - Dans tous les cas, le filtre s’applique aussi sur `entityid = NEW.entityid`.
--
-- Remarque :
--   Ce trigger garantit qu'une modification d'une regle de blacklist est
--   immediatement appliquee aux listes associees, empêchant toute execution
--   future d'une mise a jour interdite et assurant la coherence des donnees.
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
    -- Mise a jour flop par updateid
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
    -- Mise a jour flop par kb
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
--   Ce trigger est execute apres l'insertion d'une nouvelle entree dans la table
--   `up_gray_list`. Il gere l'ajout de commandes de mise a jour et verifie si
--   l'entree doit être automatiquement approuvee selon des regles predefinies.
--
-- Fonctionnement :
--   - Construit une commande pour le script `medulla_mysql_exec_update.sh` avec le `updateid`.
--   - Insere une action dans `up_action_update_packages` pour declencher la commande.
--   - Enregistre un log dans la table `logs` pour tracer la creation de la commande.
--   - Recupere les metadonnees (`msrcseverity`, `updateclassification`) depuis `update_data`.
--   - Verifie si une regle d'approbation automatique (`up_auto_approve_rules`) s'applique :
--     * La regle doit être active (`active_rule = 1`).
--     * La regle doit correspondre aux metadonnees recuperees ou être generique (valeur NULL).
--   - Si une regle est trouvee, insere l'entree dans `pending_events` pour traitement ulterieur.
--
-- Tables impactees :
--   - `up_action_update_packages` : insertion de commandes de mise a jour.
--   - `logs` : insertion de logs pour tracer les actions effectuees.
--   - `pending_events` : insertion des entrees approuvees automatiquement.
--
-- Remarques :
--   - Utilise `INSERT IGNORE` pour eviter les erreurs de doublons.
--   - Les logs sont detailles pour assurer une traçabilite complete des actions.
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

    -- Ajout action (lie a entityid)
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` ( `action`, `packages`, `option`)
    VALUES ( v_cmd, NEW.updateid, "-c");

    -- Log
    SET v_logtext = CONCAT("Creation command : ", v_cmd);
    INSERT INTO `xmppmaster`.`logs` ( `type`, `module`, `text`, `fromuser`, `touser`, `action`,
                                     `sessionname`, `how`, `why`, `priority`, `who`)
    VALUES ('automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_INSERT', 'medulla',
            'creation', NEW.updateid, 'auto', 'mariadb', '-1', 'system');

    -- Recuperation des metadonnees update
    SELECT msrcseverity, updateclassification
    INTO v_msrcseverity, v_updateclassification
    FROM xmppmaster.update_data
    WHERE updateid = NEW.updateid
    LIMIT 1;

    -- Verification auto-approve rules
    SELECT COUNT(*)
    INTO v_exists_rule
    FROM xmppmaster.up_auto_approve_rules
    WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
      AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
      AND active_rule = 1
      AND entityid = NEW.entityid;
    -- Si regle trouvee → ajout a pending_events
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
--   Ce trigger est execute apres la suppression d'une entree dans la table
--   `up_gray_list`. Il gere la suppression des packages en fonction de leur
--   presence dans la liste blanche (`up_white_list`) et de leur type (UUID ou non).
--
-- Fonctionnement :
--   - Declare des variables pour stocker la commande, le texte de log, et un booleen
--     indiquant si le package est en liste blanche.
--   - Construit une commande de suppression pour le script `medulla_mysql_exec_update.sh`.
--   - Verifie si le `updateid` supprime est present dans la liste blanche pour la même `entityid`.
--   - Si le package n'est pas en liste blanche :
--     * Insere une commande dans `up_action_update_packages` pour suppression.
--     * Enregistre un log dans la table `logs` pour tracer la creation de la commande.
--   - Si le `updateid` est un UUID (longueur = 36) :
--     * Enregistre un log pour indiquer le recyclage dans `up_gray_list_flop`.
--     * Insere l'entree supprimee dans `up_gray_list_flop` pour conservation.
--   - Si le `updateid` n'est pas un UUID :
--     * Enregistre un log pour indiquer la suppression definitive du package.
--
-- Tables impactees :
--   - `up_action_update_packages` : insertion de commandes de suppression.
--   - `logs` : insertion de logs pour tracer les actions effectuees.
--   - `up_gray_list_flop` : insertion des entrees recyclees (UUID uniquement).
--
-- Remarques :
--   - Utilise `INSERT IGNORE` pour eviter les erreurs de doublons.
--   - Les logs sont detailles pour assurer une traçabilite complete des actions.
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

    -- Verifie si updateid est en whitelist (même entityid)
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
        -- Sinon suppression definitive
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
--   Ce trigger est execute apres l'insertion d'une nouvelle entree dans la table
--   `up_gray_list`. Il gere l'ajout de commandes de mise a jour et verifie si
--   l'entree doit être automatiquement approuvee selon des regles predefinies.
--
-- Fonctionnement :
--   - Construit une commande pour le script `medulla_mysql_exec_update.sh` avec le `updateid`.
--   - Insere une action dans `up_action_update_packages` pour declencher la commande.
--   - Enregistre un log dans la table `logs` pour tracer la creation de la commande.
--   - Recupere les metadonnees (`msrcseverity`, `updateclassification`) depuis `update_data`.
--   - Verifie si une regle d'approbation automatique (`up_auto_approve_rules`) s'applique :
--     * La regle doit être active (`active_rule = 1`).
--     * La regle doit correspondre aux metadonnees recuperees ou être generique (valeur NULL).
--   - Si une regle est trouvee, insere l'entree dans `pending_events` pour traitement ulterieur.
--
-- Tables impactees :
--   - `up_action_update_packages` : insertion de commandes de mise a jour.
--   - `logs` : insertion de logs pour tracer les actions effectuees.
--   - `pending_events` : insertion des entrees approuvees automatiquement.
--
-- Remarques :
--   - Utilise `INSERT IGNORE` pour eviter les erreurs de doublons.
--   - Les logs sont detailles pour assurer une traçabilite complete des actions.
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

    -- Ajout action (lie a entityid)
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` ( `action`, `packages`, `option`)
    VALUES ( v_cmd, NEW.updateid, "-c");

    -- Log
    SET v_logtext = CONCAT("Creation command : ", v_cmd);
    INSERT INTO `xmppmaster`.`logs` ( `type`, `module`, `text`, `fromuser`, `touser`, `action`,
                                     `sessionname`, `how`, `why`, `priority`, `who`)
    VALUES ('automate_Maria', 'update', v_logtext, 'up_gray_list_AFTER_INSERT', 'medulla',
            'creation', NEW.updateid, 'auto', 'mariadb', '-1', 'system');

    -- Recuperation des metadonnees update
    SELECT msrcseverity, updateclassification
    INTO v_msrcseverity, v_updateclassification
    FROM xmppmaster.update_data
    WHERE updateid = NEW.updateid
    LIMIT 1;

    -- Verification auto-approve rules
    SELECT COUNT(*)
    INTO v_exists_rule
    FROM xmppmaster.up_auto_approve_rules
    WHERE (msrcseverity = v_msrcseverity OR msrcseverity IS NULL)
      AND (updateclassification = v_updateclassification OR updateclassification IS NULL)
      AND active_rule = 1
      AND entityid = NEW.entityid;
    -- Si regle trouvee → ajout a pending_events
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
-- evenement : AFTER DELETE sur la table xmppmaster.up_gray_list_flop
--
-- Description :
--   Ce trigger est execute apres la suppression d'une entree dans la table
--   `up_gray_list_flop`. Il gere la reinjection des entrees supprimees dans
--   `up_gray_list` si l'`updateid` est un UUID de longeur 36. on modifie updateid a bidon avant la
--   suppression cela empeche la recopie dans  tale flop car uuid incorrect.
--
-- Logique de traitement :
--   1. Si l’`updateid` a une longueur de 36 caracteres :
--       * Generation d’un log de reinjection dans la table `logs`.
--       * Reinsertion de la mise a jour dans la table `up_gray_list` pour
--         la même entite (`entityid`), avec une `validity_date` etendue
--         de 10 jours.
--       * Si l’entree existe deja, mise a jour de la `validity_date`.
--   2. Si l’`updateid` n’a pas 36 caracteres :
--       * Generation d’un log indiquant la suppression definitive dans
--         la table `logs`.
--
-- Tables impactees :
--   - xmppmaster.up_gray_list_flop : table declencheur (ligne supprimee).
--   - xmppmaster.up_gray_list : reinsertion des mises a jour valides.
--   - xmppmaster.logs : journalisation de la suppression ou reinsertion.
--
-- Remarque :
--   Ce trigger assure que les mises a jour importantes (UUID de 36 caracteres)
--   ne sont pas perdues et sont reinserees automatiquement dans la
--   `up_gray_list`, tandis que les mises a jour mineures ou invalides
--   sont simplement consignees dans les logs avant suppression definitive.
-- =====================================================================
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_flop_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  TRIGGER `xmppmaster`.`up_gray_list_flop_AFTER_DELETE` AFTER DELETE ON `up_gray_list_flop` FOR EACH ROW
BEGIN


	   IF LENGTH(OLD.updateid) = 36 THEN
        -- Log de reinjection
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

        -- Reinsertion dans up_gray_list avec même entityid
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
        -- Log suppression definitive
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
--   Ce trigger est execute apres l'insertion d'une nouvelle entree dans la table
--   `up_white_list`. Il garantit la coherence des donnees en supprimant toute
--   entree correspondante dans la table `up_gray_list`.
--
-- Fonctionnement :
--   - Supprime automatiquement les entrees de `up_gray_list` ou :
--     * `updateid` correspond a celui de la nouvelle entree en liste blanche.
--     * `entityid` correspond a celui de la nouvelle entree en liste blanche.
--
-- Tables impactees :
--   - `up_gray_list` : suppression des entrees correspondantes.
--
-- Remarques :
--   - Assure que les packages approuves (liste blanche) ne restent pas en
--     liste grise, evitant ainsi les conflits de gestion des mises a jour.
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
--   Ce trigger est execute apres la suppression d'une entree dans la table
--   `up_white_list`. Il nettoie les entrees correspondantes dans la table
--   `up_gray_list_flop` pour maintenir la coherence des donnees.
--
-- Fonctionnement :
--   - Supprime automatiquement les entrees de `up_gray_list_flop` ou :
--     * `updateid` correspond a celui de l'entree supprimee de la liste blanche.
--     * `entityid` correspond a celui de l'entree supprimee de la liste blanche.
--
-- Tables impactees :
--   - `up_gray_list_flop` : suppression des entrees correspondantes.
--
-- Remarques :
--   - Permet de s'assurer que les entrees supprimees de la liste blanche ne
--     persistent pas dans la liste grise des echecs, evitant ainsi les incoherences.
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
--    Cette vue permet de lister les machines Windows activees pour les mises a jour,
--    en tenant compte des listes blanche (white list) et grise (gray list).
--    Elle fournit des informations sur les machines, leurs identifiants, leur statut de deploiement,
--    et leur appartenance a une liste (blanche ou grise).
--
-- Fonctionnement :
--    1. Jointure des tables :
--       - up_machine_windows (umw) : Contient les informations sur les mises a jour des machines Windows.
--       - machines (m) : Contient les informations generales sur les machines (UUID, hostname, JID).
--       - local_glpi_machines (lgm) : Contient les informations locales des machines (entites, statut de suppression, etc.).
--       - up_white_list (uwl) : Liste blanche des mises a jour validees.
--       - up_gray_list (ugl) : Liste grise des mises a jour validees.
--
--    2. Logique de selection :
--       - Seules les machines non supprimees (lgm.is_deleted = 0) et non templates (lgm.is_template = 0) sont incluses.
--       - Seules les machines sous plateforme "Microsoft Windows" sont prises en compte.
--       - Les machines doivent être validees dans au moins une des listes (blanche ou grise).
--
--    3. Champs retournes :
--       - kb : Priorise la valeur de la liste grise (ugl.kb) si elle existe, sinon utilise la valeur de la liste blanche (uwl.kb).
--       - id_machine : Identifiant de la machine.
--       - glpi_id : Identifiant GLPI extrait de l'UUID de la machine.
--       - hostname : Nom d'hôte de la machine.
--       - jid : Identifiant JID de la machine.
--       - entities_id : Identifiant de l'entite associee a la machine.
--       - update_id : Identifiant de la mise a jour.
--       - curent_deploy : Deploiement actuel.
--       - required_deploy : Deploiement requis.
--       - start_date : Date de debut de la mise a jour.
--       - end_date : Date de fin de la mise a jour.
--       - intervals : Intervalle de la mise a jour.
--       - msrcseverity : Niveau de severite MSRC.
--       - list : Indique si la machine est dans la liste blanche ("white") ou grise ("gray").
--
-- Remarques :
--    - Cette vue est utile pour identifier les machines eligibles aux mises a jour,
--      en fonction des regles definies dans les listes blanche et grise.
--    - Les machines sans entree dans la liste grise (ugl.kb IS NULL) sont marquees comme "gray" par defaut.
--    - Assurez-vous que les tables sources sont a jour pour des resultats precis.
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




