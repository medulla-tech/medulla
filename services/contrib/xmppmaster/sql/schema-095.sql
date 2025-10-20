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

USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2003_64bit`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_office_2003_64bit`()
BEGIN
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_office_2003_64bit';
    DECLARE drop_query TEXT;
    DECLARE create_query TEXT;

    -- Suppression de la table existante
    SET drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Création de la table avec jointure pour payloadfiles et updateid_package
    SET create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS
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
            aa.product LIKE ''%Office 2003%''
            AND aa.title NOT LIKE ''%ARM64%''
            AND aa.title NOT LIKE ''%32-Bit%''
            AND aa.title NOT LIKE ''%Server%''
            AND aa.title NOT LIKE ''%X86%''
            AND aa.title NOT LIKE ''%Dynamic%''
        '
    );
    PREPARE stmt FROM create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Inscription automatique dans up_list_produit si absente
    IF NOT EXISTS (SELECT 1 FROM up_list_produit WHERE name_procedure = table_name) THEN
        INSERT INTO up_list_produit (name_procedure, enable) VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- Elle est utilisée dynamiquement pour créer la table et pour l’enregistrement dans up_list_produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_office_2007_64bit';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (pour éviter les conflits)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Cette requête est propre à chaque procédure selon le filtre produit (ici Office 2007 64bit)
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Office 2007%''
            AND aa.title NOT LIKE ''%ARM64%''
            AND aa.title NOT LIKE ''%32-Bit%''
            AND aa.title NOT LIKE ''%Server%''
            AND aa.title NOT LIKE ''%X86%''
            AND aa.title NOT LIKE ''%Dynamic%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans la table de suivi des procédures : up_list_produit
    -- Cette partie est indispensable pour que la procédure soit reconnue dans Medull.
    -- Elle permet de garder trace des procédures existantes et de les activer/désactiver.
    -- Le champ 'enable' est mis à 0 par défaut (désactivé).
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- Elle est utilisée dynamiquement pour créer la table et pour l’enregistrement dans up_list_produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_office_2010_64bit';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (pour éviter les conflits)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Cette requête est propre à chaque procédure selon le filtre produit (ici Office 2010 64bit)
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Office 2010%''
            AND aa.title NOT LIKE ''%ARM64%''
            AND aa.title NOT LIKE ''%32-Bit%''
            AND aa.title NOT LIKE ''%Server%''
            AND aa.title NOT LIKE ''%X86%''
            AND aa.title NOT LIKE ''%Dynamic%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans la table de suivi des procédures : up_list_produit
    -- Cette partie est indispensable pour que la procédure soit reconnue dans Medull.
    -- Elle permet de garder trace des procédures existantes et de les activer/désactiver.
    -- Le champ 'enable' est mis à 0 par défaut (désactivé).
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
END$$

DELIMITER ;

USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2013_64bit`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_office_2013_64bit`()
BEGIN
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- Elle est utilisée dynamiquement pour créer la table et pour l’enregistrement dans up_list_produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_office_2013_64bit';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (pour éviter les conflits)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Cette requête est propre à chaque procédure selon le filtre produit (ici Office 2013 64bit)
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Office 2013%''
            AND aa.title NOT LIKE ''%ARM64%''
            AND aa.title NOT LIKE ''%32-Bit%''
            AND aa.title NOT LIKE ''%Server%''
            AND aa.title NOT LIKE ''%X86%''
            AND aa.title NOT LIKE ''%Dynamic%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans la table de suivi des procédures : up_list_produit
    -- Cette partie est indispensable pour que la procédure soit reconnue dans Medull.
    -- Elle permet de garder trace des procédures existantes et de les activer/désactiver.
    -- Le champ 'enable' est mis à 0 par défaut (désactivé).
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- Elle est utilisée dynamiquement pour créer la table et pour l’enregistrement dans up_list_produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_office_2016_64bit';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (pour éviter les conflits)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Cette requête est propre à chaque procédure selon le filtre produit (ici Office 2016 64bit)
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Office 2016%''
            AND aa.title NOT LIKE ''%ARM64%''
            AND aa.title NOT LIKE ''%32-Bit%''
            AND aa.title NOT LIKE ''%Server%''
            AND aa.title NOT LIKE ''%X86%''
            AND aa.title NOT LIKE ''%Dynamic%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans la table de suivi des procédures : up_list_produit
    -- Cette partie est indispensable pour que la procédure soit reconnue dans Medull.
    -- Elle permet de garder trace des procédures existantes et de les activer/désactiver.
    -- Le champ 'enable' est mis à 0 par défaut (désactivé).
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- Elle est utilisée dynamiquement pour créer la table et pour l’enregistrement dans up_list_produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2005';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (pour éviter les conflits)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Cette requête est propre à chaque procédure selon le filtre produit (ici Visual Studio 2005)
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2005%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans la table de suivi des procédures : up_list_produit
    -- Cette partie est indispensable pour que la procédure soit reconnue dans Medull.
    -- Elle permet de garder trace des procédures existantes et de les activer/désactiver.
    -- Le champ 'enable' est mis à 0 par défaut (désactivé).
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- Elle est utilisée dynamiquement pour créer la table et pour l’enregistrement dans up_list_produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2008';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (pour éviter les conflits)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Cette requête est propre à chaque procédure selon le filtre produit (ici Visual Studio 2008)
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2008%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans la table de suivi des procédures : up_list_produit
    -- Cette partie est indispensable pour que la procédure soit reconnue dans Medull.
    -- Elle permet de garder trace des procédures existantes et de les activer/désactiver.
    -- Le champ 'enable' est mis à 0 par défaut (désactivé).
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- Elle est utilisée dynamiquement pour créer la table et pour l’enregistrement dans up_list_produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2010';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (pour éviter les conflits)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Cette requête est propre à chaque procédure selon le filtre produit (ici Visual Studio 2010)
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2010%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans la table de suivi des procédures : up_list_produit
    -- Cette partie est indispensable pour que la procédure soit reconnue dans Medull.
    -- Elle permet de garder trace des procédures existantes et de les activer/désactiver.
    -- Le champ 'enable' est mis à 0 par défaut (désactivé).
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Cette variable contient le nom unique de la table propre au produit.
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2012';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Suppression de la table si elle existe déjà (évite les doublons)
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création dynamique de la table des mises à jour du produit
    -- Chaque procédure contient un filtre produit spécifique
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2012%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Vérifier si la table est déjà enregistrée dans up_list_produit
    -- Ne pas oublier cette étape : elle permet à Medull de détecter la procédure
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Déclaration du nom de la table de mise à jour à créer
    -- Chaque procédure génère une table dédiée, conforme au produit ciblé
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2013';
    DECLARE sql_query TEXT;

    -- =======================================
    -- Supprimer la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Créer dynamiquement la table de mise à jour pour le produit ciblé
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2013%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Vérification de l'enregistrement dans up_list_produit
    -- Cette étape est essentielle pour que Medull détecte ce jeu de données
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Nom de la table dédiée au produit Visual Studio 2015
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2015';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2015%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Nom de la table dédiée au produit Visual Studio 2017
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2017';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2017%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Nom de la table dédiée au produit Visual Studio 2019
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2019';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2019%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    -- =======================================
    -- Nom de la table dédiée au produit Visual Studio 2022
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Vstudio_2022';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.product LIKE ''%Visual Studio 2022%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;
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
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win10_X64_1903';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.title LIKE ''%Version 1903%'' AND
            aa.product LIKE ''%Windows 10, version 1903 and later%'' AND
            aa.title NOT LIKE ''%ARM64%'' AND
            aa.title NOT LIKE ''%X86%'' AND
            aa.title NOT LIKE ''%Dynamic%'' AND
            aa.title LIKE ''%X64%'''
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

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
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win10_X64_21H1';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.title LIKE ''%21H1%'' AND
            (aa.product LIKE ''%Windows 10, version 1903 and later%'' OR aa.product LIKE ''%Windows 10 and later GDR-DU%'') AND
            aa.title NOT LIKE ''%ARM64%'' AND
            aa.title NOT LIKE ''%X86%'' AND
            aa.title NOT LIKE ''%Dynamic%'' AND
            aa.title LIKE ''%X64%''
        '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

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
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win10_X64_21H2';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.title LIKE ''%Windows 10 Version 21H2%'' AND
            aa.product LIKE ''%Windows 10%'' AND
            aa.title NOT LIKE ''%ARM64%'' AND
            aa.title NOT LIKE ''%X86%'' AND
            aa.title NOT LIKE ''%Dynamic%'' AND
            aa.title LIKE ''%X64%''
        '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

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
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win10_X64_22H2';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.title LIKE ''%Windows 10 Version 22H2%'' AND
            (aa.product LIKE ''%Windows 10, version 1903 and later%'' OR aa.product LIKE ''%Windows 10 and later GDR-DU%'') AND
            aa.title NOT LIKE ''%ARM64%'' AND
            aa.title NOT LIKE ''%X86%'' AND
            aa.title NOT LIKE ''%Dynamic%'' AND
            aa.title LIKE ''%X64%''
        '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

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
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win11_X64';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS
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
            aa.product LIKE ''%Windows 11%'' AND
            aa.title NOT LIKE ''%ARM64%'' AND
            aa.title NOT LIKE ''%X86%'' AND
            aa.title NOT LIKE ''%Dynamic%'' AND
            aa.title NOT LIKE ''%22H2%'' AND
            aa.title NOT LIKE ''%23H2%'' AND
            aa.title NOT LIKE ''%21H2%''
    '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

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
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win11_X64_21H2';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS
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
            aa.title LIKE ''%Windows 11 Version 21H2%'' AND
            aa.product LIKE ''%Windows 11%'' AND
            aa.title NOT LIKE ''%ARM64%'' AND
            aa.title NOT LIKE ''%X86%'' AND
            aa.title NOT LIKE ''%Dynamic%''
    '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

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
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win11_X64_22H2';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS
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
            aa.title LIKE ''%Windows 11 Version 22H2%'' AND
            aa.product LIKE ''%Windows 11%'' AND
            aa.title NOT LIKE ''%ARM64%'' AND
            aa.title NOT LIKE ''%X86%'' AND
            aa.title NOT LIKE ''%Dynamic%''
    '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

END$$

DELIMITER ;

USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_23H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_23H2`()
BEGIN
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win11_X64_23H2';

    -- Suppression de la table si elle existe
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Création de la table avec jointure et filtres spécifiques
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS
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
            aa.title LIKE ''%Windows 11 Version 23H2%''
            AND aa.product LIKE ''%Windows 11%''
            AND aa.title NOT LIKE ''%ARM64%''
            AND aa.title NOT LIKE ''%X86%''
            AND aa.title NOT LIKE ''%Dynamic%''
        '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Inscription dans up_list_produit si absente
    IF NOT EXISTS (SELECT 1 FROM up_list_produit WHERE name_procedure = table_name) THEN
        INSERT INTO up_list_produit (name_procedure, enable) VALUES (table_name, 0);
    END IF;

END$$

DELIMITER ;


USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_24H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_24H2`()
BEGIN
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win11_X64_24H2';

    -- Suppression de la table existante
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Création de la table avec jointure pour payloadfiles et updateid_package
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS
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
            aa.title LIKE ''%Windows 11 Version 24H2%''
            AND aa.product LIKE ''%Windows 11%''
            AND aa.title NOT LIKE ''%ARM64%''
            AND aa.title NOT LIKE ''%X86%''
            AND aa.title NOT LIKE ''%Dynamic%''
        '
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- Inscription automatique dans up_list_produit si absente
    IF NOT EXISTS (SELECT 1 FROM up_list_produit WHERE name_procedure = table_name) THEN
        INSERT INTO up_list_produit (name_procedure, enable) VALUES (table_name, 0);
    END IF;

END$$

DELIMITER ;



-- =======================================
-- up_init_packages_Win_Malicious_X64 stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win_Malicious_X64`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win_Malicious_X64`()
BEGIN
    -- =======================================
    -- Nom de la table dédiée au produit Windows Malicious Software Removal Tool x64
    -- =======================================
    DECLARE table_name VARCHAR(100) DEFAULT 'up_packages_Win_Malicious_X64';

    -- =======================================
    -- Suppression de la table si elle existe déjà
    -- =======================================
    SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', table_name);
    PREPARE stmt FROM @drop_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    -- =======================================
    SET @create_query = CONCAT(
        'CREATE TABLE ', table_name, ' AS ',
        'SELECT
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
            aa.title LIKE ''%Windows Malicious Software Removal Tool x64%'' AND
            aa.product LIKE ''%Windows 1%''
        ORDER BY aa.revisionid DESC'
    );

    PREPARE stmt FROM @create_query;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

    -- =======================================
    -- Enregistrement dans up_list_produit si absent (enable = 0 par défaut)
    -- =======================================
    IF NOT EXISTS (
        SELECT 1 FROM up_list_produit WHERE name_procedure = table_name
    ) THEN
        INSERT INTO up_list_produit (name_procedure, enable)
        VALUES (table_name, 0);
    END IF;

END$$

DELIMITER ;
;

-- =======================================
-- up_create_product_tables stored procedure
-- =======================================
USE `xmppmaster`;
DROP procedure IF EXISTS `up_create_product_tables`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_create_product_tables`;
;

DELIMITER $$

CREATE PROCEDURE up_create_product_tables()
BEGIN
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
  DECLARE done INT DEFAULT FALSE;
  DECLARE proc_name VARCHAR(255);
  DECLARE cur CURSOR FOR
    SELECT ROUTINE_NAME
    FROM information_schema.ROUTINES
    WHERE ROUTINE_SCHEMA = 'xmppmaster'
      AND ROUTINE_TYPE = 'PROCEDURE'
      AND ROUTINE_NAME LIKE 'up_init_packages_%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  OPEN cur;

  read_loop: LOOP
    FETCH cur INTO proc_name;
    IF done THEN
      LEAVE read_loop;
    END IF;

    SELECT CONCAT('CALL ', proc_name, '();') AS call_statement;
  END LOOP;

  CLOSE cur;
END$$

DELIMITER ;
;

-- =======================================
-- up_create_product_tables stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_create_product_tables`;

DELIMITER $$

CREATE PROCEDURE `up_create_product_tables`()
BEGIN
  DECLARE done INT DEFAULT FALSE;
  DECLARE proc_name VARCHAR(255);
  DECLARE sql_stmt VARCHAR(300);

  -- Déclaration du curseur en premier
  DECLARE cur CURSOR FOR
    SELECT ROUTINE_NAME
    FROM information_schema.ROUTINES
    WHERE ROUTINE_SCHEMA = 'xmppmaster'
      AND ROUTINE_TYPE = 'PROCEDURE'
      AND ROUTINE_NAME LIKE 'up_init_packages_%';

  -- Handlers APRÈS la déclaration du curseur
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
  BEGIN
    SELECT CONCAT('⚠️ Erreur lors de l’exécution de : ', proc_name) AS error_msg;
  END;

  OPEN cur;

  read_loop: LOOP
    FETCH cur INTO proc_name;
    IF done THEN
      LEAVE read_loop;
    END IF;

    SET sql_stmt = CONCAT('CALL ', proc_name, '();');

    -- Affiche la procédure en cours
    -- SELECT CONCAT('Exécution de : ', sql_stmt) AS info;

    -- Exécute réellement la procédure
    PREPARE stmt FROM sql_stmt;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;

   -- SELECT
   --  CONCAT('✓ Fin : ', proc_name, ' exécutée avec succès') AS info_end;
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



-- =======================================
-- Database version
-- =======================================
UPDATE version SET Number = 95;

COMMIT;
