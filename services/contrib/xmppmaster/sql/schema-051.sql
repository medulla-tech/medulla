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

-- Fixes for mariadb 10.3

START TRANSACTION;

USE `xmppmaster`;

UPDATE `rules` SET `description`='Chooses ARS based on user' WHERE `id`=1;
UPDATE `rules` SET `description`='Chooses ARS based on hostname' WHERE `id`=2;
UPDATE `rules` SET `description`='Chooses ARS based on best location' WHERE `id`=3;
UPDATE `rules` SET `description`='Chooses ARS in same subnet' WHERE `id`=4;
UPDATE `rules` SET `description`='Use default ARS' WHERE `id`=5;
UPDATE `rules` SET `description`='Chooses the least used ARS' WHERE `id`=6;
UPDATE `rules` SET `description`='Chooses ARS based on AD machines OUs' WHERE `id`=7;
UPDATE `rules` SET `description`='Chooses ARS based on AD users OUs' WHERE `id`=8;
UPDATE `rules` SET `description`='Chooses ARS based on network address' WHERE `id`=9;
UPDATE `rules` SET `description`='Chooses ARS based on netmask' WHERE `id`=10;

UPDATE `qa_custom_command` SET `description`='Download agent log to file-transfer folder' WHERE `namecmd`='Download agent log to file-transfer folder';
UPDATE `qa_custom_command` SET `description`='Restart Pulse Agent service' WHERE `namecmd`='Restart Pulse Agent service';

ALTER TABLE `xmppmaster`.`qa_relay_launched` CHANGE COLUMN `command_start` `command_start` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP;

UPDATE version SET Number = 51;

COMMIT;
