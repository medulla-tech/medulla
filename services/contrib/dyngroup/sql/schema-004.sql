--
-- (c) 2008 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Pulse 2, http://pulse2.mandriva.org
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

INSERT INTO GroupType values (2, 'Convergence');
ALTER TABLE `Groups` ADD `parent_id` INT NULL;

CREATE TABLE IF NOT EXISTS `Convergence` (
      `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
      `parentGroupId` int(11) NOT NULL,
      `deployGroupId` int(11) NOT NULL,
      `doneGroupId` int(11) NOT NULL,
      `papi` varchar(255) NOT NULL,
      `packageUUID` varchar(36) NOT NULL,
      `commandId` int(11) NOT NULL,
      `active` int(11) NOT NULL,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB;

UPDATE version set Number = 4;
