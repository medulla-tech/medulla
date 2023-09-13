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
-- Crée la table `mmc_module_actif` s'il n'existe pas déjà.
-- Cette table permet de mettre à disposition des informations au substitut via la base de données.
-- ----------------------------------------------------------------------

-- Cette table est mise à jour à chaque démarrage de l'agent mmc.
-- Lors du démarrage, l'agent mmc met à jour cette table à l'initialisation de xmpp.

-- Les modules activés par la configuration sont des informations directement accessibles au substitus
-- qui ont accès à xmppmaster.
CREATE TABLE IF NOT EXISTS `xmppmaster`.`mmc_module_actif` (
  `name_module` VARCHAR(40) NOT NULL,  -- Nom du module (chaîne de caractères jusqu'à 40 caractères)
  `enable` INT NOT NULL DEFAULT 0,    -- Activation du module (entier non nul, par défaut à 0)
  `informations` VARCHAR(1024) NULL,  -- Informations supplémentaires (chaîne de caractères jusqu'à 1024 caractères, peut être nul)
  PRIMARY KEY (`name_module`)         -- Clé primaire sur le nom du module
);

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 83;

COMMIT;
