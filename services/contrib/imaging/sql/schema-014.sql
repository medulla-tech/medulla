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

SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

-- Create table auto_inc_1000 and auto_inc_10000 to link 1000 or 10000 value to auto_increment
CREATE TABLE auto_inc_1000(id INT NOT NULL, PRIMARY KEY(id));
INSERT INTO auto_inc_1000 VALUE(1000);


-- Set BootService.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
delimiter //
drop trigger if exists BootService_before_insert;
CREATE TRIGGER BootService_before_insert BEFORE INSERT ON BootService
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='BootService';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;

-- Set PostInstallScript.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
delimiter //
drop trigger if exists PostInstallScript_before_insert;
CREATE TRIGGER PostInstallScript_before_insert BEFORE INSERT ON PostInstallScript
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='PostInstallScript';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;

-- Set Menu.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
delimiter //
drop trigger if exists PostInstallScript_before_insert;
CREATE TRIGGER Menu_before_insert BEFORE INSERT ON Menu
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='Menu';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;

-- Set Internationalization.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
delimiter //
drop trigger if exists Internationalization_before_insert;
CREATE TRIGGER Internationalization_before_insert BEFORE INSERT ON Internationalization
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='Internationalization';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;

-- Set MenuItem.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
delimiter //
drop trigger if exists MenuItem_before_insert;
CREATE TRIGGER MenuItem_before_insert BEFORE INSERT ON MenuItem
FOR EACH ROW
BEGIN
declare auto_incr1 BIGINT;
declare auto_incr2 BIGINT;
SELECT AUTO_INCREMENT INTO auto_incr1 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='MenuItem';
SELECT AUTO_INCREMENT INTO auto_incr2 FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='auto_inc_1000';
IF (auto_incr2 > auto_incr1 and NEW.id<auto_incr2) THEN
SET NEW.id = auto_incr2;
END IF;
END;//
delimiter ;


UPDATE version set Number = 14;
