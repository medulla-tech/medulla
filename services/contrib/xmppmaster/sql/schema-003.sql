--
-- (c) 2016 Siveo, http://www.siveo.net/
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

--
-- Table structure for table `parameters_deploy`
--

DROP TABLE IF EXISTS `parameters_deploy`;

CREATE TABLE `parameters_deploy` (
  `id` int(11) NOT NULL,
  `command` int(11) NOT NULL,
  `dictionary_data` text NOT NULL,
  `data1` varchar(45) DEFAULT NULL,
  `data2` varchar(45) DEFAULT NULL,
  `data3` varchar(45) DEFAULT NULL,
  `id_machine` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `command_UNIQUE` (`command`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

TRUNCATE `xmppmaster`.`relayserver`;
ALTER TABLE `xmppmaster`.`relayserver`
ADD COLUMN `package_server_ip` VARCHAR(45) NOT NULL AFTER `groupdeploy`,
ADD COLUMN `package_server_port` VARCHAR(45) NOT NULL AFTER `package_server_ip`;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

UPDATE version SET Number = 3;

COMMIT;
