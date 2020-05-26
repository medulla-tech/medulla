--
-- (c) 2020 Siveo, http://www.siveo.net/
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

-- ----------------------------------------------------------------------
-- link has_guacamole with xmppmaster table machine. (no glpi)
-- ----------------------------------------------------------------------

START TRANSACTION;
-- ----------------------------------------------------------------------
-- Database chang colunm
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`has_guacamole` 
CHANGE COLUMN `idinventory` `machine_id` INT(11) NOT NULL ;

-- ----------------------------------------------------------------------
-- Database add index fk_has_guacamole_machineid_idx for contrainte
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`has_guacamole` 
ADD INDEX `fk_has_guacamole_machineid_idx` (`machine_id` ASC) ;

-- ----------------------------------------------------------------------
-- add contrainte
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`has_guacamole` 
ADD CONSTRAINT `fk_has_guacamole_machineid_idx`
  FOREIGN KEY (`machine_id`)
  REFERENCES `xmppmaster`.`machines` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 43;

COMMIT;
