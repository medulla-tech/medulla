--
-- (c) 2017 Siveo, http://www.siveo.net/
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

START TRANSACTION;

-- ----------------------------------------------------------------------
-- Database vADD CULUMN TABLE has_login_command
-- MANAGE
--        DYNAMIC PARAMETERS FOR PACKAGE

--          after transferring files to the machine
--          to control the instantiation of the launch of the install scripts of the packages,
--          there are 3 posibilitees
--              - no control.
--              - be checked according to datetime
--              - or control of the number of deployments already launched

-- ----------------------------------------------------------------------

ALTER TABLE `xmppmaster`.`has_login_command`
ADD COLUMN `start_exec_on_time` DATETIME NULL AFTER `command`,
ADD COLUMN `grpid` INT(11) NULL AFTER `start_exec_on_time`,
ADD COLUMN `nb_machine_for_deploy` INT(11) NULL AFTER `grpid`,
ADD COLUMN `start_exec_on_nb_deploy` INT(11) NULL AFTER `nb_machine_for_deploy`,
ADD COLUMN `count_deploy_progress` INT(11) NULL AFTER `start_exec_on_nb_deploy`,
ADD COLUMN `parameters_deploy` TEXT NULL AFTER `count_deploy_progress`;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 7;

COMMIT;
