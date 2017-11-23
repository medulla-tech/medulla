--
-- (c) 2017 Siveo, http://www.siveo.net/
--
-- $Id$
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

-- --------------------------------------------------------------
-- command customizer by user for console xmpp
-- --------------------------------------------------------------


DROP TABLE IF EXISTS `xmppmaster`.`qa_custom_command` ;

CREATE TABLE IF NOT EXISTS `xmppmaster`.`qa_custom_command` (
  `user` VARCHAR(45) NOT NULL,
  `os` VARCHAR(45) NOT NULL,
  `namecmd` VARCHAR(45) NOT NULL,
  `customcmd` TEXT NOT NULL,
  `description` VARCHAR(45) NULL DEFAULT '\"\"',
  PRIMARY KEY (`namecmd`, `user`, `os`))
ENGINE = InnoDB;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 9;

COMMIT;
