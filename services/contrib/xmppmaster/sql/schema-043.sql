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

-- deactivation check contrainte
SET FOREIGN_KEY_CHECKS=0;

CREATE TABLE `xmppmaster`.`temp_table` as
SELECT
	xmppmaster.has_guacamole.id,
    xmppmaster.has_guacamole.idguacamole,
    xmppmaster.has_guacamole.idinventory,
    xmppmaster.has_guacamole.protocol,
    xmppmaster.machines.id AS machine_id
FROM
    xmppmaster.has_guacamole
        INNER JOIN
    xmppmaster.machines ON SUBSTRING(xmppmaster.machines.uuid_inventorymachine,
        5,
        LENGTH(xmppmaster.machines.uuid_inventorymachine)) = xmppmaster.has_guacamole.idinventory;

ALTER TABLE `xmppmaster`.`temp_table`
DROP COLUMN `idinventory`;

ALTER TABLE `xmppmaster`.`temp_table`
CHANGE COLUMN `id` `id` INT(11) NOT NULL AUTO_INCREMENT ,
CHANGE COLUMN `machine_id` `machine_id` INT(11) NOT NULL ,
ADD PRIMARY KEY (`id`, `idguacamole`, `protocol`);

-- ----------------------------------------------------------------------
-- Database add index fk_has_guacamole_machineid_idx for contrainte
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`temp_table`
ADD INDEX `fk_has_guacamole_machineid_idx` (`machine_id` ASC) ;
-- ----------------------------------------------------------------------
-- add contrainte
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`temp_table`
ADD CONSTRAINT `fk_has_guacamole_machineid_idx`
  FOREIGN KEY (`machine_id`)
  REFERENCES `xmppmaster`.`machines` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;

DROP TABLE has_guacamole;
ALTER TABLE xmppmaster.temp_table RENAME AS xmppmaster.has_guacamole;
-- reactivation check contrainte
SET FOREIGN_KEY_CHECKS=1;
UPDATE version SET Number = 43;

COMMIT;
