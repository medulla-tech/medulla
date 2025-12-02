--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/.>

use imaging;
SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

START TRANSACTION;

-- Delete post install scripts which are no longer compatible with Pulse
DELETE FROM PostInstallScript WHERE id IN (4, 10, 11, 12, 13, 14, 15, 16, 17, 18);

-- Create the new post install scripts for Windows 10 and Windows 11
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (19, "Medulla Windows 10 OEM", "Medulla Windows 10 OEM postinstall script example",  1, 01, "MountSystem\n\nCopySysprep windows10oem.xml\n\nCopyRunAtOnce\n\nCopyAgent\n\nCopyDrivers Windows10\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (20, "Medulla Windows 11 OEM", "Medulla Windows 11 OEM postinstall script example",  1, 01, "MountSystem\n\nCopySysprep windows11oem.xml\n\nCopyRunAtOnce\n\nCopyAgent\n\nCopyDrivers Windows11\n");


UPDATE version set Number = 29;
COMMIT;
