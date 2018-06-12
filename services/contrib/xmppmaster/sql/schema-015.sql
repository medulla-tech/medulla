--
-- (c) 2018 Siveo, http://www.siveo.net/
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

-- Create table auto_inc_1000 and auto_inc_10000 to link 1000 or 10000 value to auto_increment
CREATE TABLE auto_inc_1000(id INT NOT NULL, PRIMARY KEY(id));
INSERT INTO auto_inc_1000 VALUE(1000);


-- Set qa_custom_command.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
delimiter //
drop trigger if exists qa_custom_command_before_insert;
CREATE TRIGGER qa_custom_command_before_insert BEFORE INSERT ON qa_custom_command
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='qa_custom_command';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;

UPDATE version SET Number = 15;

COMMIT;
