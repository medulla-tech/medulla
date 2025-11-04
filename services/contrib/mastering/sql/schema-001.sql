--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/>.


--  ============================================================================
-- Ce script SQL est conçu pour automatiser le processus de passage des mises à jour logicielles
-- d'une "liste grise" vers une "liste blanche"
-- en fonction de règles d'auto-approbation prédéfinies.
--  ============================================================================
START TRANSACTION;

CREATE DATABASE IF NOT EXISTS mastering;
USE mastering;

CREATE TABLE if not exists `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


INSERT INTO `version` VALUES (1);

COMMIT;
