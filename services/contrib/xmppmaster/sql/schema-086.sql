-- SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

-- ---------------------------------------------------------
-- ---------------------------------------------------------
-- CREATION TABLE GREEN IT
-- ---------------------------------------------------------
-- ---------------------------------------------------------

START TRANSACTION;
USE `xmppmaster`;
-- ---------------------------------------------------------
-- creation table CPU machine
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`green_cpu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(90) DEFAULT NULL,
  `TDP` int(11) DEFAULT NULL,
  `freqmax` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;


CREATE TABLE `green_conso` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(36) NOT NULL,
  `date_start` datetime DEFAULT NULL,
  `date_end` datetime DEFAULT NULL,
  `puissance_total` double DEFAULT NULL,
  `charge` double DEFAULT NULL,
  `cpu_freq` double DEFAULT NULL,
  `temperature` double DEFAULT NULL,
  `puissance_cpu_gpu` double DEFAULT NULL,
  `coef_charge` double DEFAULT NULL,
  `nb_mesure` varchar(45) DEFAULT NULL,
  `energie` float DEFAULT 0,
  `charge_reelle` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `date_start_UNIQUE` (`date_start`),
  KEY `fk_green_conso_uuid_idx` (`uuid`),
  CONSTRAINT `fk_green_conso_uuid` FOREIGN KEY (`uuid`) REFERENCES `green_machine` (`uuid_machine`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

CREATE TABLE `green_machine` (
  `uuid_machine` varchar(36) NOT NULL COMMENT 'uuid number serial smbios\n',
  `hostname` varchar(45) DEFAULT NULL,
  `cpu` varchar(100) DEFAULT NULL COMMENT 'modele cpu ',
  `nbr_cpu` int(11) DEFAULT 1,
  `cpu_hertz_max` int(11) DEFAULT NULL COMMENT 'frequence maximun\\n',
  `cpu_herz` int(11) DEFAULT NULL COMMENT 'frequence courante\\n',
  `gpu` varchar(100) DEFAULT NULL,
  `nbr_gpu` int(11) DEFAULT NULL,
  `memorytype` varchar(10) DEFAULT 'DDR4' COMMENT 'type de memoire',
  `memorysize` int(11) DEFAULT 4 COMMENT 'taille memoire',
  `formfactor` varchar(10) DEFAULT 'desktop' COMMENT 'type d''ordinateur :desktop ordinateur bureau__laptop ordinateur portable \n',
  `nbr_HDD` int(11) DEFAULT 1 COMMENT 'nombre de disks HDD',
  `nbr_SSD` int(11) DEFAULT 0 COMMENT 'nombre de disks SSD',
  `monitor` varchar(100) DEFAULT NULL,
  `nbr_monitor` int(11) DEFAULT 1,
  `timeac` int(11) DEFAULT 300,
  `timedc` int(11) DEFAULT 180,
  `freq_acpi_ac_min` int(11) DEFAULT NULL,
  `biosdate` datetime DEFAULT NULL,
  `core` int(11) DEFAULT 0,
  `thread` int(11) DEFAULT NULL,
  `TDP` int(11) DEFAULT NULL,
  `osmax` varchar(20) DEFAULT NULL,
  `freq_doccpu` int(11) DEFAULT NULL,
  `freq_acpi_dc_min` int(11) DEFAULT NULL,
  `freq_acpi_ac_max` int(11) DEFAULT NULL,
  `freq_acpi_dc_max` int(11) DEFAULT NULL,
  PRIMARY KEY (`uuid_machine`),
  KEY `index2` (`TDP`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;

CREATE TABLE `greenit_global_parameter` (
  `annee` int(11) NOT NULL,
  `prix_kwh` double NOT NULL DEFAULT 0.22,
  `heures_travaillee_semaine` double NOT NULL COMMENT 'heure travailler par semaine',
  `heures_travaille_mois` double NOT NULL COMMENT '151,67 heures par mois. \\\\n',
  `heure_travaille_an` double NOT NULL COMMENT '1 607 heures par an.',
  `heure_max` double DEFAULT NULL,
  `j_ouvree` int(11) DEFAULT NULL,
  `j_ouvrable` int(11) DEFAULT NULL,
  `j_ferier` int(11) DEFAULT NULL,
  `j_max` int(11) DEFAULT NULL,
  `h_annee` int(11) DEFAULT NULL,
  `h_jour_ouvres` int(11) DEFAULT NULL,
  `h_jour_ouvrables` int(11) DEFAULT NULL,
  `f_jour_feries` int(11) DEFAULT NULL,
  PRIMARY KEY (`annee`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ;

USE `xmppmaster`;
DROP procedure IF EXISTS `_private_split_name_computer`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`_private_split_name_computer`;
;

DELIMITER $$
USE `xmppmaster`$$
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

USE `xmppmaster`;
DROP procedure IF EXISTS `search_computer`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`search_computer`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `search_computer`(in computer VARCHAR(255))
BEGIN
   DECLARE done INT DEFAULT 0;
   DECLARE element VARCHAR(255);
   DECLARE curId INT DEFAULT 0;
   DECLARE likestr VARCHAR(255);
   DECLARE countline INT DEFAULT 0;
   DECLARE cur CURSOR FOR SELECT id, value FROM `table_temp_sdsde`;
   DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    call _private_split_name_computer(computer, "table_temp_sdsde");
    OPEN cur;
    -- Boucle pour parcourir la table temporaire
    read_loop: LOOP
        FETCH cur INTO curId, element;
			IF done THEN
				LEAVE read_loop;
			END IF;
        -- Sélectionner des données de la table principale en utilisant chaque élément récupéré
		set likestr = concat("%",element ,"%");
		SELECT count(*) into countline FROM greenit.cpu_complete_base WHERE modele like likestr limit 2;
		-- select countline;
		IF countline = 1 THEN
			select *  FROM greenit.cpu_complete_base WHERE modele like likestr;
		END IF;
    END LOOP;
    CLOSE cur;
    -- Supprimer la table temporaire
    DROP TEMPORARY TABLE IF EXISTS `table_temp_sdsde`;

END$$

DELIMITER ;
;




UPDATE version SET Number = 86;

COMMIT;
