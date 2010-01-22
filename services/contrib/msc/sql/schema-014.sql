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
    CHANGE `bundle_id` `fk_bundle` INT DEFAULT NULL, \
    ADD COLUMN `do_halt` SET("on_done", "on_failed", "on_over_timed", "on_out_of_time_interval") DEFAULT "" NOT NULL AFTER `do_reboot`, \
    ADD COLUMN `state` ENUM("active", "archived", "disabled", "template") DEFAULT "active" NOT NULL AFTER id;

ALTER TABLE `target` \
    DROP COLUMN `scheduler`;

ALTER TABLE `commands_on_host` \
    ADD COLUMN `awoken` ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS") DEFAULT "TODO" NOT NULL AFTER `current_state`, \
    ADD COLUMN `inventoried` ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS") DEFAULT "TODO" NOT NULL AFTER `deleted`, \
    ADD COLUMN `rebooted` ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS") DEFAULT "TODO" NOT NULL AFTER `inventoried`, \
    ADD COLUMN `halted` ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS") DEFAULT "TODO" NOT NULL AFTER `rebooted`, \
    MODIFY `current_state` ENUM("wol_in_progress", "wol_done", "wol_failed", "upload_in_progress", "upload_done", "upload_failed", "execution_in_progress", "execution_done", "execution_failed", "delete_in_progress", "delete_done", "delete_failed", "inventory_in_progress", "inventory_done", "inventory_failed", "reboot_in_progress", "reboot_done", "reboot_failed", "halt_in_progress", "halt_done", "halt_failed", "not_reachable", "done", "pause", "paused", "stop", "stopped", "scheduled", "re_scheduled", "failed", "over_timed") DEFAULT "scheduled" NOT NULL, \
    ADD COLUMN `stage` ENUM("pending", "wol_pending", "wol_running", "wol_requeued", "upload_pending", "upload_running", "upload_requeued", "execution_pending", "execution_running", "execution_requeued", "delete_pending", "delete_running", "delete_requeued", "inventory_pending", "inventory_running", "inventory_requeued", "reboot_pending", "reboot_in_progress", "reboot_requeued", "halt_pending", "halt_running", "halt_requeued", "ended") DEFAULT "pending" NOT NULL AFTER current_state;

ALTER TABLE `commands_history` \
    MODIFY `state` ENUM("wol_in_progress", "wol_done", "wol_failed", "upload_in_progress", "upload_done", "upload_failed", "execution_in_progress", "execution_done", "execution_failed", "delete_in_progress", "delete_done", "delete_failed", "inventory_in_progress", "inventory_done", "inventory_failed", "reboot_in_progress", "reboot_done", "reboot_failed", "halt_in_progress", "halt_done", "halt_failed");

UPDATE `commands_on_host` SET `stage` = "wol_running" where current_state = "wol_in_progress";
UPDATE `commands_on_host` SET `stage` = "upload_running" where uploaded="WORK_IN_PROGRESS";
UPDATE `commands_on_host` SET `stage` = "upload_requeued" where current_state = "scheduled" and uploaded="FAILED";
UPDATE `commands_on_host` SET `stage` = "execution_pending" where uploaded="DONE" and executed="TODO";
UPDATE `commands_on_host` SET `stage` = "execution_running" where executed="WORK_IN_PROGRESS";
UPDATE `commands_on_host` SET `stage` = "execution_requeued" where current_state = "scheduled" and executed="FAILED";
UPDATE `commands_on_host` SET `stage` = "delete_pending" where executed="DONE" and deleted="TODO";
UPDATE `commands_on_host` SET `stage` = "delete_running" where deleted="WORK_IN_PROGRESS";
UPDATE `commands_on_host` SET `stage` = "delete_requeued" where current_state = "scheduled" and deleted="FAILED";
UPDATE `commands_on_host` SET `stage` = "ended" where `current_state` = "failed" or `current_state` = "done";

DELETE FROM version;
INSERT INTO version VALUES( "14" );


