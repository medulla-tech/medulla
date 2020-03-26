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

START TRANSACTION;

-- -----------------------------------------------------
-- Table `xmppmaster`.`def_remote_deploy_status`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `xmppmaster`.`def_remote_deploy_status` ;
CREATE TABLE IF NOT EXISTS `xmppmaster`.`def_remote_deploy_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `regex_logmessage` varchar(80) NOT NULL,
  `status` varchar(80) NOT NULL,
  `label` varchar(255) NOT NULL,
  `type` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
COMMENT = 'this table allows you to define the regexp to apply 1 status according to 1 log of type deploy';

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 35;

COMMIT;
