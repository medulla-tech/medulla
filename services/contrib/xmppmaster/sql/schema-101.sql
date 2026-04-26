--
-- (c) 2026, http://www.medulla-tech.io/
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
-- FILE contrib/xmppmaster/sql/schema-101.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- Fix: Redéfinition des procédures up_init_packages_* avec collation utf8mb3_general_ci
-- Résout l'erreur SQL 42000: COLLATION 'utf8mb4_general_ci' is not valid for CHARACTER SET 'utf8mb3'

START TRANSACTION;
DELIMITER $$
USE `xmppmaster`$$

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
            aa.title LIKE '%X64%' COLLATE utf8mb3_general_ci;
END$$

DELIMITER ;

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
            aa.title LIKE '%X64%' COLLATE utf8mb3_general_ci;
END$$

DELIMITER ;

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
            aa.title LIKE '%X64%' COLLATE utf8mb3_general_ci;
END$$

DELIMITER ;

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
            aa.title LIKE '%X64%' COLLATE utf8mb3_general_ci;
END$$

DELIMITER ;

DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_25H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_25H2`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_25H2;
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    CREATE TABLE up_packages_Win11_X64_25H2 AS
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
            aa.title LIKE '%Windows 11, version 25H2%'
            AND aa.product LIKE '%Windows 11%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%X86%' COLLATE utf8mb3_general_ci;

END$$

DELIMITER ;

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
            aa.title NOT LIKE '%21H2%' AND
            aa.title NOT LIKE '%22H2%' AND
            aa.title NOT LIKE '%23H2%' AND
            aa.title NOT LIKE '%24H2%' AND
            aa.title NOT LIKE '%25H2%' AND
            aa.title NOT LIKE '%26H2%' AND
            aa.title NOT LIKE '%X86%' COLLATE utf8mb3_general_ci;
END$$

DELIMITER ;

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
            aa.title NOT LIKE '%X86%'  COLLATE utf8mb3_general_ci;
END$$

DELIMITER ;

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
            aa.title NOT LIKE '%X86%' COLLATE utf8mb3_general_ci;

END$$

DELIMITER ;

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
            AND aa.title NOT LIKE '%X86%' COLLATE utf8mb3_general_ci;
END$$

DELIMITER ;

DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_26H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_26H2`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_26H2;
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    CREATE TABLE up_packages_Win11_X64_26H2 AS
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
            aa.title LIKE '%Windows 11, version 25H2%'
            AND aa.product LIKE '%Windows 11%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%X86%' COLLATE utf8mb3_general_ci;

END$$

DELIMITER ;

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
            AND aa.title NOT LIKE '%X86%' COLLATE utf8mb3_general_ci;

END$$

DELIMITER ;


-- Enregistrement de la version
UPDATE version SET Number = 101;

commit;
