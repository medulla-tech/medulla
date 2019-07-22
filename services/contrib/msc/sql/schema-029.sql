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


-- check exist index before creation
DELIMITER //
DROP PROCEDURE IF EXISTS createindexidx_star_date;
create procedure createindexidx_star_date()
begin
IF (SELECT 1
    FROM `INFORMATION_SCHEMA`.`STATISTICS`
    WHERE `TABLE_SCHEMA` = 'msc' 
    AND `TABLE_NAME` = 'commands_on_host'
    AND `INDEX_NAME` = 'idx_star_date') IS NULL THEN
    ALTER TABLE `msc`.`commands_on_host` ADD INDEX `idx_star_date` (`start_date` ASC);
END IF;
END;
//
DELIMITER ;

DELIMITER //
DROP PROCEDURE IF EXISTS createindexidx_end_date;
create procedure createindexidx_end_date()
begin
IF (SELECT 1
    FROM `INFORMATION_SCHEMA`.`STATISTICS`
    WHERE `TABLE_SCHEMA` = 'msc' 
    AND `TABLE_NAME` = 'commands_on_host'
    AND `INDEX_NAME` = 'idx_end_date') IS NULL THEN
    ALTER TABLE `msc`.`commands_on_host` ADD INDEX `idx_end_date` (`end_date` ASC);
END IF;
END;
//
DELIMITER ;

call createindexidx_star_date();
call createindexidx_end_date();

UPDATE version SET Number = 29;
