--
-- (c) 2023 Siveo, http://www.siveo.net/
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

START TRANSACTION;


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win11_X64`()
BEGIN
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
		aa.title LIKE '%Windows 11%'
		AND aa.product LIKE '%Windows 11%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%'
        AND aa.title not like '%22H2%'
        AND aa.title not like '%23H2%'
        AND aa.title not like '%21H2%';
END$$

DELIMITER ;
;


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_21H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win11_X64_21H2`()
BEGIN
DROP TABLE IF EXISTS up_packages_Win11_X64_21H2;
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
        JOIN
    xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
WHERE
        aa.title LIKE '%Windows 11 Version 21H2%'
        and aa.product LIKE '%Windows 11%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%';
        --
END$$

DELIMITER ;
;


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_22H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win11_X64_22H2`()
BEGIN
DROP TABLE IF EXISTS up_packages_Win11_X64_22H2;
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
        JOIN
    xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
WHERE
        aa.title LIKE '%Windows 11 Version 22H2%'
        and aa.product LIKE '%Windows 11%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%';
        --
END$$

DELIMITER ;
;


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_23H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win11_X64_23H2`()
BEGIN
DROP TABLE IF EXISTS up_packages_Win11_X64_23H2;
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
        JOIN
    xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
WHERE
        aa.title LIKE '%Windows 11 Version 23H2%'
        and aa.product LIKE '%Windows 11%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%';
        --
END$$

DELIMITER ;
;


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_24H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_packages_Win11_X64_24H2`()
BEGIN
DROP TABLE IF EXISTS up_packages_Win11_X64_24H2;
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
        JOIN
    xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
WHERE
        aa.title LIKE '%Windows 11 Version 24H2%'
        and aa.product LIKE '%Windows 11%'
		AND aa.title NOT LIKE '%ARM64%'
		AND aa.title NOT LIKE '%X86%'
        AND aa.title not like '%Dynamic%';
END$$

DELIMITER ;
;



USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_create_product_tables`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_create_product_tables`()
BEGIN

	call up_init_packages_Win10_X64_1903();
	call up_init_packages_Win10_X64_21H2();
	call up_init_packages_Win10_X64_21H1();
	call up_init_packages_office_2003_64bit();
	call up_init_packages_office_2007_64bit();
	call up_init_packages_office_2010_64bit();
	call up_init_packages_office_2013_64bit();
	call up_init_packages_office_2016_64bit();
	call up_init_packages_Vstudio_2005();
	call up_init_packages_Vstudio_2008();
	call up_init_packages_Vstudio_2010();
	call up_init_packages_Vstudio_2012();
	call up_init_packages_Vstudio_2013();
	call up_init_packages_Vstudio_2015();
	call up_init_packages_Vstudio_2017();
	call up_init_packages_Vstudio_2019();
	call up_init_packages_Vstudio_2022();
	call up_init_packages_Win11_X64();
    call up_init_packages_Win11_X64_21H2();
	call up_init_packages_Win11_X64_22H2();
	call up_init_packages_Win11_X64_23H2();
	call up_init_packages_Win11_X64_24H2();
	call up_init_packages_Win_Malicious_X64();
	call up_init_packages_Win10_X64_22H2();
END$$

DELIMITER ;
;

INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win11_X64_21H2');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win11_X64_22H2');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win11_X64_23H2');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win11_X64_24H2');
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 92;

COMMIT;
