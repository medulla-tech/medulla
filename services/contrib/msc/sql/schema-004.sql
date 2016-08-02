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

CREATE TABLE target (
    id INT NOT NULL AUTO_INCREMENT,
    id_command INT NOT NULL ,
    id_command_on_host INT,
    target_name TEXT NOT NULL,
    mirrors TEXT,
    id_group TEXT,
    scheduler TEXT,
    INDEX cmd_ind (id_command),
    FOREIGN KEY (id_command) REFERENCES commands(id_command),
    INDEX coh_ind (id_command_on_host),
    FOREIGN KEY (id_command_on_host) REFERENCES commands_on_host(id_command_on_host),
    PRIMARY KEY (id)
) ENGINE=MYISAM;
INSERT INTO target (id_command, target_name) SELECT id_command, target FROM commands;

ALTER TABLE commands \
    DROP COLUMN target;
ALTER TABLE commands \
    ADD COLUMN scheduler VARCHAR(255) DEFAULT NULL;
ALTER TABLE commands \
    ADD COLUMN pre_command_hook TINYTEXT DEFAULT NULL;
ALTER TABLE commands \
    ADD COLUMN post_command_hook TINYTEXT DEFAULT NULL;
ALTER TABLE commands \
    ADD COLUMN pre_run_hook TINYTEXT DEFAULT NULL;
ALTER TABLE commands \
    ADD COLUMN post_run_hook TINYTEXT DEFAULT NULL;
ALTER TABLE commands \
    ADD COLUMN on_success_hook TINYTEXT DEFAULT NULL;
ALTER TABLE commands \
    ADD COLUMN on_failure_hook TINYTEXT DEFAULT NULL;

ALTER TABLE commands_history \
    ADD COLUMN error_code INT(11) DEFAULT 0;
ALTER TABLE commands_history \
    CHANGE COLUMN state state ENUM('upload_in_progress','upload_done','upload_failed','execution_in_progress','execution_done','execution_failed','delete_in_progress','delete_done','delete_failed','inventory_in_progress','inventory_failed','inventory_done','not_reachable','done','pause','stop','scheduled', 'failed') DEFAULT NULL;

ALTER TABLE commands_on_host \
    ADD COLUMN current_launcher VARCHAR(255) DEFAULT NULL;
ALTER TABLE commands_on_host \
    CHANGE COLUMN current_state current_state ENUM('upload_in_progress','upload_done','upload_failed','execution_in_progress','execution_done','execution_failed','delete_in_progress','delete_done','delete_failed','inventory_in_progress','inventory_failed','inventory_done','not_reachable','done','pause','stop','scheduled', 'failed') DEFAULT NULL;

DELETE FROM version;
INSERT INTO version VALUES( '4' );

