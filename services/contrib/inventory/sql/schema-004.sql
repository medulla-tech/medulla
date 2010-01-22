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

ALTER TABLE `Bios` CHANGE `BiosVersion` `BiosVersion` VARCHAR( 255 ) NULL DEFAULT NULL;
ALTER TABLE `Controller` CHANGE `StandardType` `StandardType` VARCHAR( 255 ) NULL DEFAULT NULL;
ALTER TABLE `Network` CHANGE `CardType` `CardType` VARCHAR( 255 ) NULL DEFAULT NULL;
ALTER TABLE `Port` CHANGE `Stamp` `Stamp` VARCHAR( 32 ) NULL DEFAULT NULL;
ALTER TABLE `Storage` CHANGE `StandardType` `StandardType` VARCHAR( 255 ) NULL DEFAULT NULL;

--
-- Database version
--
TRUNCATE Version;
INSERT INTO Version VALUES( '4' );

