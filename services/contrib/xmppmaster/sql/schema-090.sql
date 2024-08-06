-- -*- coding: utf-8; -*-
-- SPDX-FileCopyrightText: 2022-2024 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

START TRANSACTION;

USE `xmppmaster`;
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
-- Génération de noms uniques pour les tables temporaires dans la procedure. si concurence.
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

-- -----------------------------------------------------------------------
-- Création de la table temporaire tmp_kb_updateid pour stocker les KB
CREATE temporary TABLE IF NOT EXISTS tmp_kb_updateid (
  `c1` varchar(64) NOT NULL,
  PRIMARY KEY (`c1`),
  UNIQUE KEY `c1_UNIQUE` (`c1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ;
truncate tmp_kb_updateid;
-- -----------------------------------------------------------------------
-- Boucle pour remplir la table tmp_kb_updateid avec les KB de KB_LIST
-- on split kb_list passer en parametre separe par des virgules.
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

-- tmp_kb_updateid a les kb installer sur la machine 1 par ligne
-- -----------------------------------------------------------------------
-- ------ generation table kb tmp_kb_updateid -----------
-- Création de la table temporaire tmp_my_mise_a_jour pour stocker les mises à jour filtrées
-- on extrait de la table update_data tout les enregistrement consernant le titre produit (exemple "up_packages_Win_Malicious_X64")
-- seulement ceux qui sont a mettre a jour c'est a dire qui ne sont pas Dynamic Cumulative Update
-- and que supersededby soit null ou vide se qui indique que le kb a 1 mise a jour.
-- les updatesid des mise a jour deja installer seront inclus dans la table des update excluts tmp_t1

-- creation table filter
CREATE temporary TABLE IF NOT EXISTS tmp_my_mise_a_jour AS (SELECT * FROM
    xmppmaster.update_data
WHERE
    title LIKE FILTERtable
    and title not like "%Dynamic Cumulative Update%"
    and supersededby in (null,"" ));
--  tmp_my_mise_a_jour est 1 partie de update_data et peut etre vide.
-- -----------------------------------------------------------------------
-- la concatenation des champs supersedes separes par des virguls
-- donne la liste de tout les uuid de package a installe sur la machine.

-- on doit traite tout les elements de cette list en string
-- on split sur la virgule cette chaine dans 1 table temporaire tmp_t1.

SELECT
    GROUP_CONCAT(DISTINCT supersedes
        ORDER BY supersedes ASC
        SEPARATOR ',')
INTO _list FROM
    tmp_my_mise_a_jour;
-- _list est 1 chaine de caractere donnant les packages uuid a installer.
-- -----------------------------------------------------------------------
CREATE temporary TABLE IF NOT EXISTS tmp_t1 (
    `c1` VARCHAR(64) NOT NULL,
    PRIMARY KEY (`c1`),
    UNIQUE KEY `c1_UNIQUE` (`c1`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;
truncate tmp_t1;
--  on split , dans tmp_t1
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




DELETE FROM tmp_t1
WHERE `c1` = '' OR `c1` IS NULL;

-- injection les update_id deja installer dans tmp_t1

-- tout les package uuid a mettre a jour sont dans la table tmp_t1 cette table peut etre vide.
-- on ajoute a tmp_t1 tout les id de package des kb remonte par la machine.

 INSERT IGNORE INTO tmp_t1  select updateid from xmppmaster.update_data where kb in (select c1 from tmp_kb_updateid);
-- -------------------------------------------------------------------------------
-- resultat
-- on travaille sur tmp_my_mise_a_jour qui est 1 partie de update_data avec seulement se qui conserne notre produit titre a mettre a jour
--
CREATE temporary TABLE IF NOT EXISTS tmp_result_procedure AS (SELECT * FROM
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
-- on renvoi la table
SELECT
    *
FROM
    tmp_result_procedure;
drop temporary table tmp_result_procedure;
END$$

DELIMITER ;
;

-- new view to simplify the querying on up_machine_windows
-- join some machine info, and allow to avoid the gray_list / white_list join on requests
DROP VIEW IF EXISTS up_machine_activated;
CREATE VIEW IF NOT EXISTS up_machine_activated AS(
  SELECT 
    (CASE WHEN ugl.kb IS NULL THEN uwl.kb ELSE ugl.kb END) AS kb,
    id_machine,
    substr(m.uuid_inventorymachine, 5) AS glpi_id,
    m.hostname,
    m.jid,
    lgm.entities_id AS entities_id,
    update_id,
    curent_deploy, 
    required_deploy, 
    start_date, 
    end_date, 
    intervals, 
    msrcseverity,
    (CASE WHEN uwl.kb IS NULL THEN "gray" ELSE "white" END) AS list
  FROM up_machine_windows umw
  JOIN machines m ON m.id = umw.id_machine
  JOIN local_glpi_machines lgm ON CONCAT("UUID",lgm.id) = m.uuid_inventorymachine
  LEFT JOIN up_white_list uwl ON uwl.updateid = umw.update_id
  LEFT JOIN up_gray_list ugl ON ugl.updateid = umw.update_id
  WHERE (ugl.valided = 1 OR uwl.valided=1)
  AND lgm.is_deleted =0 AND lgm.is_template=0
);


UPDATE version SET Number = 90;

COMMIT;
