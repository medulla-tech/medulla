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
-- CREATE TABLE update_data
-- this table permet de retrouver les download complet pour tous les packages
-- payloadfiles dit ou trouver le package
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `up_packages` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  PRIMARY KEY (`updateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- CREATE TABLE update_data
-- this table are the updates windows
-- this table is the update_data table image of table base_wsusscn2.update_data
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_reinit_table_update_data`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_reinit_table_update_data`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_reinit_table_update_data`()
begin
        set  @existtable_in_base_wsusscn2 := ( select EXISTS (
            SELECT *
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'base_wsusscn2'
                AND TABLE_NAME = 'update_data'));

        set  @existtable_in_xmppmaster := NULL;
        if @existtable_in_base_wsusscn2 is not null then
            --  table existtable
            DROP TABLE IF EXISTS xmppmaster.update_datacopy ;
            create table xmppmaster.update_datacopy as ( SELECT * FROM base_wsusscn2.update_data);
            -- --------------------------------------------------------
            -- creation des index sur la table copie
            --
            -- --------------------------------------------------------
            ALTER TABLE `xmppmaster`.`update_datacopy`
                CHANGE COLUMN `updateid` `updateid` VARCHAR(38) CHARACTER SET 'utf8mb4' NOT NULL ,
                ADD PRIMARY KEY (`updateid`),
                ADD UNIQUE INDEX `updateid_UNIQUE` (`updateid` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_product` (`product` ASC);

            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `indkb` (`kb` ASC);


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_update_classification` (`updateclassification` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_replaceby` (`supersededby` ASC);


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_title` (`title` ASC);

            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_category` (`category` ASC);

            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_product_family` (`productfamily` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
                ADD INDEX `ind_msrcseverity` (`msrcseverity` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
            ADD INDEX `ind_msrcnumber` (`msrcnumber` ASC) ;


            ALTER TABLE `xmppmaster`.`update_datacopy`
            ADD INDEX `ind_revisionnumber` (`revisionnumber` ASC) ;


		DROP TABLE IF EXISTS xmppmaster.update_data ;
           ALTER TABLE `xmppmaster`.`update_datacopy`
              RENAME TO  `xmppmaster`.`update_data` ;

        end if;
            CREATE TABLE  IF NOT EXISTS  `update_data` (
                `updateid` varchar(38) NOT NULL,
                `revisionid` varchar(16) NOT NULL,
                `creationdate` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
                `compagny` varchar(36) DEFAULT '',
                `product` varchar(512) DEFAULT '',
                `productfamily` varchar(100) DEFAULT '',
                `updateclassification` varchar(36) DEFAULT '',
                `prerequisite` varchar(2000) DEFAULT '',
                `title` varchar(500) DEFAULT '',
                `description` varchar(2048) DEFAULT '',
                `msrcseverity` varchar(16) DEFAULT '',
                `msrcnumber` varchar(16) DEFAULT '',
                `kb` varchar(16) DEFAULT '',
                `languages` varchar(16) DEFAULT '',
                `category` varchar(80) DEFAULT '',
                `supersededby` varchar(2048) DEFAULT '',
                `supersedes` text DEFAULT NULL,
                `payloadfiles` varchar(1024) DEFAULT '',
                `revisionnumber` varchar(30) DEFAULT '',
                `bundledby_revision` varchar(30) DEFAULT '',
                `isleaf` varchar(6) DEFAULT '',
                `issoftware` varchar(30) DEFAULT '',
                `deploymentaction` varchar(30) DEFAULT '',
                `title_short` varchar(500) DEFAULT '',
                PRIMARY KEY (`updateid`),
                    UNIQUE KEY `updateid_UNIQUE` (`updateid`),
                    UNIQUE KEY `id_UNIQUE1` (`revisionid`),
                    KEY `ind_product` (`product`(768)),
                    KEY `indkb` (`kb`),
                    KEY `ind_update_classification` (`updateclassification`),
                    KEY `ind_replaceby` (`supersededby`(768)),
                    KEY `ind_title` (`title`(768)),
                    KEY `ind_category` (`category`),
                    KEY `ind_product_family` (`productfamily`),
                    KEY `ind_msrcseverity` (`msrcseverity`),
                    KEY `ind_msrcnumber` (`msrcnumber`),
                    KEY `ind_revisionnumber` (`revisionnumber`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
     END$$

DELIMITER ;
;

-- Execute the procedure
call up_reinit_table_update_data();


-- ----------------------------------------------------------------------
-- CREATE TABLE up_gray_list
-- this table are the updates machine applicable
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `up_gray_list` (
  `updateid` varchar(36) NOT NULL,
  `kb` varchar(16) NOT NULL,
  `revisionid` varchar(16) NOT NULL,
  `title` varchar(1024) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `updateid_package` varchar(36) NOT NULL,
  `payloadfiles` varchar(2048) NOT NULL,
  `supersededby` varchar(2048) DEFAULT NULL,
  `creationdate` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `title_short` varchar(500) DEFAULT NULL,
  `valided` tinyint(4) DEFAULT 0,
  `validity_date` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`updateid`),
  KEY `kb` (`kb`),
  KEY `revision` (`revisionid`),
  KEY `update_id` (`updateid_package`,`title_short`),
  KEY `validity` (`valided`),
  KEY `daye_calidity` (`validity_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------------------------------------------------
-- CREATE TABLE up_user_gray_list_commentaire
-- this table allows user to add a comment to an update
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS  `up_user_gray_list_commentaire` ( 
  `id` int(11) NOT NULL, 
  `updateid` varchar(36) NOT NULL, 
  `commentaires` varchar(45) DEFAULT NULL, 
  `user` varchar(45) DEFAULT NULL, 
  `creationdate` timestamp NULL DEFAULT current_timestamp(), 
  PRIMARY KEY (`id`), 
  KEY `update` (`updateid`) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------------------------------------------------
-- CREATE TABLE up_machine_windows
-- this table are the updates machine
-- this table contient les updates des machines possible
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `up_machine_windows` (
  `id_machine` int(11) NOT NULL,
  `update_id` varchar(38) NOT NULL,
  `kb` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id_machine`,`update_id`),
  KEY `up_machine_windows_id_machine1_idx` (`id_machine`),
  CONSTRAINT `fk_up_machine_windows_1` FOREIGN KEY (`id_machine`) REFERENCES `machines` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;

-- ----------------------------------------------------------------------
-- CREATE TABLE up_black_list
-- this table exclut ou pas les updates windows
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `up_black_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `updateid_or_kb` varchar(38) NOT NULL COMMENT 'updateid_or_kb  \nkb ou update_id  de la mise à jour.\n update or kb exclude  windows exclude si regexp match',
  `userjid_regexp` varchar(180) NOT NULL COMMENT 'regexp  exclusion sur le user jid :  .* exclude completement cette mise a jour   ^jfk  exclude toute les machine ou le nom commence par jfk ',
  `enable_rule` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'active ou deactive la regle',
  `type_rule` varchar(2) NOT NULL DEFAULT 'id' COMMENT 'type_rule = kb updateid_or_kb represente 1 kb   OU   type_rule updateid_or_kb represente 1 update_id.',
  PRIMARY KEY (`id`),
  KEY `ind_enable` (`enable_rule`),
  KEY `ind_type` (`type_rule`),
  KEY `updatekb` (`updateid_or_kb`) 
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- Drop the procedure
-- drop procedure intit_table_update_data;

-- -------------------------------------------------------
-- cette procedure permet de rechercher les updates pour windows
-- Exemple
-- call up_search_kb_windows( "%Windows 10 Version 21H2 for x64-based%",
--       "5015730,5003791,5012170,5016616,5006753,5007273,5014035,5015895,5005699");
-- 1er parametre le filtre dans title
-- 2eme parametre les kb trouver sur la machine wmic qfe
-- cette procedure renvois les kbs a installer
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_search_kb_windows`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_search_kb_windows`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_search_kb_windows`( in FILTERtable varchar(2048), in KB_LIST varchar(2048))
BEGIN
DECLARE _next TEXT DEFAULT NULL;
DECLARE _nextlen INT DEFAULT NULL;
DECLARE _value TEXT DEFAULT NULL;
DECLARE _list MEDIUMTEXT;
DECLARE kb_next TEXT DEFAULT NULL;
DECLARE kb_nextlen INT DEFAULT NULL;
DECLARE kb_value TEXT DEFAULT NULL;
DECLARE kb_updateid  varchar(50) DEFAULT NULL;
-- declare name table temporaire
DECLARE tmp_kb_updateid varchar(90) DEFAULT "tmp_kb_updateid";
DECLARE tmp_t1 varchar(90) DEFAULT "tmp_t1";
DECLARE tmp_my_mise_a_jour varchar(90) DEFAULT "tmp_my_mise_a_jour";
DECLARE tmp_result_procedure varchar(90) DEFAULT "tmp_result_procedure";

SELECT
    CONCAT('tmp_kb_updateid_',
            REPLACE(UUID(), '-', ''))
INTO tmp_kb_updateid;
SELECT CONCAT('tmp_t1_', REPLACE(UUID(), '-', '')) INTO tmp_t1;
SELECT
    CONCAT('tmp_my_mise_a_jour_',
            REPLACE(UUID(), '-', ''))
INTO tmp_my_mise_a_jour;
SELECT
    CONCAT('tmp_result_procedure_',
            REPLACE(UUID(), '-', ''))
INTO tmp_result_procedure;

CREATE temporary TABLE IF NOT EXISTS `tmp_kb_updateid` (
  `c1` varchar(64) NOT NULL,
  PRIMARY KEY (`c1`),
  UNIQUE KEY `c1_UNIQUE` (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
truncate tmp_kb_updateid;

iteratorkb:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(kb_list)) = 0 OR kb_list IS NULL THEN
    LEAVE iteratorkb;
  END IF;

  -- capture the next value from the list
  SET kb_next = SUBSTRING_INDEX(kb_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET kb_nextlen = CHAR_LENGTH(kb_next);

  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET kb_value = TRIM(kb_next);

  -- insert the extracted value into the target table
  -- select updateid into kb_updateid from xmppmaster.update_data where kb = kb_value;
  -- select kb_updateid;
  INSERT IGNORE INTO tmp_kb_updateid (c1) VALUES (kb_value );

  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes kb_nextlen + 1 characters)
  SET kb_list = INSERT(kb_list,1,kb_nextlen + 1,'');
END LOOP;
-- ------ generation table kb tmp_kb_updateid -----------
-- call list_kb_machine(KBLIST);
-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

-- creation table filter
CREATE temporary TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    xmppmaster.update_data
WHERE
    title LIKE FILTERtable
    and title not like "%Dynamic Cumulative Update%"
    and supersededby in (null,"" ));
SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    tmp_my_mise_a_jour;


CREATE temporary TABLE IF NOT EXISTS `tmp_t1` (
    `c1` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`c1`),
    UNIQUE KEY `c1_UNIQUE` (`c1`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
truncate tmp_t1;
iterator:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(_list)) = 0 OR _list IS NULL THEN
    LEAVE iterator;
  END IF;

  -- capture the next value from the list
  SET _next = SUBSTRING_INDEX(_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET _nextlen = CHAR_LENGTH(_next);
  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET _value = TRIM(_next);
  -- insert the extracted value into the target table
  INSERT IGNORE INTO tmp_t1 (c1) VALUES (_value);
  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes _nextlen + 1 characters)
  SET _list = INSERT(_list,1,_nextlen + 1,'');
END LOOP;
DELETE FROM `tmp_t1`
WHERE
    (`c1` = '');
-- injection les update_id deja installer dans tmp_t1
 INSERT IGNORE INTO tmp_t1  select updateid from xmppmaster.update_data where kb in (select c1 from tmp_kb_updateid);

CREATE temporary TABLE IF NOT EXISTS `tmp_result_procedure` AS (SELECT * FROM
    tmp_my_mise_a_jour
WHERE
    updateid NOT IN (SELECT
            c1
        FROM
            tmp_t1));
-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
DELETE FROM tmp_result_procedure
WHERE
    updateid IN (SELECT
        c1
    FROM
        tmp_kb_updateid);
drop temporary table tmp_kb_updateid;
drop temporary table tmp_t1;
drop temporary table tmp_my_mise_a_jour;
SELECT
    *
FROM
    tmp_result_procedure;
drop temporary table tmp_result_procedure;
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- cette procedure permet de rechercher les updates pour windows
-- plus de parametre de recherche
-- Exemple
-- call up_search_kb_windows1( "","%Windows 10%","%21H2%","Critical","%x64%",
--       "5015730,5003791,5012170,5016616,5006753,5007273,5014035,5015895,5005699");
-- 1er parametre le filtre dans title
-- 2eme parametre les kb trouver sur la machine wmic qfe
-- cette procedure renvois les kbs a installer
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_search_kb_windows1`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_search_kb_windows1`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_search_kb_windows1`( in FILTERtable varchar(2048),
                                           in PRODUCTtable varchar(80),
                                           in VERSIONtable varchar(20),
                                           in MSRSEVERITYtable varchar(40),
                                           in ARCHItable varchar(20),
                                           in KB_LIST varchar(2048))
BEGIN
	DECLARE _next TEXT DEFAULT NULL;
	DECLARE _nextlen INT DEFAULT NULL;
	DECLARE _value TEXT DEFAULT NULL;
	DECLARE _list MEDIUMTEXT;

	DECLARE kb_next TEXT DEFAULT NULL;
	DECLARE kb_nextlen INT DEFAULT NULL;
	DECLARE kb_value TEXT DEFAULT NULL;
	DECLARE kb_updateid  varchar(50) DEFAULT NULL;
	-- declare name table temporaire
	-- tmp_kb_updateid contient les updateid correspondant a la liste klist
	DECLARE tmp_kb_updateid varchar(90) DEFAULT "tmp_kb_updateid";

	DECLARE tmp_t1 varchar(90) DEFAULT "tmp_t1";
	DECLARE tmp_my_mise_a_jour varchar(90) DEFAULT "tmp_my_mise_a_jour";
	DECLARE tmp_result_procedure varchar(90) DEFAULT "tmp_result_procedure";

	DECLARE msrseverity varchar(40) DEFAULT "Critical";
	DECLARE produc_windows varchar(80) DEFAULT '%Windows 10%';
	DECLARE archi varchar(20) DEFAULT "%x64%";
	DECLARE version varchar(20) DEFAULT "%21H2%";
	DECLARE filterp varchar(2048) DEFAULT "%%";
-- attribution de nom aleatoire au table temporaire
-- uuid random des table
SELECT
    CONCAT('tmp_kb_updateid_',
            REPLACE(UUID(), '-', ''))
                        INTO tmp_kb_updateid;

SELECT CONCAT('tmp_t1_', REPLACE(UUID(), '-', ''))
                        INTO tmp_t1;
SELECT
    CONCAT('tmp_my_mise_a_jour_',
            REPLACE(UUID(), '-', ''))
                        INTO tmp_my_mise_a_jour;

SELECT
    CONCAT('tmp_result_procedure_',
            REPLACE(UUID(), '-', ''))
                        INTO tmp_result_procedure;

-- initialise produc_windows Windows 10 si pas ""
if PRODUCTtable  !="" THEN
    SELECT
        CONCAT('%',PRODUCTtable,'%') INTO produc_windows;
END IF;

-- initialise version 21H2 si pas ""
if VERSIONtable !="" THEN
    SELECT
        CONCAT('%',VERSIONtable,'%') INTO version;
END IF;

-- initialise archi 21H2 si pas ""
if ARCHItable !="" THEN
    SELECT
        CONCAT('%',ARCHItable,'%') INTO archi;
END IF;

-- initialise filter %% si ""
if FILTERtable != "" THEN
    SELECT
        CONCAT('%',FILTERtable,'%') INTO filterp;
END IF;

if MSRSEVERITYtable != "" THEN
	SELECT
		CONCAT('%',MSRSEVERITYtable,'%') INTO msrseverity;
END IF;

CREATE temporary TABLE IF NOT EXISTS `tmp_kb_updateid` (
  `c1` varchar(64) NOT NULL,
  PRIMARY KEY (`c1`),
  UNIQUE KEY `c1_UNIQUE` (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
truncate tmp_kb_updateid;

iteratorkb:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(kb_list)) = 0 OR kb_list IS NULL THEN
    LEAVE iteratorkb;
  END IF;

  -- capture the next value from the list
  SET kb_next = SUBSTRING_INDEX(kb_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET kb_nextlen = CHAR_LENGTH(kb_next);

  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET kb_value = TRIM(kb_next);
  -- insert the extracted value into the target table
  -- select updateid into kb_updateid from xmppmaster.update_data where kb = kb_value;
  -- select kb_updateid;
  INSERT IGNORE INTO tmp_kb_updateid (c1) VALUES (kb_value );

  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes kb_nextlen + 1 characters)
  SET kb_list = INSERT(kb_list,1,kb_nextlen + 1,'');
END LOOP;
-- ------ generation table kb tmp_kb_updateid -----------
-- call list_kb_machine(KBLIST);
-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

-- depuis la table general on cree 1 table des mise à jour possible
-- on utilise le filter pour definir filter
-- msrcseverity  uniquement  'Critical'

CREATE temporary TABLE IF NOT EXISTS `tmp_my_mise_a_jour` AS (SELECT * FROM
    xmppmaster.update_data
WHERE
    title LIKE filterp
    and title not like "%Dynamic Cumulative Update%"
    and supersededby in (null,"" )
    AND msrcseverity LIKE msrseverity
    AND product LIKE produc_windows
    AND title LIKE archi
    AND title LIKE version
    );
SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    tmp_my_mise_a_jour;

CREATE temporary TABLE IF NOT EXISTS `tmp_t1` (
    `c1` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`c1`),
    UNIQUE KEY `c1_UNIQUE` (`c1`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
truncate tmp_t1;
iterator:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(_list)) = 0 OR _list IS NULL THEN
    LEAVE iterator;
  END IF;

  -- capture the next value from the list
  SET _next = SUBSTRING_INDEX(_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET _nextlen = CHAR_LENGTH(_next);
  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET _value = TRIM(_next);
  -- insert the extracted value into the target table
  INSERT IGNORE INTO tmp_t1 (c1) VALUES (_value);
  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes _nextlen + 1 characters)
  SET _list = INSERT(_list,1,_nextlen + 1,'');
END LOOP;
DELETE FROM `tmp_t1`
WHERE
    (`c1` = '');
-- injection les update_id deja installer dans tmp_t1
 INSERT IGNORE INTO tmp_t1  select updateid from xmppmaster.update_data where kb in (select c1 from tmp_kb_updateid);

CREATE temporary TABLE `tmp_result_procedure` AS (SELECT * FROM
    tmp_my_mise_a_jour
WHERE
    updateid NOT IN (SELECT
            c1
        FROM
            tmp_t1));
-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
DELETE FROM tmp_result_procedure
WHERE
    updateid IN (SELECT
        c1
    FROM
        tmp_kb_updateid);
drop temporary table tmp_kb_updateid;
drop temporary table tmp_t1;
drop temporary table tmp_my_mise_a_jour;
SELECT
    *
FROM
    tmp_result_procedure;
drop temporary table tmp_result_procedure;

END$$

DELIMITER ;
;
/*
-- ------ generation table kb tmp_kb_updateid -----------
-- call list_kb_machine(KBLIST);
-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

-- depuis la table general on cree 1 table des mise à jour possible
-- on utilise le filter pour definir filter
-- msrcseverity  uniquement  'Critical'

CREATE temporary TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    xmppmaster.update_data
WHERE
    title LIKE filterp
    and title not like "%Dynamic Cumulative Update%"
    and supersededby in (null,"" )
    AND msrcseverity LIKE msrseverity
    AND product LIKE produc_windows
    AND title LIKE archi
    AND title LIKE version
    );
SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    tmp_my_mise_a_jour;

CREATE temporary TABLE IF NOT EXISTS `tmp_t1` (
    `c1` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`c1`),
    UNIQUE KEY `c1_UNIQUE` (`c1`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
truncate tmp_t1;
iterator:
LOOP
  -- exit the loop if the list seems empty or was null;
  -- this extra caution is necessary to avoid an endless loop in the proc.
  IF CHAR_LENGTH(TRIM(_list)) = 0 OR _list IS NULL THEN
    LEAVE iterator;
  END IF;

  -- capture the next value from the list
  SET _next = SUBSTRING_INDEX(_list,',',1);

  -- save the length of the captured value; we will need to remove this
  -- many characters + 1 from the beginning of the string
  -- before the next iteration
  SET _nextlen = CHAR_LENGTH(_next);
  -- trim the value of leading and trailing spaces, in case of sloppy CSV strings
  SET _value = TRIM(_next);
  -- insert the extracted value into the target table
  INSERT IGNORE INTO tmp_t1 (c1) VALUES (_value);
  -- rewrite the original string using the `INSERT()` string function,
  -- args are original string, start position, how many characters to remove,
  -- and what to "insert" in their place (in this case, we "insert"
  -- an empty string, which removes _nextlen + 1 characters)
  SET _list = INSERT(_list,1,_nextlen + 1,'');
END LOOP;
DELETE FROM `tmp_t1`
WHERE
    (`c1` = '');
-- injection les update_id deja installer dans tmp_t1
 INSERT IGNORE INTO tmp_t1  select updateid from xmppmaster.update_data where kb in (select c1 from tmp_kb_updateid);

CREATE temporary TABLE tmp_result_procedure AS (SELECT * FROM
    tmp_my_mise_a_jour
WHERE
    updateid NOT IN (SELECT
            c1
        FROM
            tmp_t1));
-- on supprime les updateid qui sont dans select c1 from tmp_kb_updateid
DELETE FROM tmp_result_procedure
WHERE
    updateid IN (SELECT
        c1
    FROM
        tmp_kb_updateid);
drop temporary table tmp_kb_updateid;
drop temporary table tmp_t1;
drop temporary table tmp_my_mise_a_jour;
SELECT
    *
FROM
    tmp_result_procedure;
drop temporary table tmp_result_procedure;

END$$

DELIMITER ;
;*/


USE `xmppmaster`;
DROP procedure IF EXISTS `update_datetime`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `update_datetime`()
BEGIN
  UPDATE `xmppmaster`.`update_data`
SET
    `creationdate` = STR_TO_DATE(concat(SUBSTRING(title, 1, 7),'-01'),'%Y-%m-%d %h:%i%s')
WHERE
    (`updateid` IN (SELECT
            updateid
        FROM
            update_data
        WHERE
            title REGEXP ('^[0-9]{4}-[0-9]{2} *')));


UPDATE `xmppmaster`.`update_data`
SET
    `title_short` = TRIM(SUBSTR(SUBSTR(title, 9, CHAR_LENGTH(title)),
            1,
            LENGTH(SUBSTR(title, 9, CHAR_LENGTH(title))) - 11))
WHERE
    (`updateid` IN (SELECT
            updateid
        FROM
            update_data
        WHERE
            title REGEXP ('^[0-9]{4}-[0-9]{2} .*\(kB[0-9]{7}\)$')));
END$$

DELIMITER ;

DROP TABLE IF EXISTS `xmppmaster`.`up_offline_arch`;
CREATE TABLE IF NOT EXISTS `xmppmaster`.`up_offline_arch` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `os` VARCHAR(5) NOT NULL,
  `complete` VARCHAR(15) NULL,
  PRIMARY KEY (`id`));

INSERT INTO `xmppmaster`.`up_offline_arch` (`os`, `complete`) VALUES ('x86', 'x86-based');
INSERT INTO `xmppmaster`.`up_offline_arch` (`os`, `complete`) VALUES ('x64', 'x64-based');
INSERT INTO `xmppmaster`.`up_offline_arch` (`os`, `complete`) VALUES ('ARM64', 'ARM64-based');

DROP TABLE IF EXISTS `xmppmaster`.`up_offline_os`;
CREATE TABLE IF NOT EXISTS `xmppmaster`.`up_offline_os` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `os` VARCHAR(45) NULL,
  `version` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `version_UNIQUE` (`version` ASC) );

INSERT INTO `xmppmaster`.`up_offline_os` (`os`) VALUES ('Windows 10');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '21H2');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '21H1');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1607');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1903');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1809');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1803');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '2004');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1511');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1507');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1909');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1709 ');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '20H2');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', '1703');
INSERT INTO `xmppmaster`.`up_offline_os` (`os`, `version`) VALUES ('Windows 10', 'Next');

DROP TABLE IF EXISTS `xmppmaster`.`up_offline_machine`;
CREATE TABLE `up_offline_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `machineid` int(10) NOT NULL,
  `updateid` varchar(38) NOT NULL,
  `kb` varchar(16) NOT NULL DEFAULT '""',
  `file` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_up_offline_machine_ind_idx` (`machineid`),
  CONSTRAINT `fk_up_offline_machine_ind` FOREIGN KEY (`machineid`) REFERENCES `machines` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- -------------------------------------------------------
-- cette procedure permet de genere les table
-- up_download_from_kb and
-- up_download_not_kb
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_table_download_from_kb`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_table_download_from_kb`()
BEGIN
DROP TABLE IF EXISTS `xmppmaster`.`up_download_from_kb`;
create table up_download_from_kb as
(SELECT
    revisionid, updateid, payloadfiles, ckb, kb, dateupdate
FROM
    (SELECT revisionid,
        SUBSTRING_INDEX(SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4), '_', 1) AS ckb,
            SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4, 6) AS kb,
            updateid,
            payloadfiles,
            LEFT( SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '/20', 1)) + 2),7) as dateupdate
    FROM
        xmppmaster.update_data
    WHERE
        payloadfiles LIKE 'http%' ) as ff
        where kb not like ''
);
DROP TABLE IF EXISTS `xmppmaster`.`up_download_not_kb`;
create table up_download_not_kb as
(SELECT
   revisionid,  updateid, payloadfiles, dateupdate
FROM
    (SELECT revisionid,
        SUBSTRING_INDEX(SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4), '_', 1) AS ckb,
            SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '-kb', 1)) + 4, 6) AS kb,
            updateid,
            payloadfiles,
            LEFT( SUBSTRING(payloadfiles, LENGTH(SUBSTRING_INDEX(payloadfiles, '/20', 1)) + 2),7) as dateupdate
    FROM
        xmppmaster.update_data
    WHERE
        payloadfiles LIKE 'http%' ) as ff
        where kb like ''
);
END$$

DELIMITER ;
-- -------------------------------------------------------
-- cette procedure permet de chercher les mise a jour pour les software Malicious
-- parametre  Produit windows, archirexture, major du kb installer, minor du kb installer
-- exemple : call up_windows_malicious_software_tool("Windows 10", "x64", 5, 104);
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_windows_malicious_software_tool`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_windows_malicious_software_tool`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_windows_malicious_software_tool`(in PRODUCTtable varchar(80),
                                                                                 in ARCHItable varchar(20),
                                                                                 in major integer,
                                                                                 in minor integer)
proc_Exit:BEGIN
    DECLARE version varchar(10) DEFAULT NULL;
    DECLARE  titleval varchar(1024) DEFAULT NULL;
    DECLARE major_update INT DEFAULT 0;
    DECLARE minor_update INT DEFAULT 0;
    DECLARE position_str INT DEFAULT 0;
    -- product and architecture
    DECLARE produc_windows varchar(80) DEFAULT '%Windows 10%';
	DECLARE archi varchar(20) DEFAULT "%x64%";
-- initialise produc_windows Windows 10 si pas ""
if PRODUCTtable  !="" THEN
    SELECT
        CONCAT('%',PRODUCTtable,'%') INTO produc_windows;
END IF;
-- initialise archi x64 si pas ""
if ARCHItable !="" THEN
    SELECT
        CONCAT('%',ARCHItable,'%') INTO archi;
END IF;

SELECT
    title
FROM
    xmppmaster.update_data
WHERE
    title LIKE '%Windows Malicious Software Removal Tool%' and
    title LIKE archi
        AND product LIKE produc_windows
ORDER BY revisionid DESC
LIMIT 0 , 1 INTO titleval;

SELECT INSTR(titleval, '- v') INTO position_str;

SELECT SUBSTR(titleval, position_str + 3, 5) INTO version;
SELECT LEFT(version, 2) INTO major_update;
SELECT RIGHT(version, 3) INTO minor_update;

if major > major_update then
	SELECT
    *
FROM
    xmppmaster.update_data
WHERE
    title LIKE '%Windows Malicious Software Removal Tool%' and
    title LIKE archi
        AND product LIKE produc_windows
ORDER BY revisionid DESC
LIMIT 0 , 1;
	LEAVE proc_Exit;
end if;
if minor > minor_update then
	SELECT
    *
FROM
    xmppmaster.update_data
WHERE
    title LIKE '%Windows Malicious Software Removal Tool%'  and
    title LIKE archi
        AND product LIKE produc_windows
ORDER BY revisionid DESC
LIMIT 0 , 1;
    LEAVE proc_Exit;
end if;
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- cette procedure permet de faire le lien entre les update kb et les fichier a recuperer.
-- actuellement restreint a ("Windows 10", "x64", );
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packageid`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packageid`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_packageid`()
BEGIN
	DECLARE is_done INTEGER DEFAULT 0;

	DECLARE c_title varchar(2040)  DEFAULT "";
	DECLARE c_udapeid varchar(2040)  DEFAULT "";
	DECLARE c_kb varchar(2040)  DEFAULT "";
	DECLARE c_revisionid varchar(2040)  DEFAULT "";

  DECLARE client_cursor CURSOR FOR
	  SELECT
		updateid, kb, revisionid, title
	FROM
		xmppmaster.update_data
	WHERE
		product like '%Windows 10%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

  OPEN client_cursor;

  get_list: LOOP
  FETCH client_cursor INTO c_udapeid, c_kb,c_revisionid, c_title;

  IF is_done = 1 THEN
  LEAVE get_list;
  END IF;
SELECT CONCAT('%', c_revisionid, '%') INTO @rev;
SELECT CONCAT('%', c_kb, '%') INTO @kb;

INSERT IGNORE INTO `xmppmaster`.`up_packages`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title,
    updateid, payloadfiles
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND payloadfiles LIKE @kb
        AND supersededby LIKE @rev;

  END LOOP get_list;

  CLOSE client_cursor;
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- -------------------------------------------------------
-- GENERATIONS DES TABLES PRODUIT DEPUIS update_data
-- -------------------------------------------------------
-- -------------------------------------------------------

-- -------------------------------------------------------
-- Cette PROCEDURE GENRE TOUTES LES TABLES PRODUITS.
--
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
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- cette procedure permet searcher kb en utilisant les tables produit
-- call up_search_kb_update("up_packages_Win10_X64_21H2",
--                          "5017022,5003791,5012170,5016616,5006753,5007273");
-- up_packages_Win10_X64_21H2 et la table produit
-- "5017022,5003791,5012170,5016616,5006753,5007273" et 1 sting des kb installer sur la machine
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_search_kb_update`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_search_kb_update`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_search_kb_update`(in tablesearch varchar(1024), in KB_LIST varchar(2048) )
BEGIN
-- on recupere tout les revisions id pour les kb de la machine
set @dd="";
set @rr="";
proc_label:BEGIN
 SET @query = concat("SELECT group_concat(supersededby) into @rr FROM update_data WHERE cast(kb as double) IN (", KB_LIST, ") and supersededby not in ('');");
PREPARE stmt FROM @query;
EXECUTE stmt ;

 IF @rr IS NULL or @rr = "" THEN
      LEAVE proc_label;
  END IF;
-- on conserve seulement les revision id qui sont remplacer

 SET @query = concat("SELECT group_concat(supersededby) into @dd FROM update_data WHERE revisionid IN (", @rr, ") and supersededby not like '';");
 PREPARE stmt FROM @query;
 EXECUTE stmt ;
 IF @dd IS NULL  or @dd = "" THEN
            LEAVE proc_label;
     END IF;
END;

-- on regarde suivant le produit
IF @dd IS NULL  or @dd = "" THEN
         SET @query = concat("SELECT * FROM ", tablesearch, " WHERE 0;");
	else
         SET @query = concat("SELECT * FROM ", tablesearch, " WHERE revisionid IN (",@dd,");");
     END IF;
 -- SET @query = concat("SELECT * FROM ", tablesearch, " WHERE revisionid IN (",@dd,");");
 PREPARE stmt FROM @query;
 EXECUTE stmt ;

END$$

DELIMITER ;
;



-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_office_2003_64bit
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2003_64bit`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_office_2003_64bit`()
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
        product LIKE '%Office 2003%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%'
        AND title NOT LIKE '%Server%'
        AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2003_64bit`;
CREATE TABLE `up_packages_office_2003_64bit` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_office_2003_64bit`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;


-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_office_2007_64bit
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2007_64bit`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_office_2007_64bit`()
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
        product LIKE '%Office 2007%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%'
        AND title NOT LIKE '%Server%'
        AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2007_64bit`;
CREATE TABLE `up_packages_office_2007_64bit` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_office_2007_64bit`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;

-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_office_2010_64bit
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2010_64bit`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_office_2010_64bit`()
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
        product LIKE '%Office 2010%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%'
        AND title NOT LIKE '%Server%'
        AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2010_64bit`;
CREATE TABLE `up_packages_office_2010_64bit` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_office_2010_64bit`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;


-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_office_2013_64bit
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2013_64bit`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_packages_office_2013_64bit`()
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
        product LIKE '%Office 2013%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%'
        AND title NOT LIKE '%Server%'
        AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2013_64bit`;
CREATE TABLE `up_packages_office_2013_64bit` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_office_2013_64bit`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;


-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_office_2016_64bit
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_office_2016_64bit`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_office_2016_64bit`()
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
        product LIKE '%Office 2016%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%32-Bit%'
        AND title NOT LIKE '%Server%'
        AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_office_2016_64bit`;
CREATE TABLE `up_packages_office_2016_64bit` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_office_2016_64bit`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;






-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Vstudio_2005
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2005`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2005`()
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
        product LIKE '%Visual Studio 2005%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2005`;
CREATE TABLE `up_packages_Vstudio_2005` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2005`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;



-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Vstudio_2008
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2008`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2008`()
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
        product LIKE '%Visual Studio 2008%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2008`;
CREATE TABLE `up_packages_Vstudio_2008` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2008`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;

-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Vstudio_2010
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2010`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2010`()
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
        product LIKE '%Visual Studio 2010%';
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2010`;
CREATE TABLE `up_packages_Vstudio_2010` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2010`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;

-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Vstudio_2012
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2012`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2012`()
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
        product LIKE '%Visual Studio 2012%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2012`;
CREATE TABLE `up_packages_Vstudio_2012` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2012`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;


-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Vstudio_2013
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2013`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2013`()
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
        product LIKE '%Visual Studio 2013%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2013`;
CREATE TABLE `up_packages_Vstudio_2013` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2013`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;



-- -------------------------------------------------------
-- TABLES PRODUIT up_packages_Vstudio_2015
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Vstudio_2015`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_packages_Vstudio_2015`()
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
        product LIKE '%Visual Studio 2015%';
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2015`;
CREATE TABLE `up_packages_Vstudio_2015` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2015`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- TABLES PRODUIT up_packages_Vstudio_2017
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2017`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2017`()
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
        product LIKE '%Visual Studio 2017%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2017`;
CREATE TABLE `up_packages_Vstudio_2017` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2017`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;

-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Vstudio_2019
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2019`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2019`()
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
        product LIKE '%Visual Studio 2019%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2019`;
CREATE TABLE `up_packages_Vstudio_2019` (
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
INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2019`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;
-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Vstudio_2022
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Vstudio_2022`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Vstudio_2022`()
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
        product LIKE '%Visual Studio 2022%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Vstudio_2022`;
CREATE TABLE `up_packages_Vstudio_2022` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Vstudio_2022`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;

-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Win10_X64_1903
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win10_X64_1903`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_packages_Win10_X64_1903`()
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
    title LIKE '%Version 1903%'
    AND product LIKE '%Windows 10, version 1903 and later%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
drop tables if exists `up_packages_Win10_X64_1903`;
CREATE TABLE `up_packages_Win10_X64_1903` (
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
INSERT IGNORE INTO `xmppmaster`.`up_packages_Win10_X64_1903`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
--        AND payloadfiles LIKE @kb
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;
;


-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Win10_X64_21H1
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win10_X64_21H1`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Win10_X64_21H1`()
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
    title LIKE '%21H1%'
    AND (product LIKE '%Windows 10, version 1903 and later%'
        OR product LIKE '%Windows 10 and later GDR-DU%')
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Win10_X64_21H1`;
CREATE TABLE `up_packages_Win10_X64_21H1` (
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

INSERT IGNORE INTO `xmppmaster`.`up_packages_Win10_X64_21H1`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;


-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Win10_X64_21H2
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win10_X64_21H2`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win10_X64_21H2`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_packages_Win10_X64_21H2`()
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
    title LIKE '%21H2%'
    AND (product LIKE '%Windows 10, version 1903 and later%'
        OR product LIKE '%Windows 10 and later GDR-DU%')
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
drop tables if exists `up_packages_Win10_X64_21H2`;
CREATE TABLE `up_packages_Win10_X64_21H2` (
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

-- INSERT IGNORE INTO `xmppmaster`.`up_packages_Win10_X64`
-- SELECT
--    c_udapeid, c_kb,c_revisionid, c_title, c_description,
--    updateid, payloadfiles
-- FROM
--    xmppmaster.update_data
-- WHERE
--    payloadfiles NOT IN ('')
--        AND payloadfiles LIKE @kb
--        AND supersededby LIKE @rev;
INSERT IGNORE INTO `xmppmaster`.`up_packages_Win10_X64_21H2`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Win11_X64
-- -------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win11_X64`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `up_init_packages_Win11_X64`()
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
    product LIKE '%Windows 11%'
		AND title NOT LIKE '%ARM64%'
		AND title NOT LIKE '%X86%'
        AND title not like '%Dynamic%';

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;

drop tables if exists `up_packages_Win11_X64`;
CREATE TABLE `up_packages_Win11_X64` (
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
INSERT IGNORE INTO `xmppmaster`.`up_packages_Win11_X64`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;
;

-- -------------------------------------------------------
-- TABLES PRODUIT up_init_packages_Win_Malicious_X64
-- -------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_packages_Win_Malicious_X64`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_packages_Win_Malicious_X64`()
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
		title LIKE '%Windows Malicious Software Removal Tool x64%'
		and product like '%Windows 1%'
		ORDER BY revisionid DESC;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET is_done = 1;
drop tables if exists `up_packages_Win_Malicious_X64`;
CREATE TABLE `up_packages_Win_Malicious_X64` (
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
INSERT IGNORE INTO `xmppmaster`.`up_packages_Win_Malicious_X64`
SELECT
    c_udapeid, c_kb,c_revisionid, c_title, c_description,
    updateid, payloadfiles, supersededby,creationdate,title_short
FROM
    xmppmaster.update_data
WHERE
    payloadfiles NOT IN ('')
        AND supersededby LIKE @rev;
--        AND payloadfiles LIKE @kb
  END LOOP get_list;

        -- AND payloadfiles LIKE @kb
  CLOSE client_cursor;
END$$

DELIMITER ;
-- -------------------------------------------------------
-- cette procedure diminue la taille de la table update
-- -------------------------------------------------------
USE `base_wsusscn2`;
DROP procedure IF EXISTS `reduction_base`;

USE `base_wsusscn2`;
DROP procedure IF EXISTS `base_wsusscn2`.`reduction_base`;
;

DELIMITER $$
USE `base_wsusscn2`$$
CREATE DEFINER=`jfk`@`localhost` PROCEDURE `reduction_base`()
BEGIN

DELETE FROM `base_wsusscn2`.`update_data`
WHERE
    (`product` IN (' ; Windows XP x64 Edition' , ' ; Windows XP Embedded',
    ' ; Windows XP',
    ' ; Windows Vista',
    ' ; Windows Embedded Standard 7',
    ' ; Windows 7 ; Windows Embedded Standard 7',
    ' ; Windows 7'));
END$$

DELIMITER ;
;
-- -------------------------------------------------------
-- list produits actifs
-- -------------------------------------------------------

USE `xmppmaster`;
CREATE TABLE `up_list_produit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_procedure` varchar(80) DEFAULT NULL,
  `enable` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2008');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2010');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2012');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2013');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2015');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2017');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2019');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Vstudio_2022');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win10_X64_1903');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win10_X64_21H1');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win10_X64_21H2');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win11_X64');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_Win_Malicious_X64');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_office_2003_64bit');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_office_2007_64bit');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_office_2010_64bit');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_office_2013_64bit');
INSERT INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_packages_office_2016_64bit');

-- -------------------------------------------------------
-- Quick action to disable Windows updates
-- -------------------------------------------------------

INSERT INTO `xmppmaster`.`qa_custom_command` VALUES ('allusers','windows','Disable Windows Updates','REG ADD "HKLM\\Software\\Policies\\Microsoft\\Windows\\Windows\ Update" /f && REG ADD "HKLM\\Software\\Policies\\Microsoft\\Windows\\Windows\ Update\\AU" /f && REG ADD "HKLM\\Software\\Policies\\Microsoft\\Windows\\Windows\ Update\\AU" /v AUOptions /t REG_DWORD /d 2 /f && sc config "wuauserv" start=disabled && net stop wuauserv','Disable Windows Updates');

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 73;

COMMIT;
