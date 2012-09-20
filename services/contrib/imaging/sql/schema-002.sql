--
-- (c) 2010 Mandriva, http://www.mandriva.com/
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

SET storage_engine=INNODB;
SET GLOBAL character_set_server=UTF8;
SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

DELETE FROM PostInstallScript WHERE default_name LIKE "NTFS Resize";
UPDATE PostInstallScript SET default_name = "First" WHERE default_name LIKE "Partition extension";
UPDATE PostInstallScript SET value = "MountSystem\n\ndate | unix2dos >> /mnt/date.txt\n" WHERE default_name LIKE "Date";
UPDATE PostInstallScript SET value = "MountSystem\nCopySysprepInf /revoinfo/sysprep.inf\n" WHERE default_name LIKE "Sysprep";
UPDATE PostInstallScript SET value = "MountSystem\nChangeSIDAndName" WHERE default_name LIKE "SID";
UPDATE PostInstallScript SET value = "DeployAgents" WHERE default_name = "Agent Pack";
UPDATE PostInstallScript SET default_desc = "The first partition will be extend across the whole disk." WHERE default_name LIKE "First";
UPDATE Internationalization SET label = "La première partition sera étendue à l'intégralité du disque dur" WHERE id = 18;
DELETE FROM Internationalization WHERE id = 19;

UPDATE version set Number = 2;
