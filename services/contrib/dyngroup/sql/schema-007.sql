--
-- (c) 2008 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Pulse 2, http://pulse2.mandriva.org
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
-- les table dyngroup sont InnoDB
--

-- Structure de la table `logs`
-- ATTENTION : IMPORTANT !!!
-- Ne pas convertir cette table en InnoDB,
-- car nous insérons des messages depuis des déclencheurs pour notifier une opération annulée.
-- Si la table était en InnoDB, les messages seraient supprimés par le mécanisme de rollback.
CREATE TABLE IF NOT EXISTS `logs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  `type` varchar(25) DEFAULT '',
  `module` varchar(255) DEFAULT '',
  `text` varchar(4096) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `Lang_code_windows`
--

DROP TABLE IF EXISTS `Lang_code_windows`;
CREATE TABLE `Lang_code_windows` (
  `lang_codes` varchar(10) NOT NULL,
  `num_code` varchar(6) NOT NULL,
  `country_name` varchar(45) NOT NULL,
  `enabled` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`lang_codes`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
--  data for table `Lang_code_windows`
--
INSERT INTO `Lang_code_windows` VALUES
('ar-SA','0401','Arabic',0),
('cs-CZ','0405','Czech',0),
('da-DK','0406','Danish',0),
('de-DE','0407','German',0),
('el-GR','0408','Greek',0),
('en-US','0409','English',1),
('es-ES','040A','Spanish',0),
('fi-FI','040E','Finnish',0),
('fr-FR','040C','French',1),
('he-IL','040D','Hebrew',0),
('hi-IN','0439','Hindi',0),
('hu-HU','040E','Hungarian',0),
('it-IT','0410','Italian',0),
('ja-JP','0411','Japanese',0),
('ko-KR','0412','Korean',0),
('nb-NO','0414','Norwegian',0),
('nl-NL','0413','Dutch',0),
('pl-PL','0415','Polish',0),
('pt-PT','0416','Portuguese',0),
('ru-RU','0419','Russian',0),
('sv-SE','041D','Swedish',0),
('th-TH','041E','Thai',0),
('tr-TR','041F','Turkish',0),
('zh-CN','0804','Chinese_Simplified',0),
('zh-TW','0404','Chinese_Traditional',0);



-- ----------------------------------------------------------------------------------------------------------
--  CONTRAINTES
-- ----------------------------------------------------------------------------------------------------------
--
-- 5 commandes suivantes avant la suite.
--
ALTER TABLE `dyngroup`.`Results` DROP FOREIGN KEY `Results_ibfk_1`;
ALTER TABLE `dyngroup`.`ShareGroup` DROP FOREIGN KEY `ShareGroup_ibfk_2`;
ALTER TABLE `dyngroup`.`ProfilesResults` DROP FOREIGN KEY `ProfilesResults_ibfk_1`;
ALTER TABLE `dyngroup`.`ProfilesPackages` DROP FOREIGN KEY `ProfilesPackages_ibfk_1`;
ALTER TABLE `dyngroup`.`ProfilesData` DROP FOREIGN KEY `ProfilesData_ibfk_1`;

-- reconstructions des contraintes.
ALTER TABLE `dyngroup`.`Results`
ADD CONSTRAINT `Results_ibfk_1`
FOREIGN KEY (`FK_groups`) REFERENCES `dyngroup`.`Groups` (`id`) ON DELETE CASCADE;

ALTER TABLE `dyngroup`.`ShareGroup`
ADD CONSTRAINT `ShareGroup_ibfk_2`
FOREIGN KEY (`FK_groups`) REFERENCES `dyngroup`.`Groups` (`id`) ON DELETE CASCADE;

ALTER TABLE `dyngroup`.`ProfilesResults`
ADD CONSTRAINT `ProfilesResults_ibfk_1`
FOREIGN KEY (`FK_groups`) REFERENCES `dyngroup`.`Groups` (`id`) ON DELETE CASCADE;

ALTER TABLE `dyngroup`.`ProfilesPackages`
ADD CONSTRAINT `ProfilesPackages_ibfk_1`
FOREIGN KEY (`FK_groups`) REFERENCES `dyngroup`.`Groups` (`id`) ON DELETE CASCADE;

ALTER TABLE `dyngroup`.`ProfilesData`
ADD CONSTRAINT `ProfilesData_ibfk_1`
FOREIGN KEY (`FK_groups`) REFERENCES `dyngroup`.`Groups` (`id`) ON DELETE CASCADE;

-- ----------------------------------------------------------------------------------------------------------
--  TRIGGER
-- ----------------------------------------------------------------------------------------------------------

--
--  Trigger `Groups_BEFORE_DELETE`
--  Ce trigger est déclenché avant la suppression d'une ligne dans la table `Groups`.
--  Il vérifie si le group que l'on supprime n'est pas 1 composant d'un autre group.
--  Si c'est le cas, il insère un message de log pour chaque occurrence trouvée et empêche la suppression.
--  le message delivre par l'exception mysql precice la liste des group utilisant ce group
--

DROP TRIGGER IF EXISTS `dyngroup`.`Groups_BEFORE_DELETE`;

DELIMITER $$
USE `dyngroup`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `dyngroup`.`Groups_BEFORE_DELETE` BEFORE DELETE ON `Groups` FOR EACH ROW
BEGIN
    -- Déclaration des variables
    DECLARE done INT DEFAULT 0; -- Indicateur pour la fin du curseur
    DECLARE group_id INT; -- Variable pour stocker l'ID de la ligne trouvée
    DECLARE group_query VARCHAR(255); -- Variable pour stocker la valeur de la colonne `query` de la ligne trouvée
    DECLARE group_name VARCHAR(255); -- Variable pour stocker la valeur de la colonne `name` de la ligne trouvée
    DECLARE row_count INT DEFAULT 0; -- Compteur pour vérifier si des lignes ont été trouvées
    DECLARE concat_group_query VARCHAR(4096) DEFAULT ''; -- Variable pour accumuler les valeurs de `query`
    DECLARE Message_exception TEXT; -- Variable pour stocker le message d'exception
    -- Curseur pour parcourir les lignes où le nom existe dans la colonne `query`
    DECLARE cur CURSOR FOR
    SELECT id, name, query
    FROM dyngroup.Groups
    WHERE query LIKE CONCAT('%', OLD.name, '%');

    -- Déclarer un handler pour la fin du curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    -- Ouvrir le curseur
    OPEN cur;

    -- Parcourir les lignes trouvées
    read_loop: LOOP
        FETCH cur INTO group_id, group_name, group_query;
        IF done THEN
            LEAVE read_loop; -- Sortir de la boucle si la fin du curseur est atteinte
        END IF;

        -- Ajouter la chaîne group_query à concat_group_query
        SET concat_group_query = CONCAT(concat_group_query, group_name, ', ');

        -- Insérer un avertissement dans la table `logs`
        INSERT INTO logs (type, module, text)
        VALUES ('warning', 'dyngroup', CONCAT('Deletion forbidden for Group: ', OLD.name, ' as it already used in the group number ', group_id, ' and named "', group_name, '".'));

        -- Incrémenter le compteur de lignes trouvées
        SET row_count = row_count + 1;
    END LOOP;

    -- Fermer le curseur
    CLOSE cur;

    -- Si des lignes ont été trouvées, lever une exception pour empêcher la suppression
    IF row_count > 0 THEN
        -- Supprimer la virgule et l'espace finaux de concat_group_query
        SET concat_group_query = TRIM(TRAILING ', ' FROM concat_group_query);

        -- Construire le message d'exception
        SET Message_exception = CONCAT('Deletion forbidden for Group: ', OLD.name, '. Delete before the groups: ', concat_group_query);

        -- Lever une exception pour empêcher la suppression
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = Message_exception;
    END IF;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------------------------------------------
--  PROCEDURE STOCKEE
-- ----------------------------------------------------------------------------------------------------------

--
--  Procédure `create_groups_major_update_win`
--  Cette procédure crée des groupes dynamiques pour les mises à jour majeures de Windows
--  en fonction des versions de Windows et des codes de langue. Elle insère les groupes
--  dans la table `Groups` et met à jour les relations de groupe dans la table `ShareGroup`.
--

USE `dyngroup`;
DROP procedure IF EXISTS `create_groups_major_update_win`;

USE `dyngroup`;
DROP procedure IF EXISTS `dyngroup`.`create_groups_major_update_win`;
;

DELIMITER $$
USE `dyngroup`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `create_groups_major_update_win`()
BEGIN
    -- Déclaration des variables
    DECLARE done INT DEFAULT 0; -- Indicateur de fin de boucle
    DECLARE version_windows VARCHAR(2048); -- Version de Windows
    DECLARE version_windows_code VARCHAR(2048); -- Code de la version de Windows
    DECLARE code_lang VARCHAR(2048); -- Code de la langue
    DECLARE vnum_code VARCHAR(2048); -- Numéro de code de la langue
    DECLARE vcountry_name VARCHAR(2048); -- Nom du pays
    DECLARE name_group TEXT DEFAULT NULL; -- Nom du groupe
    DECLARE name_group_dynamic TEXT DEFAULT NULL; -- Nom du groupe dynamique
    DECLARE concaneme_group TEXT; -- Groupe concaténé
    DECLARE relation_group TEXT; -- Relation de groupe
    DECLARE nbligne INT; -- Nombre de lignes
	DECLARE last_id INT;
    -- Déclaration des curseurs pour les versions de Windows et les codes de langue
    DECLARE windows_cursor CURSOR FOR SELECT version, version_name_code FROM windows_versions;
    DECLARE lang_cursor CURSOR FOR SELECT lang_codes, num_code, country_name FROM Lang_code_windows WHERE enabled = 1;

    -- Déclaration des gestionnaires de continuation pour les curseurs
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
    -- Suppression de la table temporaire si elle existe
    DROP TEMPORARY TABLE IF EXISTS mes_groups;

    -- Création de la table temporaire mes_groups avec les colonnes id et name
    CREATE TEMPORARY TABLE mes_groups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255)
    );

    -- Création de la table temporaire pour stocker les versions de Windows
    CREATE TEMPORARY TABLE IF NOT EXISTS windows_versions (
        version VARCHAR(2048),
        version_name_code VARCHAR(2048)
    );

    -- Insertion des versions de Windows dans la table temporaire
    INSERT INTO windows_versions (version, version_name_code) VALUES ('10', '22H2'), ('11', '24H2');

    -- Ouverture du curseur pour les versions de Windows
    OPEN windows_cursor;

    -- Boucle sur les versions de Windows
    windows_loop: LOOP
        FETCH windows_cursor INTO version_windows, version_windows_code;
        IF done THEN
            LEAVE windows_loop;
        END IF;

        -- Ouverture du curseur pour les codes de langue
        OPEN lang_cursor;

        -- Boucle sur les codes de langue
        lang_loop: LOOP
            FETCH lang_cursor INTO code_lang, vnum_code, vcountry_name;
            IF done THEN
                LEAVE lang_loop;
            END IF;

            -- Génération du nom du groupe
            SET name_group = CONCAT('_@med_Grp_Major_update_win_', version_windows, '_', code_lang, '_', vcountry_name);
			SET name_group_dynamic = CONCAT('1==glpi::Installed software==Medulla_%@',
                                             code_lang, '-', version_windows);
            -- Insertion dans la table `Groups` uniquement si le nom n'existe pas déjà
            INSERT INTO `dyngroup`.`Groups` (`name`, `query`, `bool`, `FK_users`, `type`, `parent_id`)
            SELECT name_group, name_group_dynamic, '', '1', '0', '0'
            FROM dual
            WHERE NOT EXISTS (
                SELECT 1
                FROM `dyngroup`.`Groups`
                WHERE `name` = name_group
            );
        END LOOP lang_loop;

        -- Fermeture du curseur pour les codes de langue
        CLOSE lang_cursor;

        -- Réinitialisation du gestionnaire de continuation pour les codes de langue
        SET done = 0;

        -- Insertion des lignes correspondantes de dyngroup.Groups dans mes_groups
        INSERT INTO mes_groups (name)
			SELECT name
			FROM dyngroup.Groups
			WHERE name LIKE CONCAT('_@med_Grp_Major_update_win_', version_windows, '_%');

        -- Concaténation des groupes et des relations
        SELECT GROUP_CONCAT(CONCAT(id, '==dyngroup::groupname==', name) SEPARATOR '||') INTO concaneme_group FROM mes_groups;
        SELECT CONCAT('OR(', GROUP_CONCAT(id SEPARATOR ','), ')') INTO relation_group FROM mes_groups;

        -- Stocker le nombre de lignes de la table mes_groups dans la variable nbligne
        SELECT COUNT(*) INTO nbligne
        FROM mes_groups WHERE name LIKE CONCAT('_@med_Grp_Major_update_win_', version_windows, '_%');

        -- Vider la table temporaire mes_groups
        TRUNCATE mes_groups;

        -- Génération du nom du groupe pour toutes les langues
        SET name_group = CONCAT('_@med_Grp_Major_update_win_', version_windows, '_ALL_LANG');

        -- Insérer ou mettre à jour la ligne dans la table Groups
        IF EXISTS (SELECT 1 FROM `dyngroup`.`Groups` WHERE `name` = name_group) THEN
			UPDATE `dyngroup`.`Groups`
			SET `query` = concaneme_group,
				`bool` = relation_group,
				`FK_users` = '1',
				`type` = '0',
				`parent_id` = '0'
			WHERE `name` = name_group;
		ELSE
			INSERT INTO `dyngroup`.`Groups` (`name`, `query`, `bool`, `FK_users`, `type`, `parent_id`)
			VALUES (name_group, concaneme_group, relation_group, '1', '0', '0');
			SET last_id = LAST_INSERT_ID();  -- Récupérer l'ID de la dernière insertion
			-- Utiliser cet ID dans l'insertion suivante
			INSERT INTO `dyngroup`.`ShareGroup` (`FK_groups`, `FK_users`, `type`, `display_in_menu`)
			VALUES (last_id, '1', '1', '2');
		END IF;
    END LOOP windows_loop;

    -- Fermeture du curseur pour les versions de Windows
    CLOSE windows_cursor;

    -- Suppression des tables temporaires
    DROP TEMPORARY TABLE IF EXISTS windows_versions;
    DROP TEMPORARY TABLE IF EXISTS mes_groups;
END$$

DELIMITER ;
;

-- This procedure inserts a log entry into the `logs` table. ou tout les champ sont a preciser
-- The `date` column is automatically populated with the current timestamp.

USE `dyngroup`;
DROP procedure IF EXISTS `insert_complet_log`;

DELIMITER $$
USE `dyngroup`$$
CREATE PROCEDURE `insert_complet_log` (
    IN p_date TIMESTAMP,
    IN p_type VARCHAR(25),
    IN p_module VARCHAR(255),
    IN p_text VARCHAR(4096)
)
BEGIN
    INSERT INTO logs (`date`, `type`, `module`, `text`)
    VALUES (p_date, p_type, p_module, p_text);
END$$

DELIMITER ;


-- This procedure inserts a log entry into the `logs` table.
-- The `date` column is automatically populated with the current timestamp.

USE `dyngroup`;
DROP procedure IF EXISTS `insert_log`;

DELIMITER $$
USE `dyngroup`$$
CREATE PROCEDURE `insert_log` ( IN log_type VARCHAR(25),
    IN log_module VARCHAR(255),
    IN log_text VARCHAR(4096))
BEGIN
 INSERT INTO logs (type, module, text)
    VALUES (log_type, log_module, log_text);
END$$

DELIMITER ;


UPDATE version set Number = 7;

