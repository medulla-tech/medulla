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
-- ----------------------------------------------------------------------
-- Database cretion table produit Server
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_server_MSOS_ARM64_24H2`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_MSOS_ARM64_24H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_MSOS_ARM64_24H2`()
BEGIN
-- création table up_packages_MSOS_ARM64_24H2
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



USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_server_MSOS_X64_23H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_server_MSOS_X64_23H2`()
BEGIN
-- création table up_packages_MSOS_X64_23H2
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


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_create_product_tables`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_create_product_tables`()
BEGIN
	-- Generation des tables de mise à jour produits
    -- office mise à jour
    call up_init_packages_office_2003_64bit();
	call up_init_packages_office_2007_64bit();
	call up_init_packages_office_2010_64bit();
	call up_init_packages_office_2013_64bit();
	call up_init_packages_office_2016_64bit();

    -- visual studio mise à jour
	call up_init_packages_Vstudio_2005();
	call up_init_packages_Vstudio_2008();
	call up_init_packages_Vstudio_2010();
	call up_init_packages_Vstudio_2012();
	call up_init_packages_Vstudio_2013();
	call up_init_packages_Vstudio_2015();
	call up_init_packages_Vstudio_2017();
	call up_init_packages_Vstudio_2019();
	call up_init_packages_Vstudio_2022();

    -- Operating system
    -- WIN 10 mise à jour
	call up_init_packages_Win10_X64_1903();
	call up_init_packages_Win10_X64_21H2();
	call up_init_packages_Win10_X64_21H1();
    call up_init_packages_Win10_X64_22H2();

	-- Win 11 mise à jour
	call up_init_packages_Win11_X64();
    call up_init_packages_Win11_X64_21H2();
	call up_init_packages_Win11_X64_22H2();
	call up_init_packages_Win11_X64_23H2();
	call up_init_packages_Win11_X64_24H2();

    -- securité mise à jour
	call up_init_packages_Win_Malicious_X64();

    -- SERVER mise à jour
	call up_init_packages_server_MSOS_X64_21H2();
	call up_init_packages_server_MSOS_X64_22H2();
	call up_init_packages_server_MSOS_X64_23H2();
	call up_init_packages_server_MSOS_X64_24H2();
	call up_init_packages_server_MSOS_ARM64_24H2();

	 -- OLD SERVEUR WINDOWS

	 -- call up_init_packages_server_WS_X64_2003();
	 -- call up_init_packages_server_WS_X64_2008();
	 call up_init_packages_server_WS_X64_2012();
	 call up_init_packages_server_WS_X64_2016();
	 call up_init_packages_server_WS_X64_2019();
END$$

DELIMITER ;
;

-- prise en compte  produit
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_21H2', '0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_22H2', '0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_23H2', '0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_X64_24H2', '0');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`, `enable`) VALUES ('up_packages_MSOS_ARM64_24H2', '0');

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 96;

COMMIT;
