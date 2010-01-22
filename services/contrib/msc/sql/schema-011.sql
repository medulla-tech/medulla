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

UPDATE `commands` \
    SET `delete_file_after_execute_successful` = "enable" WHERE `delete_file_after_execute_successful` IS NULL OR `delete_file_after_execute_successful` = "";
UPDATE `commands` \
    SET `start_inventory` = "disable" WHERE `start_inventory` IS NULL OR `start_inventory` = "";
UPDATE `commands` \
    SET `wake_on_lan` = "disable" WHERE `wake_on_lan` IS NULL OR `wake_on_lan` = "";
UPDATE `commands` \
    SET `username` = NULL WHERE `username` = "";
UPDATE `commands` \
    SET `webmin_username` = NULL WHERE `webmin_username` = "";
UPDATE `commands` \
    SET `title` = NULL WHERE `title` = "";

UPDATE `commands_on_host` \
    SET `uploaded` = "TODO" WHERE `uploaded` IS NULL OR `uploaded` = "";
UPDATE `commands_on_host` \
    SET `executed` = "TODO" WHERE `executed` IS NULL OR `executed` = "";
UPDATE `commands_on_host` \
    SET `deleted` = "TODO" WHERE `deleted` IS NULL OR `deleted` = "";
UPDATE `commands_on_host` \
    SET `current_state` = "scheduled" WHERE `current_state` IS NULL OR `current_state` = "";

ALTER TABLE `commands` \
    CHANGE `delete_file_after_execute_successful` `clean_on_success` ENUM("enable", "disable") DEFAULT "enable" NOT NULL, \
    CHANGE `start_inventory` `do_inventory` ENUM("enable","disable") DEFAULT "disable" NOT NULL, \
    CHANGE `wake_on_lan` `do_wol` ENUM("enable","disable") DEFAULT "disable" NOT NULL, \
    CHANGE `username` `connect_as` VARCHAR(255) DEFAULT NULL, \
    CHANGE `webmin_username` `creator` VARCHAR(255) DEFAULT NULL, \
    MODIFY `title` VARCHAR(255) DEFAULT NULL, \
    CHANGE `date_created` `creation_date` DATETIME NOT NULL, \
    DROP COLUMN `repeat`, \
    ADD COLUMN `do_reboot` ENUM("enable", "disable") DEFAULT "disable" NOT NULL, \
    ADD COLUMN `bundle_id` INT DEFAULT NULL, \
    ADD COLUMN `order_in_bundle` SMALLINT DEFAULT NULL, \
    ADD KEY(`bundle_id`);

ALTER TABLE `commands_on_host` \
    CHANGE `number_attempt_connection_remains` `attempts_left` SMALLINT DEFAULT NULL, \
    MODIFY `uploaded` ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS") DEFAULT "TODO" NOT NULL, \
    MODIFY `executed` ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS") DEFAULT "TODO" NOT NULL, \
    MODIFY `deleted` ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS") DEFAULT "TODO" NOT NULL, \
    MODIFY `current_state` ENUM("wol_in_progress", "wol_done", "wol_failed", "upload_in_progress", "upload_done", "upload_failed", "execution_in_progress", "execution_done", "execution_failed", "delete_in_progress", "delete_done", "delete_failed", "inventory_in_progress", "inventory_done", "inventory_failed", "not_reachable", "done", "pause", "stop", "scheduled") DEFAULT "scheduled" NOT NULL, \
    DROP KEY `id_command`, \
    ADD KEY(`fk_commands`), \
    ADD KEY(`scheduler`);

ALTER TABLE `commands_history` \
    MODIFY `state` ENUM("wol_in_progress", "wol_done", "wol_failed", "upload_in_progress", "upload_done", "upload_failed", "execution_in_progress", "execution_done", "execution_failed", "delete_in_progress", "delete_done", "delete_failed", "inventory_in_progress", "inventory_done", "inventory_failed", "reboot_in_progress", "reboot_done", "reboot_failed"), \
    DROP KEY `id_command_on_host`, \
    ADD KEY(`fk_commands_on_host`);

ALTER TABLE `target` \
    ADD KEY(`target_uuid`(10));
CREATE TABLE IF NOT EXISTS bundle ( \
    id INT NOT NULL AUTO_INCREMENT, \
    title VARCHAR(255) DEFAULT NULL, \
    do_reboot ENUM("enable", "disable") DEFAULT "disable" NOT NULL, \
    PRIMARY KEY (id) \
);

DELETE FROM version;
INSERT INTO version VALUES( "11" );
