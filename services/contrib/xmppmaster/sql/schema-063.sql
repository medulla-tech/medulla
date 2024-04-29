--
-- (c) 2021 Siveo, http://www.siveo.net/
--
--
-- This file is part of Medulla 2, http://www.siveo.net/
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

START TRANSACTION;

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------
-- ----------------------------------------------------------------------
-- Creation table medulla_users
-- This table is used to define users. We attribute them preferences and permissions to allow to visualize shares
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `medulla_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(255) NOT NULL,
  `comment` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login_UNIQUE` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
-- ----------------------------------------------------------------------
-- Creation table medulla_teams
-- This table is used to define the teams
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `medulla_teams` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Define the team',
  `name` varchar(120) NOT NULL,
  `comment` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Creation table medulla_preferences
-- This table allow to attribute preferences in a key/value format to one user
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `medulla_preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(120) NOT NULL,
  `value` text DEFAULT '',
  `id_user` int(11) NOT NULL,
  `domain` varchar(80) DEFAULT NULL COMMENT 'This field can set preferences to a domain ( a domain can be a web page for ex. )',
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_UNIQUE` (`key`,`id_user`,`domain`),
  KEY `fk_medulla_preferences_1_idx` (`id_user`),
  CONSTRAINT `fk_medulla_preferences_1` FOREIGN KEY (`id_user`) REFERENCES `medulla_users` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Creation table medulla_team_user
-- This table is used to create teams
-- ----------------------------------------------------------------------

 CREATE TABLE IF NOT EXISTS `medulla_team_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) DEFAULT NULL,
  `id_team` int(11) DEFAULT NULL,
  `comment` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unix_team_user` (`id_user`,`id_team`),
  KEY `fk_medulla_team_user_1_idx` (`id_user`),
  KEY `fk_medulla_team_user_2_idx` (`id_team`),
  CONSTRAINT `fk_medulla_team_user_1` FOREIGN KEY (`id_user`) REFERENCES `medulla_users` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
  CONSTRAINT `fk_medulla_team_user_2` FOREIGN KEY (`id_team`) REFERENCES `medulla_teams` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------------------------------------------------
-- create use root
-- ----------------------------------------------------------------------

INSERT IGNORE INTO `xmppmaster`.`medulla_users` (`login`) VALUES ('root');

-- ----------------------------------------------------------------------
-- Add in table logs index on date
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`logs`
ADD INDEX IF NOT EXISTS `ind_date_log` (`date` ASC) ;

-- ----------------------------------------------------------------------
-- change size coluum in table logs field text
-- -----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`logs`
CHANGE COLUMN `text` `text` VARCHAR(4096) NOT NULL ;

-- les champs de la tables historylogs doivent correspondre au champ de la table logs. ------------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `text` `text` VARCHAR(4096) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `type` `type` VARCHAR(25) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `module` `module` VARCHAR(255) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `fromuser` `fromuser` VARCHAR(255) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `touser` `touser` VARCHAR(255) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `who` `who` VARCHAR(255) NULL DEFAULT NULL ;

SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 63;

COMMIT;
