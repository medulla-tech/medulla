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
-- FILE contrib/xmppmaster/sql/schema-096.sql
-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;
USE `xmppmaster`;



ALTER TABLE `xmppmaster`.`up_machine_major_windows`
ADD COLUMN `is_active` VARCHAR(10) DEFAULT '1' AFTER `isolang`;

-- =======================================
-- add office 2019
-- =======================================
-- Insertion des données pour les produits Microsoft
INSERT IGNORE INTO `applicationconfig` (`id`, `key`, `value`, `comment`, `context`, `module`, `enable`) VALUES
(43,'table produits','up_packages_office_2019_64bit','Microsoft Office suite bureautique','entity','xmppmaster/update',0);



-- =======================================
-- on prend en charge visual studio et office
-- =======================================

UPDATE xmppmaster.applicationconfig
SET enable = 1
WHERE `key` = 'table produits'
  AND (comment LIKE 'Microsoft Office%'
       OR comment LIKE '%Visual Studio%')
  AND id > 0;


-- =======================================
-- up_init_packages_office_2019_64bit stored procedure
-- =======================================
USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `up_packages_office_2019_64bit`;

DELIMITER $$

CREATE PROCEDURE `up_packages_office_2019_64bit`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_office_2019_64bit;
    CREATE TABLE up_packages_office_2019_64bit AS
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
            aa.product LIKE '%Office 2019%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%32-Bit%'
            AND aa.title NOT LIKE '%Server%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END$$

DELIMITER ;



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

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`up_init_table_major_win_complet`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `up_init_table_major_win_complet`()
BEGIN
    -- ------------------------------------------------------------------
    -- Déclarations de variables
    -- ------------------------------------------------------------------
    DECLARE done INT DEFAULT FALSE;
    DECLARE id_machine INT;
    DECLARE update_id VARCHAR(255);
    DECLARE kb VARCHAR(45);
    DECLARE msrcseverity VARCHAR(16);
    DECLARE vglpi_id INT UNSIGNED;
    DECLARE vent_id INT UNSIGNED;
    DECLARE vhostname VARCHAR(255);
    DECLARE venabled TINYINT(1);
    DECLARE vjid VARCHAR(255);
    DECLARE vserial VARCHAR(255);
    DECLARE vplatform VARCHAR(100);
    DECLARE vis_active VARCHAR(10);
    DECLARE vname VARCHAR(255);
    DECLARE vcomment TEXT;
    DECLARE ventity VARCHAR(255);
    DECLARE vlang_code VARCHAR(10);
    DECLARE vold_version VARCHAR(50);
    DECLARE vnew_version VARCHAR(50);
    DECLARE voldcode VARCHAR(50);
    DECLARE vnewcode VARCHAR(50);
    DECLARE visolang VARCHAR(10);

    -- ------------------------------------------------------------------
    -- Définition du curseur sur la table temporaire up_major_win
    -- ------------------------------------------------------------------
    DECLARE cur CURSOR FOR
        SELECT xmpp_id, package_uuid, NULL AS kb, NULL AS msrcseverity,
               glpi_id, ent_id, hostname, enabled, jid, serial, platform,
               is_active, name, comment, entity, lang_code,
               old_version, new_version, oldcode, newcode, isolang
        FROM up_major_win;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- ------------------------------------------------------------------
    -- Phase 1 : (Re)création et alimentation de la table up_major_win
    -- ------------------------------------------------------------------
    START TRANSACTION;

    DROP TABLE IF EXISTS up_major_win;

    CREATE TABLE up_major_win (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        xmpp_id INT UNSIGNED NOT NULL,
        glpi_id INT UNSIGNED NOT NULL,
        ent_id INT UNSIGNED NOT NULL,
        hostname VARCHAR(255),
        enabled TINYINT(1),
        jid VARCHAR(255),
        serial VARCHAR(255),
        platform VARCHAR(100),
        name VARCHAR(255),
        comment TEXT,
        entity VARCHAR(255),
        lang_code VARCHAR(10),
        iso_filename VARCHAR(255),
        package_uuid VARCHAR(255) NOT NULL,
        prefix VARCHAR(50),
        old_version VARCHAR(50),
        oldcode VARCHAR(50),
        isolang VARCHAR(10),
        internal_code VARCHAR(50),
        target_name VARCHAR(255),
        is_active VARCHAR(10),
        lang_version VARCHAR(50),
        new_version VARCHAR(50),
        newcode VARCHAR(50),
        PRIMARY KEY (id),
        INDEX idx_glpi_id (glpi_id),
        INDEX idx_ent_id (ent_id),
        INDEX idx_package_uuid (package_uuid)
    );

    -- ------------------------------------------------------------------
    -- Insertion optimisée avec découpage en CTE
    -- ------------------------------------------------------------------
    INSERT IGNORE INTO up_major_win (
        xmpp_id, glpi_id, ent_id,
        hostname, enabled, jid, serial, platform,
        name, comment, entity,
        lang_code, iso_filename, package_uuid,
        prefix, old_version, oldcode, isolang,
        internal_code, target_name, is_active, lang_version,
        new_version, newcode
    )
    WITH parts AS (
        SELECT
            s.id AS soft_id,
            s.name AS fullname,
            SUBSTRING_INDEX(s.name, '@', 1) AS part1,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1) AS part2,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1) AS part3,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 4), '@', -1) AS part4,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1) AS part5,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 6), '@', -1) AS part6,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 7), '@', -1) AS part7
        FROM xmppmaster.local_glpi_softwares s
        WHERE s.name LIKE 'Medulla\_%'
    )
    SELECT
        mx.id AS xmpp_id,
        m.id AS glpi_id,
        e.id AS ent_id,
        mx.hostname,
        mx.enabled,
        mx.jid,
        mx.uuid_serial_machine AS serial,
        mx.platform,
        parts.fullname AS name,
        s.comment,
        e.completename AS entity,
        lc.lang_code,
        lc.iso_filename,
        lc.package_uuid,
        SUBSTRING_INDEX(parts.part1, '_', 1) AS prefix,
        SUBSTRING_INDEX(parts.part1, '_', -1) AS old_version,
        parts.part2 AS oldcode,
        parts.part3 AS isolang,
        parts.part4 AS internal_code,
        parts.part5 AS target_name,
        parts.part6 AS is_active,
        parts.part7 AS lang_version,
        SUBSTRING_INDEX(parts.part7, '-', -1) AS new_version,
        SUBSTRING_INDEX(SUBSTRING_INDEX(parts.part5, '_', 2), '_', -1) AS newcode
    FROM xmppmaster.local_glpi_items_softwareversions si
    LEFT JOIN xmppmaster.local_glpi_softwareversions sv ON si.softwareversions_id = sv.id
    LEFT JOIN xmppmaster.local_glpi_machines m ON si.items_id = m.id
    LEFT JOIN xmppmaster.local_glpi_entities e ON e.id = m.entities_id
    LEFT JOIN xmppmaster.local_glpi_softwares s ON sv.softwares_id = s.id
    LEFT JOIN parts ON parts.soft_id = s.id
    INNER JOIN xmppmaster.machines mx ON NULLIF(REPLACE(mx.uuid_inventorymachine, 'UUID', ''),'') = si.items_id
    LEFT JOIN xmppmaster.up_packages_major_Lang_code lc
        ON lc.lang_code = parts.part3
        AND lc.major = SUBSTRING_INDEX(parts.part7, '-', -1)
    WHERE s.name LIKE 'Medulla\_%';

    COMMIT;
    -- ------------------------------------------------------------------
    -- Phase 2 : Insertion conditionnelle dans up_machine_major_windows
    -- ------------------------------------------------------------------
    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO id_machine, update_id, kb, msrcseverity,
                        vglpi_id, vent_id, vhostname, venabled,
                        vjid, vserial, vplatform, vis_active,
                        vname, vcomment, ventity, vlang_code,
                        vold_version, vnew_version, voldcode,
                        vnewcode, visolang;

        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Insertion uniquement si la mise à jour est active
        IF vis_active IS NULL OR vis_active = '1' OR LOWER(vis_active) = 'true' THEN

            IF NOT EXISTS (
                SELECT 1
                FROM up_machine_major_windows
                WHERE id_machine = id_machine
                  AND update_id = update_id
            ) THEN
                INSERT IGNORE INTO up_machine_major_windows (
                    id_machine, update_id, kb, msrcseverity,
                    glpi_id, ent_id, hostname, enabled, jid, serial,
                    platform, is_active, name, comment, entity,
                    lang_code, old_version, new_version, oldcode, newcode, isolang
                )
                VALUES (
                    id_machine, update_id, kb, msrcseverity,
                    vglpi_id, vent_id, vhostname, venabled, vjid, vserial,
                    vplatform, 1, vname, vcomment, ventity,
                    vlang_code, vold_version, vnew_version, voldcode, vnewcode, visolang
                );
            END IF;

        END IF;
    END LOOP;

    CLOSE cur;
END$$

DELIMITER ;
;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 96;

COMMIT;
