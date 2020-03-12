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

-- add FOREIGN KEY in table network on table machines  

ALTER TABLE `xmppmaster`.`network` 
ADD INDEX `fk_network_idx_machine` (`machines_id` ASC);


ALTER TABLE `xmppmaster`.`network` 
ADD CONSTRAINT `fk_network_idx_machine`
  FOREIGN KEY (`machines_id`)
  REFERENCES `xmppmaster`.`machines` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE;
  
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 36;
