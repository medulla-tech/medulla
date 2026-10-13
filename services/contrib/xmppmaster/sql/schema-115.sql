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

-- Création de la procédure stockée qui initialise la table des paquets Windows 11 x64 26H2.
-- Cette procédure recrée la table `up_packages_Win11_X64_26H2` à partir des données de `update_data`.
-- Elle ne garde que les mises à jour concernées par Windows 11 Version 26H2,
-- avec le bon produit, sans ARM64/X86 ni paquets dynamiques.

-- La procédure stockée existe déjà mais cible les Windows 11 25H2
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
            aa.title LIKE '%Windows 11 Version 26H2%'
            AND aa.product LIKE '%Windows 11%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%X86%'
            AND aa.title NOT LIKE '%Dynamic%';
END //
DELIMITER ;


-- Enregistre le produit Windows 11 26H2 dans la configuration des applications.
-- La table des produits utilisée pour ce package est `up_packages_Win11_X64_26H2`.
insert into applicationconfig (`key`, `value`, `comment`, context, module, `enable`) values("table produits", "up_packages_Win11_X64_26H2", "Microsoft Windows 11 [ fin support 2028/10 ]", "entity", "xmppmaster/update", 1);
update applicationconfig set enable=1, comment="" where values("table produits", "up_packages_Win11_X64_26H2", "Microsoft Windows 11 [ fin support 2028/10 ]", "entity", "xmppmaster/update", 1);

-- Fichiers ISO disponibles pour les build Windows 11 25H2 et 26H2.
-- Ces lignes servent de documentation de configuration et de référence des packages gestionnés.
-- Elements à désactiver
-- rw-r--r-- 1 root root 7754645504 Sep 30 2025 Win11_25H2_English_UK_x64.iso
-- -rw-r--r-- 1 root root 8471603200 Mar 19 2026 Win11_25H2_English_US_x64.iso
-- -rw-r--r-- 1 root root 7746467840 Sep 30 2025 Win11_25H2_French_x64.iso
-- Elements à ajouter et activer
-- -rw-r--r-- 1 root root 9061271552 Sep 30 01:10 Win11_26H2_English_UK_x64.iso
-- -rw-r--r-- 1 root root 9047330816 Sep 30 01:10 Win11_26H2_English_US_x64.iso
-- -rw-r--r-- 1 root root 9062821888 Sep 30 01:10 Win11_26H2_French_x64.iso

-- Désactive les anciens paquets Windows 11 25H2 pour ne plus proposer ces versions en tant que livrables actifs.
UPDATE `up_packages_major_Lang_code` SET `enabled` = 0 WHERE iso_filename = 'Win11_25H2_English_UK_x64.iso';
UPDATE `up_packages_major_Lang_code` SET `enabled` = 0 WHERE iso_filename = 'Win11_25H2_English_US_x64.iso';
UPDATE `up_packages_major_Lang_code` SET `enabled` = 0 WHERE iso_filename = 'Win11_25H2_French_x64.iso';

-- Ajoute les nouveaux packages Windows 11 26H2 pour les langues supportées.
-- `INSERT IGNORE` évite les doublons si la ligne existe déjà.
INSERT IGNORE INTO `up_packages_major_Lang_code` VALUES (11, 'en-GB', '0809', 'English - United Kingdom', 1, 'Win11_26H2_English_UK_x64.iso', 'Win11upd_26H2_English_UK_x64_pbqbowfj6h9lom');
INSERT IGNORE INTO `up_packages_major_Lang_code` VALUES (11, 'en-US', '0409', 'English - United States', 1, 'Win11_26H2_English_US_x64.iso', 'Win11upd_26H2_English_US_x64_pbqbowfj6h9lom');
INSERT IGNORE INTO `up_packages_major_Lang_code` VALUES (11, 'fr-FR', '040C', 'French', 1, 'Win11_26H2_French_x64.iso', 'Win11upd_26H2_French_x64_pbqbowfj6h9lom');

-- Normalise les identifiants de package en ne conservant que les 36 premiers caractères.
-- Cela évite les valeurs trop longues des UUID générées dans un autre format.
UPDATE `xmppmaster`.`up_packages_major_Lang_code`
SET `package_uuid` = LEFT(COALESCE(`package_uuid`, ''), 36)
WHERE CHAR_LENGTH(COALESCE(`package_uuid`, '')) > 36;

CALL up_create_product_tables();

UPDATE version SET Number = 115;

commit;