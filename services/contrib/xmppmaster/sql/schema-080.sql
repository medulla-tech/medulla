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

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------

START TRANSACTION;
USE `xmppmaster`;


-- ----------------------------------------------------------------------
-- up_init_packages_office_2007_64bit stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2007_64bit`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_office_2007_64bit`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
        AND aa.title not like '%Dynamic%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_office_2010_64bit stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2010_64bit`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_office_2010_64bit`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package
DROP TABLE IF EXISTS up_packages_office_2010_64bit;
CREATE TABLE up_packages_office_2010_64bit AS
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
        AND aa.title not like '%Dynamic%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_office_2013_64bit stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2013_64bit`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_office_2013_64bit`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
DROP TABLE IF EXISTS up_packages_office_2013_64bit;
CREATE TABLE up_packages_office_2013_64bit AS
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
        AND aa.title not like '%Dynamic%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_office_2016_64bit stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2016_64bit`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_office_2016_64bit`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
        AND aa.title not like '%Dynamic%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2005 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2005`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2005`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2008 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2008`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2008`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2010 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2010`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2010`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2012 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2012`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2012`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2013 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2013`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2013`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2015 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2015`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2015`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2017 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2017`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2017`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2019 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2019`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2019`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Vstudio_2022 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2022`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Vstudio_2022`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
;

-- ----------------------------------------------------------------------
-- up_init_packages_Win10_X64_1903 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win10_X64_1903`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Win10_X64_1903`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
		aa.title LIKE '%Version 1903%'
		AND aa.product LIKE '%Windows 10, version 1903 and later%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_Win10_X64_21H1 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win10_X64_21H1`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Win10_X64_21H1`()
BEGIN
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
    aa.title LIKE '%21H1%'
    AND (aa.product LIKE '%Windows 10, version 1903 and later%'
        OR aa.product LIKE '%Windows 10 and later GDR-DU%')
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_Win10_X64_21H2 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win10_X64_21H2`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Win10_X64_21H2`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
		aa.title LIKE '%Windows 10 Version 21H2%'
        AND aa.product LIKE '%Windows 10%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_Win10_X64_22H2 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win10_X64_22H2`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Win10_X64_22H2`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
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
		aa.title LIKE '%Windows 10 Version 22H2%'
		AND (aa.product LIKE '%Windows 10, version 1903 and later%'
        OR aa.product LIKE '%Windows 10 and later GDR-DU%')
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title LIKE '%X64%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_Win11_X64 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win11_X64`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Win11_X64`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
DROP TABLE IF EXISTS up_packages_Win11_X64;
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
        JOIN
    xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
WHERE
		aa.product LIKE '%Windows 11%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%';
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_init_packages_Win_Malicious_X64 stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win_Malicious_X64`;

DELIMITER $$
CREATE PROCEDURE `up_init_packages_Win_Malicious_X64`()
BEGIN
-- jointure pour renseigner le payloadfiles et le updateid_package 
DROP TABLE IF EXISTS up_packages_Win_Malicious_X64;
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
        JOIN
    xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
WHERE
    aa.title LIKE '%Windows Malicious Software Removal Tool x64%'
        AND aa.product LIKE '%Windows 1%'
ORDER BY aa.revisionid DESC;
END$$

DELIMITER ;
;

-- ----------------------------------------------------------------------
-- up_search_kb_update stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_search_kb_update`;

DELIMITER $$
CREATE PROCEDURE `up_search_kb_update`(in tablesearch varchar(1024), in KB_LIST varchar(2048) )
BEGIN
	  DECLARE result VARCHAR(50);
      CASE 
      WHEN tablesearch IN ( 'up_packages_Win10_X64_21H1',
							'up_packages_Win10_X64_21H2',
						    'up_packages_Win10_X64_221H2',
						    'up_packages_Win11_X64', 
                            'up_packages_Win10_X64_1903') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				",tablesearch," vv
					INNER JOIN
				(SELECT 
					*
				FROM
					",tablesearch,"
				WHERE
					supersededby = ''
				GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 9)
				ORDER BY revisionid DESC) ee ON ee.updateid = vv.updateid
			WHERE
				vv.KB NOT IN (",KB_LIST,");");
	WHEN  tablesearch IN ( 'up_packages_office_2003_64bit',
						   'up_packages_office_2007_64bit',
						   'up_packages_office_2010_64bit',
						   'up_packages_office_2013_64bit',
						   'up_packages_office_2016_64bit') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				",tablesearch," vv
					INNER JOIN
				(SELECT 
					*
				FROM
					",tablesearch,"
				WHERE
					supersededby = '' 
					and updateclassification like 'Security Updates' 
				   GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 31)
					ORDER BY revisionid DESC) ee ON ee.updateid = vv.updateid
					where  
					vv.updateclassification like 'Security Updates'
                    AND vv.KB NOT IN (",KB_LIST,");");

    
	WHEN  tablesearch IN ( 'up_packages_Vstudio_2005',
						   'up_packages_Vstudio_2008',
                           'up_packages_Vstudio_2010',
                           'up_packages_Vstudio_2012',
                           'up_packages_Vstudio_2013',
                           'up_packages_Vstudio_2015',
                           'up_packages_Vstudio_2017',
                           'up_packages_Vstudio_2019',
                           'up_packages_Vstudio_2022') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				",tablesearch," vv
					INNER JOIN
				(SELECT 
					*
				FROM
					",tablesearch,"
				WHERE
					supersededby = '' 
					and updateclassification like 'Security Updates' 
				   GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 38)
					ORDER BY revisionid DESC) ee ON ee.updateid = vv.updateid
					where  
					vv.updateclassification like 'Security Updates'
                    AND vv.KB NOT IN (",KB_LIST,");");
	WHEN  tablesearch IN ( 'up_packages_Win_Malicious_X64') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				xmppmaster.up_packages_Win_Malicious_X64
			WHERE 
				KB NOT IN (",KB_LIST,")
			ORDER BY revisionid DESC
			LIMIT 1;");
	ELSE
		SET @query = concat("SELECT * FROM xmppmaster.update_data");
	END CASE;   
 PREPARE stmt FROM @query;
 EXECUTE stmt ;
END$$

DELIMITER ;
;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 80;

COMMIT;
