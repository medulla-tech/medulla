--
-- (c) 2021 Siveo, http://www.siveo.net/
--
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

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------
-- ----------------------------------------------------------------------
-- ADD COLUMNS md5agentversion AND version table uptime_machine
-- ADD INDEX ON COLUMNS  md5agentversion AND version and date
-- ----------------------------------------------------------------------

START TRANSACTION;

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;

ALTER TABLE `xmppmaster`.`uptime_machine`
ADD COLUMN `timetempunix` int(11) DEFAULT NULL AFTER `date`,
ADD COLUMN `md5agentversion` VARCHAR(32) NULL AFTER `timetempunix`,
ADD COLUMN `version` VARCHAR(10) NULL AFTER `md5agentversion`,
ADD INDEX `ind_md5agent` (`md5agentversion` ASC) ,
ADD INDEX `ind_agenntversion` (`version` ASC) ,
ADD INDEX `ind_date` (`date` ASC),
ADD INDEX `ind_time_unix` (`timetempunix` ASC);


DROP TRIGGER IF EXISTS `xmppmaster`.`uptime_machine_BEFORE_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`uptime_machine_BEFORE_INSERT` BEFORE INSERT ON `uptime_machine` FOR EACH ROW
BEGIN
IF new.timetempunix IS NULL then SET new.timetempunix =  UNIX_TIMESTAMP(new.date);END IF;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- PURGE uptime_machine OLD RECORD  Weeks
-- ----------------------------------------------------------------------
CREATE EVENT IF NOT EXISTS purgeuptimemachine
  ON SCHEDULE
  AT
  (CURRENT_TIMESTAMP + INTERVAL 1 DAY) ON COMPLETION PRESERVE ENABLE
  DO
    DELETE FROM xmppmaster.uptime_machine
    WHERE
        date < DATE_SUB(NOW(), INTERVAL 4 WEEK);

SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 68;

COMMIT;
