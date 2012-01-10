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

CREATE TABLE IF NOT EXISTS commands (
    id_command INT NOT NULL AUTO_INCREMENT,

    date_created DATETIME,
    start_file TINYTEXT NULL DEFAULT "",
    parameters TEXT NULL DEFAULT "",
    path_destination TEXT NULL DEFAULT "",
    path_source TEXT NULL DEFAULT "",
    create_directory ENUM("enable", "disable") DEFAULT "enable",
    start_script ENUM("enable", "disable") DEFAULT "enable",
    delete_file_after_execute_successful ENUM("enable", "disable") DEFAULT "enable",
    files MEDIUMTEXT NULL DEFAULT "",
    start_date DATETIME NULL,
    end_date DATETIME NULL,
    target TINYTEXT NULL DEFAULT "",
    username VARCHAR(255) NULL DEFAULT "",
    dispatched ENUM("YES", "NO") DEFAULT "NO",
    title VARCHAR(255) NULL DEFAULT "",
    start_inventory ENUM("enable", "disable") DEFAULT "disable",
    wake_on_lan ENUM("enable", "disable") DEFAULT "disable",
    next_connection_delay INT DEFAULT 60,
    max_connection_attempt INT DEFAULT 3,
    PRIMARY KEY (id_command)
) ENGINE=MYISAM;

CREATE TABLE IF NOT EXISTS commands_on_host (
    id_command_on_host INT NOT NULL AUTO_INCREMENT,
    id_command INT NOT NULL,

    host TINYTEXT NULL DEFAULT "",
    start_date DATETIME NULL,
    end_date DATETIME NULL,
    current_state ENUM(
        "upload_in_progress",
        "upload_done",
        "upload_failed",
        "execution_in_progress",
        "execution_done",
        "execution_failed",
        "delete_in_progress",
        "delete_done",
        "delete_failed",
        "inventory_in_progress",
        "inventory_failed",
        "inventory_done",
        "not_reachable",
        "done",
        "pause",
        "stop",
        "scheduled"
    ),
    uploaded ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS"),
    executed ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS"),
    deleted ENUM("TODO", "IGNORED", "DONE", "FAILED", "WORK_IN_PROGRESS"),
    next_launch_date DATETIME NULL,
    current_pid INT DEFAULT 0,
    number_attempt_connection_remains INT DEFAULT 0,
    next_attempt_date_time BIGINT DEFAULT 0,

    PRIMARY KEY (id_command_on_host),
    KEY (id_command)
) ENGINE=MYISAM;

CREATE TABLE IF NOT EXISTS commands_history (
    id_command_history INT NOT NULL AUTO_INCREMENT,
    id_command_on_host INT NOT NULL,

    date TINYTEXT NULL DEFAULT "",
    stderr LONGTEXT NULL DEFAULT "",
    stdout LONGTEXT NULL DEFAULT "",
    state ENUM(
        "upload_in_progress",
        "upload_done",
        "upload_failed",
        "execution_in_progress",
        "execution_done",
        "execution_failed",
        "delete_in_progress",
        "delete_done",
        "delete_failed",
        "inventory_in_progress",
        "inventory_failed",
        "inventory_done",
        "not_reachable",
        "done",
        "pause",
        "stop",
        "scheduled"
    ),

    PRIMARY KEY (id_command_history),
    KEY (id_command_on_host)
) ENGINE=MYISAM;



--
-- Database version
--

CREATE TABLE version (
  Number tinyint(4) unsigned NOT NULL default '0'
) ENGINE=MYISAM;

INSERT INTO version VALUES( '1' );
