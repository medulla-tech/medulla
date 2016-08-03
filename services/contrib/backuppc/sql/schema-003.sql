--
-- (c) 2016 Siveo, http://siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://siveo.net
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

-- Create table auto_inc_1000 to link 1000 value to auto_increment
CREATE TABLE auto_inc_1000(id INT NOT NULL, PRIMARY KEY(id));
INSERT INTO auto_inc_1000 VALUE(1000);


-- Create trigger to set backuppc.backup_profiles.AUTO_INCREMENT to 1000, even after mysql restart and even if no row upper 1000 exist.
delimiter //
drop trigger if exists backup_profiles_before_insert;
CREATE TRIGGER backup_profiles_before_insert BEFORE INSERT ON backup_profiles
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='backup_profiles';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;

-- Create trigger to set backuppc.period_profiles.AUTO_INCREMENT to 1000, even after mysql restart and even if no row upper 1000 exist.
delimiter //
drop trigger if exists period_profiles_insert;
CREATE TRIGGER period_profiles_before_insert BEFORE INSERT ON period_profiles
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='period_profiles';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;


UPDATE version SET Number = 3;
