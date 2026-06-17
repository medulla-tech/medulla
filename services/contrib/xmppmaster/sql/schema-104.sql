--
-- (c) 2026, http://www.medulla-tech.io/
--
-- FILE contrib/xmppmaster/sql/schema-105.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- Correctif global de collation pour les procedures Win* presentes
-- sur certaines infras en utf8mb3_general_ci (heritage schema-101).
--
-- Objectif:
--   - Ne pas modifier schema-102.sql.
--   - Redefinir les procedures impactees en utf8mb4_general_ci.

START TRANSACTION;

USE `xmppmaster`;

DELIMITER $$

DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_1903`$$

CREATE PROCEDURE `up_init_packages_Win10_X64_1903`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win10_X64_1903;

    CREATE TABLE up_packages_Win10_X64_1903 CHARSET utf8mb4 AS
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
            aa.title LIKE '%X64%';
END$$

DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_21H1`$$

CREATE PROCEDURE `up_init_packages_Win10_X64_21H1`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win10_X64_21H1;
    CREATE TABLE up_packages_Win10_X64_21H1 CHARSET utf8mb4 AS
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
            aa.title LIKE '%X64%';
END$$

DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_21H2`$$

CREATE PROCEDURE `up_init_packages_Win10_X64_21H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win10_X64_21H2;

    CREATE TABLE up_packages_Win10_X64_21H2 CHARSET utf8mb4 AS
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
            aa.title LIKE '%X64%';
END$$

DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_22H2`$$

CREATE PROCEDURE `up_init_packages_Win10_X64_22H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win10_X64_22H2;
    CREATE TABLE up_packages_Win10_X64_22H2 CHARSET utf8mb4 AS
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
            aa.title LIKE '%X64%';
END$$

DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_25H2`$$

CREATE PROCEDURE `up_init_packages_Win11_X64_25H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64_25H2;
    CREATE TABLE up_packages_Win11_X64_25H2 CHARSET utf8mb4 AS
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
            AND aa.title NOT LIKE '%X86%';
END$$

DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64`$$

CREATE PROCEDURE `up_init_packages_Win11_X64`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64;
    CREATE TABLE up_packages_Win11_X64 CHARSET utf8mb4 AS
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
            aa.title NOT LIKE '%X86%';
END$$

DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_21H2`$$

CREATE PROCEDURE `up_init_packages_Win11_X64_21H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64_21H2;
    CREATE TABLE up_packages_Win11_X64_21H2 CHARSET utf8mb4 AS
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
            aa.title NOT LIKE '%X86%';
END$$

DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_22H2`$$

CREATE PROCEDURE `up_init_packages_Win11_X64_22H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64_22H2;
    CREATE TABLE up_packages_Win11_X64_22H2 CHARSET utf8mb4 AS
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
            aa.title NOT LIKE '%X86%';
END$$

DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_23H2`$$

CREATE PROCEDURE `up_init_packages_Win11_X64_23H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64_23H2;
    CREATE TABLE up_packages_Win11_X64_23H2 CHARSET utf8mb4 AS
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
            AND aa.title NOT LIKE '%X86%';
END$$

DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_26H2`$$

CREATE PROCEDURE `up_init_packages_Win11_X64_26H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64_26H2;
    CREATE TABLE up_packages_Win11_X64_26H2 CHARSET utf8mb4 AS
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
            AND aa.title NOT LIKE '%X86%';
END$$

DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_24H2`$$

CREATE PROCEDURE `up_init_packages_Win11_X64_24H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64_24H2;
    CREATE TABLE up_packages_Win11_X64_24H2 CHARSET utf8mb4 AS
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
            AND aa.title NOT LIKE '%X86%';
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 104;

COMMIT;