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


-- Alter Users table
ALTER TABLE `Users` CHANGE  `login`  `login` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE `Users` ADD UNIQUE (`login` ,`type`);
-- Add root user if not exists
INSERT IGNORE INTO Users (`login`, `type`) VALUES ('root', 0);

-- Add Update GroupType
INSERT INTO GroupType values (4, 'Update');

-- Insert pulse internal update groups ids start at 2147483000
SET @root_id = (SELECT id FROM Users WHERE login = 'root' AND type = 0);
INSERT INTO Groups (`id`, `name`, `query`, `FK_users`, `type`, `parent_id`) VALUES (2147483000, 'PULSE_INTERNAL_UPDATE_GROUP||Windows XP', '1==glpi::Operating system==*Windows XP*', @root_id, 4, 0);
INSERT INTO Groups (`id`, `name`, `query`, `FK_users`, `type`, `parent_id`) VALUES (2147483001, 'PULSE_INTERNAL_UPDATE_GROUP||Windows Vista', '1==glpi::Operating system==*Windows Vista*', @root_id, 4, 0);
INSERT INTO Groups (`id`, `name`, `query`, `FK_users`, `type`, `parent_id`) VALUES (2147483002, 'PULSE_INTERNAL_UPDATE_GROUP||Windows 7', '1==glpi::Operating system==*Windows 7*', @root_id, 4, 0);
INSERT INTO Groups (`id`, `name`, `query`, `FK_users`, `bool`, `type`, `parent_id`) VALUES (2147483003, 'PULSE_INTERNAL_UPDATE_GROUP||Windows 8', '1==glpi::Operating system==*Windows 8*||2==glpi::Operating system==*Windows RT*', @root_id, 'OR(1, 2)', 4, 0);

UPDATE version set Number = 5;
