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

ALTER TABLE `commands_on_host` \
    MODIFY `current_state` ENUM("wol_in_progress", "wol_done", "wol_failed", "upload_in_progress", "upload_done", "upload_failed", "execution_in_progress", "execution_done", "execution_failed", "delete_in_progress", "delete_done", "delete_failed", "inventory_in_progress", "inventory_done", "inventory_failed", "not_reachable", "done", "pause", "stop", "scheduled", "failed") DEFAULT "scheduled" NOT NULL;

UPDATE `commands_on_host` \
    SET `current_state` = "failed" WHERE `current_state` = 0;

ALTER TABLE `commands` \
    ADD COLUMN `package_id` VARCHAR(255) DEFAULT NULL;

DELETE FROM version;
INSERT INTO version VALUES( "12" );
