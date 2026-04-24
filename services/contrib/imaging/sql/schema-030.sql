--
--  (c) 2024-2026 Medulla, http://www.medulla-tech.io
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

-- Update the post install script for Windows 11 to include partition extension script
UPDATE PostInstallScript SET value = "MountSystem\n\nCopySysprep windows11oem.xml\n\nCopyRunAtOnce\n\nCopyRunAtOnce ExtendOSPartition.ps1\n\nCopyAgent\n\nCopyDrivers Windows11\n" WHERE id = 20;


UPDATE version set Number = 30;
COMMIT;
