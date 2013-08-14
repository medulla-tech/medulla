--
-- (c) 2013 Mandriva, http://www.mandriva.com/
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


-- Default menu item change on WOL

ALTER TABLE `commands` \
    ADD COLUMN `do_imaging_menu` ENUM('enable','disable') DEFAULT 'disable' NOT NULL;

ALTER TABLE `commands_on_host` \
    ADD COLUMN `imgmenu_changed` ENUM('TODO','IGNORED','DONE','FAILED','WORK_IN_PROGRESS') DEFAULT 'TODO' NOT NULL,
    MODIFY `current_state` ENUM('wol_in_progress',
	                        'wol_done',
				'wol_failed',
		        	'imgmenu_in_progress',
				'imgmenu_done',
				'imgmenu_failed',
				'upload_in_progress',
				'upload_done',
				'upload_failed',
				'execution_in_progress',
				'execution_done',
				'execution_failed',
				'delete_in_progress',
				'delete_done',
				'delete_failed',
				'inventory_in_progress',
				'inventory_done',
				'inventory_failed',
				'reboot_in_progress',
				'reboot_done',
				'reboot_failed',
				'halt_in_progress',
				'halt_done',
				'halt_failed',
				'not_reachable',
				'done',
				'pause',
				'paused',
				'stop',
				'stopped',
				'scheduled',
				're_scheduled',
				'failed',
				'over_timed') DEFAULT 'scheduled' NOT NULL,
    MODIFY `stage` ENUM('pending',
	                'wol_pending',
			'wol_running',
			'wol_requeued',
	                'imgmenu_pending',
			'imgmenu_running',
			'imgmenu_requeued',
			'upload_pending',
			'upload_running',
			'upload_requeued',
			'execution_pending',
			'execution_running',
			'execution_requeued',
			'delete_pending',
			'delete_running',
			'delete_requeued',
			'inventory_pending',
			'inventory_running',
			'inventory_requeued',
			'reboot_pending',
			'reboot_in_progress',
			'reboot_requeued',
			'halt_pending',
			'halt_running',
			'halt_requeued',
			'ended') DEFAULT 'pending' NOT NULL;

ALTER TABLE `commands_history` MODIFY `state` ENUM('wol_in_progress',
	                        'wol_done',
				'wol_failed',
		        	'imgmenu_in_progress',
				'imgmenu_done',
				'imgmenu_failed',
				'upload_in_progress',
				'upload_done',
				'upload_failed',
				'execution_in_progress',
				'execution_done',
				'execution_failed',
				'delete_in_progress',
				'delete_done',
				'delete_failed',
				'inventory_in_progress',
				'inventory_done',
				'inventory_failed',
				'reboot_in_progress',
				'reboot_done',
				'reboot_failed',
				'halt_in_progress',
				'halt_done',
				'halt_failed') DEFAULT NULL;


-- Bump version
DELETE FROM version;
INSERT INTO version VALUES( "20" );

