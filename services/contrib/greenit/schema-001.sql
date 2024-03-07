--
-- (c) 2023 Siveo, http://www.siveo.net/
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
-- Database greenit
-- ----------------------------------------------------------------------

START TRANSACTION;

--
-- Table structure for table `version`
--

CREATE TABLE if not exists `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for profils
--

CREATE TABLE IF NOT EXISTS `tests` (
        `id` int NOT NULL AUTO_INCREMENT, PRIMARY KEY(`id`),
        `name` varchar(50) NOT NULL,
        `message` varchar(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Crée la table `consommation_generale` depuis la base xmppmaster.
-- Cette table permet de reunir les informations de consomation des machines.
-- ----------------------------------------------------------------------
DROP TABLE IF EXISTS `greenit`.`consommation_generale;
CREATE TABLE IF NOT EXISTS `greenit`.`consommation_generale` (
  `hostname` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `year` int(4) DEFAULT NULL,
  `month` int(2) DEFAULT NULL,
  `date_start` datetime DEFAULT NULL,
  `date_end` datetime DEFAULT NULL,
  `puissance_total` double DEFAULT NULL,
  `charge_reelle` double DEFAULT NULL,
  `cpu_freq` double DEFAULT NULL,
  `temperature` double DEFAULT NULL,
  `puissance_cpu_gpu` double DEFAULT NULL,
  `energie` float DEFAULT 0,
  `nb_mesure` int(11) DEFAULT 0,
  `platform` varchar(60) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `archi` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `glpi_entity_id` int(11) DEFAULT 1,
  `model` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT '',
  `manufacturer` varchar(45) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT '',
  `complete_name` varchar(512) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `glpi_id` int(11) NOT NULL,
  `cpu` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL COMMENT 'modele cpu ',
  `nbr_cpu` int(11) DEFAULT 1,
  `cpu_hertz_max` int(11) DEFAULT NULL COMMENT 'frequence maximun\\n',
  `cpu_herz` int(11) DEFAULT NULL COMMENT 'frequence courante\\n',
  `gpu` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `nbr_gpu` int(11) DEFAULT NULL,
  `memorytype` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT 'DDR4' COMMENT 'type de memoire',
  `memorysize` int(11) DEFAULT 4 COMMENT 'taille memoire',
  `formfactor` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT 'desktop' COMMENT 'type d''ordinateur :desktop ordinateur bureau__laptop ordinateur portable \n',
  `nbr_HDD` int(11) DEFAULT 1 COMMENT 'nombre de disks HDD',
  `nbr_SSD` int(11) DEFAULT 0 COMMENT 'nombre de disks SSD',
  `monitor` varchar(100) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `nbr_monitor` int(11) DEFAULT 1,
  `timeac` int(11) DEFAULT 300,
  `timedc` int(11) DEFAULT 180,
  `PROC_MAX_AC` int(11) DEFAULT 0,
  `PROC_MAX_DC` int(11) DEFAULT 0,
  `PROC_MIN_AC` int(11) DEFAULT 0,
  `PROC_MIN_DC` int(11) DEFAULT 0,
  `biosdate` datetime DEFAULT NULL,
  `core` int(11) DEFAULT 0,
  `thread` int(11) DEFAULT NULL,
  `TDP` int(11) DEFAULT NULL,
  `osmax` varchar(20) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `freq_doccpu` int(11) DEFAULT NULL,
  `uuid` varchar(36) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  UNIQUE KEY `idx_uniq_start_uuid` (`uuid`,`date_start`),
  KEY `idx_hostname` (`hostname`),
  KEY `idx_year` (`year`),
  KEY `idx_month` (`month`),
  KEY `idx_datestart` (`date_start`),
  KEY `idx_dateend` (`date_end`),
  KEY `idx_puissance_total` (`puissance_total`),
  KEY `idx_charge_reelle` (`charge_reelle`),
  KEY `idx_cpu_freq` (`cpu_freq`),
  KEY `idx_temperature` (`temperature`),
  KEY `idx_puissance_cpu_gpu` (`puissance_cpu_gpu`),
  KEY `idx_energie` (`energie`),
  KEY `idx_nb_mesure` (`nb_mesure`),
  KEY `idx_platform` (`platform`),
  KEY `idx_archi` (`archi`),
  KEY `idx_glpi_entity_id` (`glpi_entity_id`),
  KEY `idx_model` (`model`),
  KEY `idx_manufacturer` (`manufacturer`),
  KEY `idx_complete_name` (`complete_name`),
  KEY `idx_glpi_id` (`glpi_id`),
  KEY `idx_cpu` (`cpu`),
  KEY `idx_nbr_cpu` (`nbr_cpu`),
  KEY `idx_cpu_hertz_max` (`cpu_hertz_max`),
  KEY `idx_cpu_herz` (`cpu_herz`),
  KEY `idx_gpu` (`gpu`),
  KEY `idx_nbr_gpu` (`nbr_gpu`),
  KEY `idx_memorytype` (`memorytype`),
  KEY `idx_memorysize` (`memorysize`),
  KEY `idx_formfactor` (`formfactor`),
  KEY `idx_nbr_HDD` (`nbr_HDD`),
  KEY `idx_nbr_SSD` (`nbr_SSD`),
  KEY `idx_monitor` (`monitor`),
  KEY `idx_nbr_monitor` (`nbr_monitor`),
  KEY `idx_timeac` (`timeac`),
  KEY `idx_timedc` (`timedc`),
  KEY `idx_PROC_MAX_AC` (`PROC_MAX_AC`),
  KEY `idx_PROC_MAX_DC` (`PROC_MAX_DC`),
  KEY `idx_PROC_MIN_AC` (`PROC_MIN_AC`),
  KEY `idx_PROC_MIN_DC` (`PROC_MIN_DC`),
  KEY `idx_biosdate` (`biosdate`),
  KEY `idx_core` (`core`),
  KEY `idx_thread` (`thread`),
  KEY `idx_TDP` (`TDP`),
  KEY `idx_osmax` (`osmax`),
  KEY `idx_freq_doccpu` (`freq_doccpu`),
  KEY `idx_uuid` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ---------------------------------------------------------------------------------
-- --------------- scheduled_update_consommation_generale_after_date ---------------
-- Procedure to update the consommation_generale table after a specific date
-- cette procedure doit etre appeller regulierement.
-- elle a pour but d'inclure des enregistrements contenue dans xmppmaster
-- la date entree sera pour limiter la tentative de mettre a jour des enregistrements deja existant
-- exemple appel
-- CALL scheduled_update_consommation_generale_after_date(DATE_SUB(NOW(), INTERVAL 8 DAY));
-- CALL scheduled_update_consommation_generale_after_date( DATE_SUB(CURDATE(), INTERVAL 120 DAY));
-- CALL scheduled_update_consommation_generale_after_date(2024-03-01 10:35:11');
-- ---------------------------------------------------------------------------------

USE `greenit`;
DROP procedure IF EXISTS `scheduled_update_consommation_generale_after_date`;

USE `greenit`;
DROP procedure IF EXISTS `greenit`.`scheduled_update_consommation_generale_after_date`;
;

DELIMITER $$
USE `greenit`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `scheduled_update_consommation_generale_after_date`(IN datestart DATETIME)
BEGIN
-- Procedure to update the consommation_generale table after a specific date
INSERT IGNORE INTO greenit.consommation_generale (
    hostname,
    year,
    month,
    date_start,
    date_end,
    puissance_total,
    charge_reelle,
    cpu_freq,
    temperature,
    puissance_cpu_gpu,
    energie,
    nb_mesure,
    platform,
    archi,
    glpi_entity_id,
    model,
    manufacturer,
    complete_name,
    glpi_id,
    cpu,
    nbr_cpu,
    cpu_hertz_max,
    cpu_herz,
    gpu,
    nbr_gpu,
    memorytype,
    memorysize,
    formfactor,
    nbr_HDD,
    nbr_SSD,
    monitor,
    nbr_monitor,
    timeac,
    timedc,
    PROC_MAX_AC,
    PROC_MAX_DC,
    PROC_MIN_AC,
    PROC_MIN_DC,
    biosdate,
    core,
    thread,
    TDP,
    osmax,
    freq_doccpu,
    uuid
)
SELECT
    macht.hostname AS hostname,
    YEAR(greent.date_start) AS year,
    MONTH(greent.date_start) AS month,
    greent.date_start,
    greent.date_end,
    greent.puissance_total,
    greent.charge_reelle,
    greent.cpu_freq,
    greent.temperature,
    greent.puissance_cpu_gpu,
    greent.energie,
    greent.nb_mesure,
    macht.platform,
    macht.archi,
    macht.glpi_entity_id,
    macht.model,
    macht.manufacturer,
    glpit.complete_name,
    glpit.glpi_id,
    greenmt.cpu,
    greenmt.nbr_cpu,
    greenmt.cpu_hertz_max,
    greenmt.cpu_herz,
    greenmt.gpu,
    greenmt.nbr_gpu,
    greenmt.memorytype,
    greenmt.memorysize,
    greenmt.formfactor,
    greenmt.nbr_HDD,
    greenmt.nbr_SSD,
    greenmt.monitor,
    greenmt.nbr_monitor,
    greenmt.timeac,
    greenmt.timedc,
    greenmt.PROC_MAX_AC,
    greenmt.PROC_MAX_DC,
    greenmt.PROC_MIN_AC,
    greenmt.PROC_MIN_DC,
    greenmt.biosdate,
    greenmt.core,
    greenmt.thread,
    greenmt.TDP,
    greenmt.osmax,
    greenmt.freq_doccpu,
    greent.uuid
FROM
    xmppmaster.green_conso greent
INNER JOIN
    xmppmaster.machines macht ON macht.uuid_serial_machine = greent.uuid
INNER JOIN
    xmppmaster.glpi_entity glpit ON glpit.id = macht.glpi_entity_id
INNER JOIN
    xmppmaster.green_machine greenmt ON greenmt.uuid_machine = macht.uuid_serial_machine
WHERE
    greent.date_start > datestart ;
END$$

DELIMITER ;
;

CREATE DEFINER=`root`@`localhost` PROCEDURE `create_table_search1`(IN annee INT, IN mois INT, in id_entity_machine INT)
BEGIN
    IF annee = -1 AND mois = -1 AND id_entity_machine = -1 THEN
        -- Si tous les paramètres sont -1, sélectionnez tous les enregistrements
        SELECT *
        FROM greenit.consommation_generale;
    ELSE
        -- Sinon, filtrez selon les valeurs spécifiées des paramètres
        SELECT *
        FROM greenit.consommation_generale
        WHERE
            (annee = -1 OR `YEAR` = annee) AND
            (mois = -1 OR `MONTH` = mois) AND
            (id_entity_machine = -1 OR glpi_entity_id = id_entity_machine);
    END IF;
END
-- ---------------------------------------------------------------------------------
-- ----------------------------- EVENT TOUTE LES HEURES ----------------------------
-- ------------- call scheduled_update_consommation_generale_after_date ------------
-- on mais a jour la table greenit.consommation_generale toutes les heures.
-- ---------------------------------------------------------------------------------

DELIMITER $$
DROP EVENT IF EXISTS CONSO_MACHINE;
CREATE EVENT IF NOT EXISTS conso_machine
    ON SCHEDULE
        EVERY 1 HOUR
        STARTS CURRENT_TIMESTAMP
    DO
    BEGIN
        CALL scheduled_update_consommation_generale_after_date(DATE_SUB(NOW(), INTERVAL 4 HOUR));
    END$$
DELIMITER ;

-- ---------------------------------------------------------------------------------
-- ----------------------------- EVENT TOUTE LES semaines ----------------------------
-- ------------- call scheduled_update_consommation_generale_after_date ------------
-- on mais a jour la table greenit.consommation_generale toutes les semaines a 5heure le dimanche
-- call la procedure toutes les semaines et insert ou ignore 2 semaines d'enregistrement
-- ---------------------------------------------------------------------------------

DELIMITER $$
DROP EVENT IF EXISTS CONSO_MACHINE;
CREATE EVENT IF NOT EXISTS conso_machine
    ON SCHEDULE
        EVERY 1 WEEK
        STARTS TIMESTAMP(DATE_ADD(NOW(), INTERVAL 1 DAY) + INTERVAL (7 - WEEKDAY(NOW() + INTERVAL 1 DAY) + 1) DAY + INTERVAL 5 HOUR)
    DO
    BEGIN
        CALL scheduled_update_consommation_generale_after_date(DATE_SUB(NOW(), INTERVAL 15 Day));
    END$$
DELIMITER ;


USE `greenit`;
DROP procedure IF EXISTS `genere_tables`;

USE `greenit`;
DROP procedure IF EXISTS `greenit`.`genere_tables`;
;

DELIMITER $$
USE `greenit`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `genere_tables`()
BEGIN
# genere des table conso
call generation_charge_moi1();
call generation_kwh_moi1();
call generation_prix_conso_moi1();
END$$

DELIMITER ;
;



USE `greenit`;
DROP procedure IF EXISTS `generation_charge_moi1`;

USE `greenit`;
DROP procedure IF EXISTS `greenit`.`generation_charge_moi1`;
;

DELIMITER $$
USE `greenit`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `generation_charge_moi1`()
BEGIN
    DECLARE debut_annee DATE;
    DECLARE fin_annee DATE;
    DECLARE annee_val INT;
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR SELECT DISTINCT(YEAR(`date_start`)) AS `Annee` FROM xmppmaster.green_conso;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO annee_val;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET debut_annee = STR_TO_DATE(CONCAT(annee_val, '-01-01'), '%Y-%m-%d');
        SET fin_annee = STR_TO_DATE(CONCAT(annee_val, '-12-31'), '%Y-%m-%d');

        SET @table_name = CONCAT('charge_mois_', annee_val);

        -- Drop the table if it exists
        SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', @table_name);
        PREPARE drop_stmt FROM @drop_query;
        EXECUTE drop_stmt;
        DEALLOCATE PREPARE drop_stmt;

        -- Create the new table
        SET @create_query = CONCAT('CREATE TABLE ', @table_name, ' AS
            SELECT
                MONTHNAME(date_start) AS month,
                AVG(charge_reelle) AS charge
            FROM
                xmppmaster.green_conso
            INNER JOIN
                xmppmaster.machines
            ON
                xmppmaster.machines.uuid_serial_machine = xmppmaster.green_conso.uuid
            WHERE
                YEAR(date_start) = ', annee_val, '
            GROUP BY
                MONTH(date_start)'); --  WITH ROLLUP
        PREPARE create_stmt FROM @create_query;
        EXECUTE create_stmt;
        DEALLOCATE PREPARE create_stmt;

    END LOOP;
    CLOSE cur;
END$$

DELIMITER ;
;

USE `greenit`;
DROP procedure IF EXISTS `generation_kwh_moi1`;

USE `greenit`;
DROP procedure IF EXISTS `greenit`.`generation_kwh_moi1`;
;

DELIMITER $$
USE `greenit`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `generation_kwh_moi1`()
BEGIN
    DECLARE debut_annee DATE;
    DECLARE fin_annee DATE;
    DECLARE annee_val INT;
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR SELECT DISTINCT(YEAR(`date_start`)) AS `Annee` FROM xmppmaster.green_conso;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO annee_val;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET debut_annee = STR_TO_DATE(CONCAT(annee_val, '-01-01'), '%Y-%m-%d');
        SET fin_annee = STR_TO_DATE(CONCAT(annee_val, '-12-31'), '%Y-%m-%d');

        SET @table_name = CONCAT('kws_mois_', annee_val);

        -- Drop the table if it exists
        SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', @table_name);
        PREPARE drop_stmt FROM @drop_query;
        EXECUTE drop_stmt;
        DEALLOCATE PREPARE drop_stmt;

        -- Create the new table
        SET @create_query = CONCAT('CREATE TABLE ', @table_name, ' AS
            SELECT
                MONTHNAME(date_start) AS month,
                SUM(energie) AS total_energy
            FROM
                xmppmaster.green_conso
            INNER JOIN
                xmppmaster.machines
            ON
                xmppmaster.machines.uuid_serial_machine = xmppmaster.green_conso.uuid
            WHERE
                YEAR(date_start) = ', annee_val, '
            GROUP BY
                MONTH(date_start)'); --  WITH ROLLUP
        PREPARE create_stmt FROM @create_query;
        EXECUTE create_stmt;
        DEALLOCATE PREPARE create_stmt;

    END LOOP;
    CLOSE cur;
END$$

DELIMITER ;
;

USE `greenit`;
DROP procedure IF EXISTS `generation_prix_conso_moi1`;

USE `greenit`;
DROP procedure IF EXISTS `greenit`.`generation_prix_conso_moi1`;
;

DELIMITER $$
USE `greenit`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `generation_prix_conso_moi1`()
BEGIN
    DECLARE debut_annee DATE;
    DECLARE fin_annee DATE;
    DECLARE annee_val INT;
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR SELECT DISTINCT(YEAR(`date_start`)) AS `Annee` FROM xmppmaster.green_conso;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO annee_val;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET debut_annee = STR_TO_DATE(CONCAT(annee_val, '-01-01'), '%Y-%m-%d');
        SET fin_annee = STR_TO_DATE(CONCAT(annee_val, '-12-31'), '%Y-%m-%d');

        SET @table_name = CONCAT('cout_mois_', annee_val);

        -- Drop the table if it exists
        SET @drop_query = CONCAT('DROP TABLE IF EXISTS ', @table_name);
        PREPARE drop_stmt FROM @drop_query;
        EXECUTE drop_stmt;
        DEALLOCATE PREPARE drop_stmt;

        -- Create the new table
        SET @create_query = CONCAT('CREATE TABLE ', @table_name, ' AS
            SELECT
                MONTHNAME(date_start) AS month,
                (SUM(energie)/1000) * 0.22 AS cout
            FROM
                xmppmaster.green_conso
            INNER JOIN
                xmppmaster.machines
            ON
                xmppmaster.machines.uuid_serial_machine = xmppmaster.green_conso.uuid
            WHERE
                YEAR(date_start) = ', annee_val, '
            GROUP BY
                MONTH(date_start)'); --  WITH ROLLUP
        PREPARE create_stmt FROM @create_query;
        EXECUTE create_stmt;
        DEALLOCATE PREPARE create_stmt;

    END LOOP;
    CLOSE cur;
END$$

DELIMITER ;
;
USE `greenit`;
DROP procedure IF EXISTS `_private_split_name_computer`;

USE `greenit`;
DROP procedure IF EXISTS `greenit`.`_private_split_name_computer`;
;

DELIMITER $$
USE `greenit`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `_private_split_name_computer`(IN chaine VARCHAR(255), IN tempTableName VARCHAR(255))
BEGIN

   DECLARE done INT DEFAULT 0;
   DECLARE element VARCHAR(255);
   DECLARE curPosition INT DEFAULT 1;
   DECLARE countline INT DEFAULT 0;
    -- Construction de la commande DROP TABLE dynamiquement
   SET @dropStatement = CONCAT('DROP TEMPORARY TABLE IF EXISTS ', tempTableName);
    -- Exécution de la commande DROP TABLE
    PREPARE stmt FROM @dropStatement;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    -- Créer la table temporaire TEMPORARYTEMPORARY
    SET @createTableStatement = CONCAT('CREATE TEMPORARY TABLE ', tempTableName, ' (
        id INT AUTO_INCREMENT PRIMARY KEY,
        value VARCHAR(255)
    )');
    PREPARE stmt FROM @createTableStatement;
    EXECUTE stmt;
    DEALLOCATE PREPARE stmt;
    -- Tant que nous n'avons pas parcouru toute la chaîne
    WHILE NOT done DO
        -- Trouver la position du prochain espace
        SET curPosition = LOCATE(' ', chaine, curPosition);
        -- Si aucun espace n'est trouvé, cela signifie que nous sommes à la fin de la chaîne
        IF curPosition = 0 THEN
			IF not(TRIM(element) = 'Core(TM)' OR
				TRIM(element) REGEXP '[0-9][0-9]th' OR
				element LIKE '%Intel(R)%' OR
				LENGTH(TRIM(element)) = 1 OR
				element LIKE '%GHz%' OR
				element = 'GEN') THEN
				  SET @insertStatement = CONCAT('INSERT INTO ', tempTableName, ' (value) VALUES (\'',element,'\')');
					PREPARE stmt FROM @insertStatement;
					EXECUTE stmt;
					DEALLOCATE PREPARE stmt;
			END IF;
            SET done = 1;
        ELSE
            -- Extraire l'élément entre la position actuelle et la position de l'espace
            SET element = LEFT(chaine, curPosition);
            set chaine = RIGHT(chaine, CHAR_LENGTH(chaine) - curPosition );
            set curPosition = 1;
			-- Insérer l'élément dans la table temporaire
			IF not(TRIM(element) = 'Core(TM)' OR
				TRIM(element) REGEXP '[0-9][0-9]th' OR
				element LIKE '%Intel(R)%' OR
				LENGTH(TRIM(element)) = 1 OR
				element LIKE '%GHz%' OR
				element = 'GEN') THEN
                SET @insertStatement = CONCAT('INSERT INTO ', tempTableName, ' (value) VALUES (\'',element,'\')');
				PREPARE stmt FROM @insertStatement;
				EXECUTE stmt;
				DEALLOCATE PREPARE stmt;
			END IF;
        END IF;
    END WHILE;
END$$

DELIMITER ;
;



-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
INSERT INTO `version` VALUES (1);

COMMIT;
