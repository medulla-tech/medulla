--
-- (c) 2018 Siveo, http://www.siveo.net/
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
-- insert item params_json  parameters deployement general

START TRANSACTION;

DROP TABLE IF EXISTS `xmppmaster`.`cluster_resources` ;

--
-- Table cluster_resources
--

CREATE TABLE  IF NOT EXISTS `xmppmaster`.`cluster_resources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` VARCHAR(45) NULL,
  `jidmachine` VARCHAR(255) NOT NULL,
  `jidrelay` VARCHAR(255) NOT NULL,
  `startcmd` TIMESTAMP NULL,
  `endcmd` TIMESTAMP NULL,
  `login` VARCHAR(45) NULL,
  `sessionid` VARCHAR(45) NULL,
  PRIMARY KEY (`id`));


UPDATE version SET Number = 23;

COMMIT;
