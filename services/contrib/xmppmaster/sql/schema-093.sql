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

-- ----------------------------------------------------------------------
-- CREATE TABLE up_machine_major_windows
-- a la suppression d'une machine dans la table machine, la mise a jour est aussi supprimer de cette table.
-- cette table est mis a jour depuis 1 procedure stockee
-- ----------------------------------------------------------------------

 CREATE TABLE `up_machine_major_windows` (
  `id_machine` int(11) NOT NULL,
  `update_id` varchar(38) NOT NULL,
  `kb` varchar(45) NOT NULL,
  `curent_deploy` tinyint(1) DEFAULT 0,
  `required_deploy` tinyint(1) DEFAULT 0,
  `start_date` timestamp NULL DEFAULT NULL,
  `end_date` timestamp NULL DEFAULT NULL,
  `intervals` varchar(256) DEFAULT NULL,
  `msrcseverity` varchar(16) DEFAULT NULL,
  `glpi_id` int(10) unsigned NOT NULL,
  `ent_id` int(10) unsigned NOT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT 0,
  `jid` varchar(255) DEFAULT NULL,
  `serial` varchar(255) DEFAULT NULL,
  `platform` varchar(100) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `comment` text DEFAULT NULL,
  `entity` varchar(255) DEFAULT NULL,
  `lang_code` varchar(10) DEFAULT NULL,
  `old_version` varchar(50) DEFAULT NULL,
  `new_version` varchar(50) DEFAULT NULL,
  `oldcode` varchar(50) DEFAULT NULL,
  `newcode` varchar(50) DEFAULT NULL,
  `isolang` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id_machine`,`update_id`),
  UNIQUE KEY `index_uniq_update` (`id_machine`,`update_id`),
  UNIQUE KEY `index_uniq_kb` (`id_machine`,`kb`),
  KEY `up_machine_windows_id_machine1_idx` (`id_machine`),
  CONSTRAINT `fk_up_machine_windows_2` FOREIGN KEY (`id_machine`) REFERENCES `machines` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;


-- if enabled change sur machine le mettre a jour dans up_machine_major_windows

DROP TRIGGER IF EXISTS `xmppmaster`.`machines_BEFORE_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER = CURRENT_USER TRIGGER `xmppmaster`.`machines_BEFORE_UPDATE` BEFORE UPDATE ON `machines` FOR EACH ROW
BEGIN
IF NEW.enabled <> OLD.enabled THEN
        UPDATE xmppmaster.up_machine_major_windows
        SET enabled = NEW.enabled
        WHERE up_machine_major_windows.id_machine = NEW.id;
    END IF;
END$$
DELIMITER ;

--
-- Table structure for table `up_packages_major_Lang_code`
--

DROP TABLE IF EXISTS `up_packages_major_Lang_code`;
CREATE TABLE IF EXISTS  `up_packages_major_Lang_code` (
  `major` int(11) NOT NULL DEFAULT 11,
  `lang_code` varchar(10) NOT NULL,
  `num_code` varchar(6) NOT NULL,
  `country` varchar(45) NOT NULL,
  `enabled` tinyint(4) NOT NULL DEFAULT 0,
  `iso_filename` varchar(250) NOT NULL,
  `package_uuid` varchar(64) NOT NULL,
  PRIMARY KEY (`lang_code`,`major`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Dumping data for table `up_packages_major_Lang_code`
--

INSERT INTO `up_packages_major_Lang_code` VALUES
(11,'ar-SA','0401','Arabic',0,'Win11_24H2_Arabic_x64.iso','Win11upd_24H2_Arabicx64_pbqbowfj6h9l'),
(11,'bg-BG','0402','Bulgarian',0,'Win11_24H2_Bulgarian_x64.iso','Win11upd_24H2_Bulgarianx64_pbqbowfj6'),
(11,'cs-CZ','0405','Czech',0,'Win11_24H2_Czech_x64.iso','Win11upd_24H2_Czechx64_pbqbowfj6h9lo'),
(11,'da-DK','0406','Danish',0,'Win11_24H2_Danish_x64.iso','Win11upd_24H2_Danishx64_pbqbowfj6h9l'),
(11,'de-DE','0407','German',0,'Win11_24H2_German_x64.iso','Win11upd_24H2_Germanx64_pbqbowfj6h9l'),
(11,'el-GR','0408','Greek',0,'Win11_24H2_Greek_x64.iso','Win11upd_24H2_Greekx64_pbqbowfj6h9lo'),
(11,'en-GB','0809','English - United Kingdom',1,'Win11_24H2_English_x64.iso','Win11upd_24H2_Englishx64_pbqbowfj6h9'),
(11,'en-US','0409','English',1,'Win11_24H2_EnglishInternational_x64.iso','Win11upd_24H2_EnglishInternationalx6'),
(11,'es-ES','040A','Spanish',0,'Win11_24H2_Spanish_x64.iso','Win11upd_24H2_Spanishx64_pbqbowfj6h9'),
(11,'es-MX','080A','Spanish - Mexico',0,'Win11_24H2_Spanish_Mexico_x64.iso','Win11upd_24H2_Spanish_Mexicox64_pbqb'),
(11,'et-EE','0425','Estonian - Estonia',0,'Win11_24H2_Estonian_x64.iso','Win11upd_24H2_Estonianx64_pbqbowfj6h'),
(11,'fi-FI','040E','Finnish',0,'Win11_24H2_Finnish_x64.iso','Win11upd_24H2_Finnishx64_pbqbowfj6h9'),
(11,'fr-CA','0C0C','French - Canada',0,'Win11_24H2_FrenchCanadian_x64.iso','Win11upd_24H2_FrenchCanadianx64_pbqb'),
(11,'fr-FR','040C','French',1,'Win11_24H2_French_x64.iso','Win11upd_24H2_Frenchx64_pbqbowfj6h9l'),
(11,'he-IL','040D','Hebrew',0,'Win11_24H2_Hebrew_x64.iso','Win11upd_24H2_Hebrewx64_pbqbowfj6h9l'),
(11,'hi-IN','0439','Hindi',0,'Win11_24H2_Hindi_x64.iso','Win11upd_24H2_Hindix64_pbqbowfj6h9lo'),
(11,'hr-HR','041A','Croatian',0,'Win11_24H2_Croatian_x64.iso','Win11upd_24H2_Croatianx64_pbqbowfj6h'),
(11,'hu-HU','040E','Hungarian',0,'Win11_24H2_Hungarian_x64.iso','Win11upd_24H2_Hungarianx64_pbqbowfj6'),
(11,'it-IT','0410','Italian',0,'Win11_24H2_Italian_x64.iso','Win11upd_24H2_Italianx64_pbqbowfj6h9'),
(11,'ja-JP','0411','Japanese',0,'Win11_24H2_Japanese_x64.iso','Win11upd_24H2_Japanesex64_pbqbowfj6h'),
(11,'ko-KR','0412','Korean',0,'Win11_24H2_Korean_x64.iso','Win11upd_24H2_Koreanx64_pbqbowfj6h9l'),
(11,'lt-LT','0427','Lithuanian',0,'Win11_24H2_Lithuanian_x64.iso','Win11upd_24H2_Lithuanianx64_pbqbowfj'),
(11,'lv-LV','0426','Latvian',0,'Win11_24H2_Latvian_x64.iso','Win11upd_24H2_Latvianx64_pbqbowfj6h9'),
(11,'nb-NO','0414','Norwegian',0,'Win11_24H2_Norwegian_x64.iso','Win11upd_24H2_Norwegianx64_pbqbowfj6'),
(11,'nl-NL','0413','Dutch',0,'Win11_24H2_Dutch_x64.iso','Win11upd_24H2_Dutchx64_pbqbowfj6h9lo'),
(11,'pl-PL','0415','Polish',0,'Win11_24H2_Polish_x64.iso','Win11upd_24H2_Polishx64_pbqbowfj6h9l'),
(11,'pt-PT','0416','Portuguese - Portugal',0,'Win11_24H2_Portuguese_x64.iso','Win11upd_24H2_Portuguesex64_pbqbowfj'),
(11,'ru-RU','0419','Russian',0,'Win11_24H2_Russian_x64.iso','Win11upd_24H2_Russianx64_pbqbowfj6h9'),
(11,'sv-SE','041D','Swedish',0,'Win11_24H2_Swedish_x64.iso','Win11upd_24H2_Swedishx64_pbqbowfj6h9'),
(11,'th-TH','041E','Thai',0,'Win11_24H2_Thai_x64.iso','Win11upd_24H2_Thaix64_pbqbowfj6h9lom'),
(11,'tr-TR','041F','Turkish',0,'Win11_24H2_Turkish_x64.iso','Win11upd_24H2_Turkishx64_pbqbowfj6h9'),
(11,'uk-UA','0422','Ukrainian',0,'Win11_24H2_Ukrainian_x64.iso','Win11upd_24H2_Ukrainian_x64_pbqbowfj'),
(11,'zh-CHT','7C04','Chinese - Traditional',0,'Win11_24H2_Chinese_Traditional_x64.iso','Win11upd_24H2_Chinese_Traditionalx64'),
(11,'zh-CN','0804','Chinese (Simplified) - China',0,'Win11_24H2_Chinese_Simplified_x64.iso','Win11upd_24H2_Chinese_Simplifiedx64_');


-- -----------------------------------------------------
--
-- Procédure stockée pour initialiser et synchroniser la table `up_machine_major_windows`
-- à partir des données de la table `up_major_win`.
--
-- Cette procédure effectue les opérations suivantes :
-- 1. Supprime et recrée la table `up_major_win`.
-- 2. Insère des données dans `up_major_win` à partir de plusieurs jointures.
-- 3. Lit les données de `up_major_win` et insère les enregistrements dans `up_machine_major_windows`
--    uniquement si les enregistrements n'existent pas déjà.
--
-- -----------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_init_table_major_win_complet`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `up_init_table_major_win_complet`()
BEGIN
    -- Variable pour indiquer la fin de la boucle de lecture du curseur
    DECLARE done INT DEFAULT FALSE;
    -- Variables pour stocker les valeurs lues depuis le curseur
    DECLARE id_machine INT; -- Identifiant de la machine
    DECLARE update_id VARCHAR(38); -- Identifiant de la mise à jour
    DECLARE kb VARCHAR(45); -- Identifiant du bulletin de sécurité
    DECLARE msrcseverity VARCHAR(16); -- Niveau de sévérité de la mise à jour
    DECLARE vglpi_id INT UNSIGNED; -- Identifiant GLPI
    DECLARE vent_id INT UNSIGNED; -- Identifiant de l'entité
    DECLARE vhostname VARCHAR(255); -- Nom d'hôte
    DECLARE vjid VARCHAR(255); -- Identifiant JID
    DECLARE vserial VARCHAR(255); -- Numéro de série
    DECLARE vplatform VARCHAR(100); -- os machine
    DECLARE vname VARCHAR(255); -- Nom
    DECLARE vcomment TEXT; -- Commentaire
    DECLARE ventity VARCHAR(255); -- Entité
    DECLARE vlang_code VARCHAR(10); -- Code de langue
    DECLARE vold_version VARCHAR(50); -- Ancienne version
    DECLARE vnew_version VARCHAR(50); -- Nouvelle version
    DECLARE voldcode VARCHAR(50); -- Ancien code
    DECLARE vnewcode VARCHAR(50); -- Nouveau code
    DECLARE visolang VARCHAR(10); -- Langue ISO
    DECLARE venabled INT(1); -- Presence machine

    -- Curseur pour parcourir les enregistrements de la table `up_major_win`
    DECLARE cur CURSOR FOR
        SELECT xmpp_id, package_uuid, iso_filename, 'major', glpi_id, ent_id, hostname,enabled, jid, serial, platform, name, comment, entity, lang_code, old_version, new_version, oldcode, newcode, isolang
        FROM up_major_win;

    -- Gestionnaire pour détecter la fin des enregistrements du curseur
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Démarrer une transaction
    START TRANSACTION;

    -- Supprimer la table `up_major_win` si elle existe déjà
    DROP TABLE IF EXISTS up_major_win;

    -- Création de la table `up_major_win` avec des index pour optimiser les requêtes
    CREATE TABLE up_major_win (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,  -- Clé primaire avec auto-incrémentation
        xmpp_id INT UNSIGNED NOT NULL,  -- Identifiant XMPP
        glpi_id INT UNSIGNED NOT NULL,  -- Identifiant GLPI
        ent_id INT UNSIGNED NOT NULL,  -- Identifiant de l'entité
        hostname VARCHAR(255),  -- Nom d'hôte
        enabled INT UNSIGNED,  -- on or off (0 ou 1)
        jid VARCHAR(255),  -- Identifiant JID
        serial VARCHAR(255),  -- Numéro de série
        platform VARCHAR(100),  -- os machine
        name VARCHAR(255),  -- Nom
        comment TEXT,  -- Commentaire
        entity VARCHAR(255),  -- Entité
        lang_code VARCHAR(10),  -- Code de langue
        iso_filename VARCHAR(255),  -- Nom du fichier ISO
        package_uuid VARCHAR(255) NOT NULL,  -- UUID du package
        old_version VARCHAR(50),  -- Ancienne version
        new_version VARCHAR(50),  -- Nouvelle version
        oldcode VARCHAR(50),  -- Ancien code
        newcode VARCHAR(50),  -- Nouveau code
        isolang VARCHAR(10),  -- Langue ISO
        PRIMARY KEY (id),  -- Définition de la clé primaire
        INDEX idx_glpi_id (glpi_id),  -- Index pour accélérer les requêtes sur glpi_id
        INDEX idx_xmpp_id (xmpp_id),  -- Index pour xmpp_id
        INDEX idx_ent_id (ent_id),    -- Index pour ent_id
        INDEX idx_package_uuid (package_uuid)  -- Index sur package_uuid pour les recherches rapides
    );

    -- Insertion des données dans `up_major_win` en s'assurant que NULL est bien géré
    INSERT INTO up_major_win (
        xmpp_id, glpi_id, ent_id,
        hostname,enabled, jid, serial,platform,
        name, comment, entity,
        lang_code, iso_filename,
        package_uuid, old_version,
        new_version, oldcode,
        newcode, isolang
    )
    SELECT
        mx.id AS xmpp_id,
        m.id AS glpi_id,
        e.id AS ent_id,
        mx.hostname,
        mx.enabled,
        mx.jid,
        mx.uuid_serial_machine AS serial,
        mx.platform as platform,
        s.name,
        s.comment,
        e.completename AS entity,
        lc.lang_code,
        lc.iso_filename,
        lc.package_uuid,
        -- Extraction des versions et codes depuis le nom du logiciel
        SUBSTRING(s.name, LOCATE('_', s.name) + 1, LOCATE('@', s.name) - LOCATE('_', s.name) - 1) AS old_version,
        SUBSTRING_INDEX(s.name, '-', -1) AS new_version,
        SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1) AS oldcode,
        SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1), '_', 2), '_', -1) AS newcode,
        SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1) AS isolang
    FROM xmppmaster.local_glpi_items_softwareversions si
    JOIN xmppmaster.local_glpi_softwareversions sv ON si.softwareversions_id = sv.id
    JOIN xmppmaster.local_glpi_machines m ON si.items_id = m.id
    JOIN xmppmaster.local_glpi_softwares s ON sv.softwares_id = s.id
    JOIN xmppmaster.local_glpi_entities e ON e.id = m.entities_id
    JOIN xmppmaster.machines mx ON NULLIF(REPLACE(mx.uuid_inventorymachine, 'UUID', ''),'') = si.items_id
    JOIN xmppmaster.up_packages_major_Lang_code lc ON lc.lang_code = SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1)
    WHERE s.name LIKE 'Medulla\_%'
    AND (
        SUBSTRING(s.name, LOCATE('_', s.name) + 1, LOCATE('@', s.name) - LOCATE('_', s.name) - 1)
            != SUBSTRING_INDEX(s.name, '@', -1)
        OR
        SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1)
            != SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1), '_', 2), '_', -1)
    );

    -- Valider la transaction pour enregistrer les modifications
    COMMIT;

    -- Ouvrir le curseur pour lire les données de `up_major_win`
 OPEN cur;

    read_loop: LOOP
        FETCH cur INTO id_machine, update_id, kb,
						msrcseverity, vglpi_id, vent_id, vhostname,venabled,
                        vjid, vserial,vplatform, vname, vcomment, ventity,
                        vlang_code, vold_version, vnew_version,
                        voldcode, vnewcode, visolang;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Vérifier si l'enregistrement existe déjà dans `up_machine_major_windows`
        IF NOT EXISTS (
            SELECT 1
            FROM up_machine_major_windows
            WHERE id_machine = id_machine AND update_id = update_id
        ) THEN
            -- Insérer le nouvel enregistrement dans `up_machine_major_windows`
            INSERT INTO up_machine_major_windows (
                id_machine, update_id, kb, msrcseverity, glpi_id, ent_id, hostname,enabled, jid, serial, platform, name, comment, entity, lang_code, old_version, new_version, oldcode, newcode, isolang
            )
            VALUES (
                id_machine, update_id, kb, msrcseverity, vglpi_id,
                vent_id, vhostname,venabled, vjid,
                vserial, vplatform,vname, vcomment, ventity, vlang_code, vold_version,
                vnew_version, voldcode, vnewcode, visolang
            );
        END IF;
    END LOOP;
    -- Fermer le curseur
    CLOSE cur;
END$$

DELIMITER ;
;

-- -----------------------------------------------------
--
-- additionne colonne dans table machine
-- on ajoute 1 colonne pour facilite les jointures.
-- cette colonne aura la meme valeur que uuid_inventory sans le prefixe UUID
-- -----------------------------------------------------
ALTER TABLE `xmppmaster`.`machines`
ADD COLUMN `id_glpi` INT(11) NULL AFTER `uuid_inventorymachine`,
CHANGE COLUMN `manufacturer` `manufacturer` VARCHAR(45) NULL DEFAULT '' COMMENT 'id de la machine dans glpi.\n' ,
ADD INDEX `inx_id_glpi` (`id_glpi` ASC) ;
-- -----------------------------------------------------
-- initialisation de la colonne
-- -----------------------------------------------------
UPDATE xmppmaster.machines
SET id_glpi = SUBSTRING(uuid_inventorymachine, 5);

DROP TRIGGER IF EXISTS `xmppmaster`.`machines_BEFORE_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `xmppmaster`.`machines_BEFORE_UPDATE` BEFORE UPDATE ON `machines` FOR EACH ROW
BEGIN
IF NEW.enabled <> OLD.enabled THEN
        UPDATE xmppmaster.up_machine_major_windows
        SET enabled = NEW.enabled
        WHERE up_machine_major_windows.id_machine = NEW.id;
    END IF;
IF NEW.uuid_inventorymachine <> OLD.uuid_inventorymachine THEN
	SET NEW.id_glpi = SUBSTRING(NEW.uuid_inventorymachine, 5);
    END IF;
END$$
DELIMITER ;


-- -----------------------------------------------------
-- INSTALL PLANIFICATION DE L'APPEL AUTOMATIQUE DE PROCEDURE STOCKEE up_init_table_major_win_complet
--
-- Planifie l'événement pour qu'il se répète tous les jours
-- L'événement commencera à partir du 1er mars 2025 à 20h00
-- -----------------------------------------------------
-- Supprime l'événement s'il existe déjà
DROP EVENT IF EXISTS appel_procedure_soir_init_major_table;
-- Crée un nouvel événement nommé 'appel_procedure_soir_init_major_table'
CREATE EVENT appel_procedure_soir_init_major_table
ON SCHEDULE EVERY 1 DAY
STARTS '2025-03-01 20:00:00'
DO CALL up_init_table_major_win_complet();

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 93;

COMMIT;
