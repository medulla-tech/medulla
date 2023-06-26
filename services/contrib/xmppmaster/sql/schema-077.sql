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
ALTER TABLE `up_list_produit`
ADD CONSTRAINT `name_procedure_UNIQUE` 
    UNIQUE IF NOT EXISTS (`name_procedure`);


-- https://www.catalog.update.microsoft.com/Home.aspx for getting product names and versions

-- -------------------------------------------------------
-- Procedure to generate all product tables.
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_create_product_tables`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_create_product_tables`()
BEGIN
	-- cette procedure stockee genere les tables pour different produit
    -- list des procedure a appeler pour generer les tables updates
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
	call up_init_packages_Win_Malicious_X64();
	call up_init_packages_Win10_X64_22H2();
END$$

DELIMITER ;
;


-- -------------------------------------------------------
-- PRODUCT TABLE up_init_packages_Win10_X64_22H2
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win10_X64_22H2`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win10_X64_22H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_packages_Win10_X64_22H2`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;
	DECLARE c_title varchar(2040)  DEFAULT "";
    DECLARE c_description varchar(2040)DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";
  DECLARE client_cursor CURSOR FOR
	  SELECT
		updateid, kb, revisionid, title, description
	FROM
		xmppmaster.update_data
	WHERE
    title LIKE '%Windows 10 Version 22H2%'
    AND (product LIKE '%Windows 10, version 1903 and later%'
        OR product LIKE '%Windows 10 and later GDR-DU%')
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
DROP TABLE IF EXISTS `up_packages_Win10_X64_22H2`;
CREATE TABLE `up_packages_Win10_X64_22H2` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048),
  `creationdate` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP() ON UPDATE CURRENT_TIMESTAMP(),
  `title_short` varchar(500),
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title, c_description;

  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `xmppmaster`.`up_packages_Win10_X64_22H2`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

  CLOSE client_cursor;
END$$

DELIMITER ;
;


DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `xmppmaster`.`up_black_list_AFTER_INSERT` AFTER INSERT ON `up_black_list` FOR EACH ROW
BEGIN
	DELETE FROM `xmppmaster`.`up_gray_list`
	WHERE
		`updateid` IN (SELECT
			updateid_or_kb
		FROM
			xmppmaster.up_black_list
		WHERE
			userjid_regexp = '.*'
			AND type_rule = 'id');
	UPDATE `xmppmaster`.`up_gray_list_flop`
	SET
		`updateid` = LEFT(UUID(), 8),
		`kb` = 'bidon'
	WHERE
		`updateid` IN (SELECT
				updateid_or_kb
			FROM
				xmppmaster.up_black_list
			WHERE
				userjid_regexp = '.*'
					AND type_rule = 'id');

	DELETE FROM `xmppmaster`.`up_gray_list`
	WHERE
		`kb` IN (SELECT
			updateid_or_kb
		FROM
			xmppmaster.up_black_list

		WHERE
			userjid_regexp = '.*'
			AND type_rule = 'kb');

	UPDATE `xmppmaster`.`up_gray_list_flop`
	SET
		`kb` = 'bidon'
	WHERE
		`updateid` IN (SELECT
				updateid_or_kb
			FROM
				xmppmaster.up_black_list
			WHERE
				userjid_regexp = '.*'
					AND type_rule = 'kb');
	DELETE FROM `xmppmaster`.`up_gray_list_flop`
	WHERE
		(`kb` = 'bidon');

   DELETE FROM `xmppmaster`.`up_white_list` WHERE (`updateid` = new.updateid_or_kb or `kb` = new.updateid_or_kb );

END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 77;

COMMIT;
