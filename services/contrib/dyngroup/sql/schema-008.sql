-- SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/dyngroup/sql/schema-008.sql
--
-- Retrait de l'ancien moteur des mises a jour : procedure sans appelant,
-- sa table de langues et les groupes techniques des mises a niveau majeures Windows.
-- Lignes liees d'abord : selon la version du serveur, l'ancienne contrainte sans
-- ON DELETE CASCADE a survecu au schema 007, qui la cherche sous un autre nom.
-- Groupes _ALL_LANG ensuite : leur requete cite les autres, et
-- Groups_BEFORE_DELETE refuse de supprimer un groupe cite par un autre.

USE `dyngroup`;

START TRANSACTION;

DROP PROCEDURE IF EXISTS `create_groups_major_update_win`;
DROP TABLE IF EXISTS `Lang_code_windows`;


SET @major_groups = '!_@med!_Grp!_Major!_update!_win!_%';

DELETE FROM `Results`
 WHERE `FK_groups` IN (SELECT `id` FROM `Groups` WHERE `name` LIKE @major_groups ESCAPE '!');
DELETE FROM `ShareGroup`
 WHERE `FK_groups` IN (SELECT `id` FROM `Groups` WHERE `name` LIKE @major_groups ESCAPE '!');
DELETE FROM `ProfilesResults`
 WHERE `FK_groups` IN (SELECT `id` FROM `Groups` WHERE `name` LIKE @major_groups ESCAPE '!');
DELETE FROM `ProfilesPackages`
 WHERE `FK_groups` IN (SELECT `id` FROM `Groups` WHERE `name` LIKE @major_groups ESCAPE '!');
DELETE FROM `ProfilesData`
 WHERE `FK_groups` IN (SELECT `id` FROM `Groups` WHERE `name` LIKE @major_groups ESCAPE '!');

DELETE FROM `Groups`
 WHERE `name` LIKE '!_@med!_Grp!_Major!_update!_win!_%!_ALL!_LANG' ESCAPE '!';
DELETE FROM `Groups`
 WHERE `name` LIKE @major_groups ESCAPE '!';

UPDATE version SET Number = 8;

COMMIT;
