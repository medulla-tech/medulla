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
-- Cree la table `mmc_module_actif` s'il n'existe pas deja.
-- Cette table permet de mettre a disposition des informations au substitut via la base de donnees.
-- ----------------------------------------------------------------------

-- Cette table est mise a jour a chaque demarrage de l'agent mmc.
-- Lors du demarrage, l'agent mmc met a jour cette table a l'initialisation de xmpp.

-- Les modules actives par la configuration sont des informations directement accessibles au substitus
-- qui ont acces a xmppmaster.
CREATE TABLE IF NOT EXISTS `xmppmaster`.`mmc_module_actif` (
  `name_module` VARCHAR(40) NOT NULL,  -- Nom du module (chaîne de caracteres jusqu'a 40 caracteres)
  `enable` INT NOT NULL DEFAULT 0,    -- Activation du module (entier non nul, par defaut a 0)
  `informations` VARCHAR(1024) NULL,  -- Informations supplementaires (chaîne de caracteres jusqu'a 1024 caracteres, peut être nul)
  PRIMARY KEY (`name_module`)         -- Cle primaire sur le nom du module
);

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 83;

COMMIT;
