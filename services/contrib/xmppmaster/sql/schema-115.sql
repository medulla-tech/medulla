-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-115.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- 

USE `xmppmaster`;

START TRANSACTION;

-- Creation de la procedure stockee qui initialise la table des paquets Windows 11 x64 26H2.
-- Cette procedure recree la table `up_packages_Win11_X64_26H2` a partir des donnees de `update_data`.
-- Elle ne garde que les mises a jour concernees par Windows 11 Version 26H2,
-- avec le bon produit, sans ARM64/X86 ni paquets dynamiques.

-- La procedure stockee existe deja mais cible les Windows 11 25H2
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_26H2`;

DELIMITER //
CREATE PROCEDURE IF NOT EXISTS `up_init_packages_Win11_X64_26H2`()
BEGIN
    DROP TABLE IF EXISTS up_packages_Win11_X64_26H2;
    CREATE TABLE up_packages_Win11_X64_26H2 AS
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
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
         WHERE
            aa.title LIKE '%Windows 11, Version 26H2%'
            AND aa.product LIKE '%Windows 11%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END //
DELIMITER ;

update applicationconfig set `enable`=1, `comment`="Microsoft Windows 11 [ fin support 2028/10 ]" where value="up_packages_Win11_X64_26H2";

-- Fichiers ISO disponibles pour les build Windows 11 25H2 et 26H2.
-- Ces lignes servent de documentation de configuration et de reference des packages gestionnes.
-- Elements a desactiver
-- rw-r--r-- 1 root root 7754645504 Sep 30 2025 Win11_25H2_English_UK_x64.iso
-- -rw-r--r-- 1 root root 8471603200 Mar 19 2026 Win11_25H2_English_US_x64.iso
-- -rw-r--r-- 1 root root 7746467840 Sep 30 2025 Win11_25H2_French_x64.iso
-- Elements a ajouter et activer
-- -rw-r--r-- 1 root root 9061271552 Sep 30 01:10 Win11_26H2_English_UK_x64.iso
-- -rw-r--r-- 1 root root 9047330816 Sep 30 01:10 Win11_26H2_English_US_x64.iso
-- -rw-r--r-- 1 root root 9062821888 Sep 30 01:10 Win11_26H2_French_x64.iso

-- Desactive les anciens paquets Windows 11 25H2 pour ne plus proposer ces versions en tant que livrables actifs.
UPDATE `up_packages_major_Lang_code` SET `enabled` = 0 WHERE iso_filename = 'Win11_25H2_English_UK_x64.iso';
UPDATE `up_packages_major_Lang_code` SET `enabled` = 0 WHERE iso_filename = 'Win11_25H2_English_US_x64.iso';
UPDATE `up_packages_major_Lang_code` SET `enabled` = 0 WHERE iso_filename = 'Win11_25H2_French_x64.iso';

-- Ajoute les nouveaux packages Windows 11 26H2 pour les langues supportees.
-- `INSERT IGNORE` evite les doublons si la ligne existe deja.
INSERT IGNORE INTO `up_packages_major_Lang_code` VALUES (11, 'en-GB', '0809', 'English - United Kingdom', 1, 'Win11_26H2_English_UK_x64.iso', 'Win11upd_26H2_English_UK_x64_pbqbowfj6h9lom');
INSERT IGNORE INTO `up_packages_major_Lang_code` VALUES (11, 'en-US', '0409', 'English - United States', 1, 'Win11_26H2_English_US_x64.iso', 'Win11upd_26H2_English_US_x64_pbqbowfj6h9lom');
INSERT IGNORE INTO `up_packages_major_Lang_code` VALUES (11, 'fr-FR', '040C', 'French', 1, 'Win11_26H2_French_x64.iso', 'Win11upd_26H2_French_x64_pbqbowfj6h9lom');

-- Normalise les identifiants de package en ne conservant que les 36 premiers caracteres.
-- Cela evite les valeurs trop longues des UUID generees dans un autre format.
UPDATE `xmppmaster`.`up_packages_major_Lang_code`
SET `package_uuid` = LEFT(COALESCE(`package_uuid`, ''), 36)
WHERE CHAR_LENGTH(COALESCE(`package_uuid`, '')) > 36;

-- Redefinit la procedure de reconstruction des upgrades Windows majeurs
-- pour ne retenir que la ligne de package active par langue/version.
DELIMITER $$

DROP PROCEDURE IF EXISTS `up_init_table_major_win_complet`$$
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_table_major_win_complet`$$

CREATE PROCEDURE `up_init_table_major_win_complet`()
BEGIN
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
   ),
   mx_one AS (
      SELECT
         m1.id,
         m1.hostname,
         m1.enabled,
         m1.jid,
         m1.uuid_serial_machine,
         m1.platform,
         NULLIF(REPLACE(m1.uuid_inventorymachine, 'UUID', ''), '') AS glpi_machine_id
      FROM xmppmaster.machines m1
      INNER JOIN (
         SELECT
            mxn.glpi_machine_id,
            COALESCE(
               NULLIF(MAX(CASE WHEN mxn.enabled = 1 THEN mxn.id ELSE 0 END), 0),
               MAX(mxn.id)
            ) AS selected_id
         FROM (
            SELECT
               id,
               enabled,
               NULLIF(REPLACE(uuid_inventorymachine, 'UUID', ''), '') AS glpi_machine_id
            FROM xmppmaster.machines
         ) mxn
         WHERE mxn.glpi_machine_id IS NOT NULL
           AND mxn.glpi_machine_id <> ''
         GROUP BY mxn.glpi_machine_id
      ) mx_pick ON mx_pick.selected_id = m1.id
   )
   SELECT
      mx.id AS xmpp_id,
      m.id AS glpi_id,
      COALESCE(e.id, m.entities_id) AS ent_id,
      COALESCE(NULLIF(m.name, ''), mx.hostname) AS hostname,
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
   INNER JOIN mx_one mx ON mx.glpi_machine_id = si.items_id
   LEFT JOIN xmppmaster.up_packages_major_Lang_code lc
      ON lc.lang_code = parts.part3
      AND lc.major = SUBSTRING_INDEX(parts.part7, '-', -1)
      AND lc.enabled = 1
   WHERE s.name LIKE 'Medulla\_%';

   COMMIT;

   TRUNCATE TABLE up_machine_major_windows;

   INSERT INTO up_machine_major_windows (
      id_machine, update_id, kb, msrcseverity,
      glpi_id, ent_id, hostname, enabled, jid, serial,
      platform, is_active, name, comment, entity,
      lang_code, old_version, new_version, oldcode, newcode, isolang
   )
   SELECT
      xmpp_id,
      LEFT(COALESCE(package_uuid, ''), 36),
      LEFT(COALESCE(package_uuid, ''), 36),
      NULL,
      glpi_id,
      ent_id,
      hostname,
      enabled,
      jid,
      serial,
      platform,
      'True',
      name,
      comment,
      entity,
      lang_code,
      old_version,
      new_version,
      oldcode,
      newcode,
      isolang
   FROM up_major_win
   WHERE
      (
         TRIM(COALESCE(old_version, '')) = '11'
         AND TRIM(COALESCE(new_version, '')) = '11'
         AND UPPER(TRIM(COALESCE(oldcode, ''))) != UPPER(TRIM(COALESCE(newcode, '')))
         AND UPPER(TRIM(COALESCE(oldcode, ''))) != '26H1'
      )
      OR
      (
         TRIM(COALESCE(old_version, '')) = '10'
         AND TRIM(COALESCE(new_version, '')) = '11'
         AND UPPER(TRIM(COALESCE(is_active, ''))) = 'TRUE'
      );
END$$

DELIMITER ;

-- Limite le temps de migration en ne regenerant que la table produit
-- introduite par ce schema, au lieu de reconstruire toutes les tables produits.
CALL up_init_packages_Win11_X64_26H2();

-- Laisse le cron reconstruire les donnees avec la nouvelle logique.
-- up_machine_major_windows existe deja via les schemas precedents.
TRUNCATE TABLE up_machine_major_windows;

-- up_major_win est normalement recreee par la procedure. Sur certaines bases,
-- elle peut ne pas encore exister au moment de la migration, donc on la cree
-- vide ici pour eviter a la fois les erreurs SQL et les donnees stale.
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

TRUNCATE TABLE up_major_win;

UPDATE version SET Number = 115;

commit;
