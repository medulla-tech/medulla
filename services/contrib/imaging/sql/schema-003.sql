--
-- (c) 2012 Mandriva, http://www.mandriva.com/
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

SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

INSERT INTO Internationalization (id, fk_language, label) VALUES (23, 2, "Effacement de disque sécurisé");
INSERT INTO Internationalization (id, fk_language, label) VALUES (24, 2, "Efface un disque de manière sécurisée en écrivant des nombres pseudoaléatoire");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (6, "Disk Wipe and Data Clearing", "Securely erase disk by overwriting data with pseudorandom numbers", 23, 24, "kernel ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_DBAN## root=/dev/ram0 init=rc nuke=\"dwipe\"");
UPDATE PostInstallScript SET default_name = "Deploy Pulse Agents", default_desc = "Deploy Pulse agents (SSH, OCS, VNC)" WHERE default_name LIKE "Agent Pack";
UPDATE Internationalization SET label = "Déployer les agents Pulse (SSH, OCS, VNC)" WHERE id = 20;

UPDATE version set Number = 3;

