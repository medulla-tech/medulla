--
-- (c) 2019 Siveo, http://www.siveo.net/
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

-- -----------------------------------------------------
-- Table `xmppmaster`.`substituteconf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `xmppmaster`.`substituteconf` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(45) NOT NULL DEFAULT 'master',
  `jidsubtitute` varchar(255) NOT NULL,
  `countsub` int(11) NOT NULL DEFAULT '0',
  `relayserver_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_substituteconf_relayserver_idx` (`relayserver_id`),
  CONSTRAINT `fk_substituteconf_relayserver_idx` FOREIGN KEY (`relayserver_id`) REFERENCES `relayserver` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 32;

COMMIT;
