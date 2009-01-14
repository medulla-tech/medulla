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

ALTER TABLE `commands` \
    DROP COLUMN `path_destination`,\
    DROP COLUMN `path_source`,\
    DROP COLUMN `create_directory`,\
    CHANGE `id_command` `id` INT(11) NOT NULL AUTO_INCREMENT,\
    ADD COLUMN `maxbw` int(11) DEFAULT '0';
ALTER TABLE `commands_on_host` \
    DROP COLUMN current_pid,\
    CHANGE `id_command_on_host` `id` INT(11) NOT NULL AUTO_INCREMENT,\
    CHANGE `id_command` `fk_commands` int(11) NOT NULL DEFAULT '0';
ALTER TABLE `commands_history` \
    CHANGE `id_command_history` `id` INT(11) NOT NULL AUTO_INCREMENT,\
    CHANGE `id_command_on_host` `fk_commands_on_host` int(11) NOT NULL DEFAULT '0';
ALTER TABLE `target` \
    CHANGE `id_command` `fk_commands` INT(11) NOT NULL DEFAULT '0',\
    CHANGE `id_command_on_host` `fk_commands_on_host` int(11) DEFAULT NULL;

DELETE FROM version;
INSERT INTO version VALUES( '6' );
