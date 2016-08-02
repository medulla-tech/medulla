--
-- (c) 2008 Mandriva, http://www.mandriva.com/
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

-- Tranforming the workflow to dynamic. 
-- Each record in commands_on_hosts_phase corrensponds to one phase
-- in the actual workflow.

CREATE TABLE IF NOT EXISTS phase (
    id INT NOT NULL AUTO_INCREMENT,
    fk_commands_on_host INT NOT NULL,
    phase_order INT NOT NULL, 
    name VARCHAR(32) NOT NULL,
    state ENUM ("ready", 
	        "running",
	        "done", 
		"failed") DEFAULT "ready" NOT NULL,
    PRIMARY KEY(id),
    FOREIGN KEY (fk_commands_on_host) REFERENCES commands_on_host(id)
    ) ENGINE=MYISAM;

ALTER TABLE commands ADD COLUMN sum_running INT NOT NULL DEFAULT 0;
ALTER TABLE commands ADD COLUMN sum_failed INT NOT NULL DEFAULT 0;
ALTER TABLE commands ADD COLUMN sum_done INT NOT NULL DEFAULT 0;


ALTER TABLE commands_on_host \
    MODIFY current_state ENUM('done',
                              'stopped',
                              'scheduled',
                              'failed',
                              'in_progress',
                              'over_timed') DEFAULT 'scheduled' NOT NULL;

ALTER TABLE `commands_history` ADD COLUMN `phase` ENUM('wol',
                                                       'pre_menu',
						       'post_menu',
						       'upload',
						       'execute',
						       'delete',
						       'inventory',
						       'reboot',
						       'halt') DEFAULT 'wol' NOT NULL;
						       
	
ALTER TABLE `commands_history` MODIFY `state` ENUM('done',
                                                   'running',
                                                   'failed') DEFAULT NULL;

-- ALTER TABLE `commands_history` MODIFY `state` ENUM('wol_in_progress',
--	                        'wol_done',
--				'wol_failed',
--		        	'pre_menu_in_progress',
--				'pre_menu_done',
--				'pre_menu_failed',
--	 	        	'post_menu_in_progress',
--				'post_menu_done',
--				'post_menu_failed',
--				'upload_in_progress',
--				'upload_done',
--				'upload_failed',
--				'execution_in_progress',
--				'execution_done',
--				'execution_failed',
--				'delete_in_progress',
--				'delete_done',
--				'delete_failed',
--				'inventory_in_progress',
--				'inventory_done',
--				'inventory_failed',
--				'reboot_in_progress',
--				'reboot_done',
--				'reboot_failed',
--				'halt_in_progress',
--				'halt_done',
--				'halt_failed') DEFAULT NULL;


DELETE FROM version;
INSERT INTO version VALUES( "21" );


