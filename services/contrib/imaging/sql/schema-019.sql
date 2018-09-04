--
-- (c) 2018 Siveo, http://siveo.net/
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

use imaging;

START TRANSACTION;

-- Set BootService.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
delimiter //
drop trigger if exists BootService_before_insert;
CREATE TRIGGER BootService_before_insert BEFORE INSERT ON BootService
FOR EACH ROW
BEGIN
set @auto_incr1= (SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='BootService');
set @auto_incr2 = (SELECT id from auto_inc_1000);

IF (@auto_incr2 > @auto_incr1) THEN
SET NEW.id = @auto_incr2;
END IF;
END;//


-- Set PostInstallScript.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
drop trigger if exists PostInstallScript_before_insert;
CREATE TRIGGER PostInstallScript_before_insert BEFORE INSERT ON PostInstallScript
FOR EACH ROW
BEGIN
set @auto_incr1 = (SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='PostInstallScript');
set @auto_incr2 = (SELECT id from auto_inc_1000);

IF (@auto_incr2 > @auto_incr1) THEN
SET NEW.id = @auto_incr2;
END IF;
END;//

-- Set Menu.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
drop trigger if exists Menu_before_insert;
CREATE TRIGGER Menu_before_insert BEFORE INSERT ON Menu
FOR EACH ROW
BEGIN
set @auto_incr1 =(SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='Menu');
set @auto_incr2 =(SELECT id from auto_inc_1000);

IF (@auto_incr2 > @auto_incr1) THEN
SET NEW.id = @auto_incr2;
END IF;
END;//

-- Set Internationalization.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
drop trigger if exists Internationalization_before_insert;
CREATE TRIGGER Internationalization_before_insert BEFORE INSERT ON Internationalization
FOR EACH ROW
BEGIN
set @auto_incr1 = (SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='Internationalization');
set @auto_incr2 = (SELECT id from auto_inc_1000);

IF (@auto_incr2 > @auto_incr1) THEN
SET NEW.id = @auto_incr2;
END IF;
END;//

-- Set MenuItem.AUTO_INCREMENT to 1000 if calculated auto_increment is under this value.
drop trigger if exists MenuItem_before_insert;
CREATE TRIGGER MenuItem_before_insert BEFORE INSERT ON MenuItem
FOR EACH ROW
BEGIN
set @auto_incr1 = (SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE table_schema=DATABASE() AND table_name='MenuItem');
set @auto_incr2 = (SELECT id from auto_inc_1000);

IF (@auto_incr2 > @auto_incr1) THEN
SET NEW.id = @auto_incr2;
END IF;
END;//
delimiter ;


UPDATE version set Number = 19;

COMMIT;
