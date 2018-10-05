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

-- Delete post install scripts which are no longer compatible with Pulse
DELETE FROM PostInstallScript WHERE id IN (1, 2, 5, 6, 8);

-- Insert the new post install scripts
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (10, "MountSystem",           "Mount folders needed by post install scripts",  1, 01, "MountSystem\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (11, "Check MountSystem",     "Show mounted folders",  1, 01, "df -h |grep pulse2\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (12, "DebugImaging",          "Debug imaging",  1, 01, "MountSystem\n\nmkdir -p /imaging_server/masters/debug_imaging/`hostname`\ncp /var/log/clonezilla.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-clonezilla.log\ncp /var/log/partclone.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-partclone.log\ncp /mnt/[[:alpha:]]indows/[[:alpha:]]anther/unattend.xml /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-unattend.xml\ncp /mnt/[[:alpha:]]indows/[[:alpha:]]anther/[[:alpha:]]etuperr.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-setuperr.log\ncp /mnt/[[:alpha:]]indows/[[:alpha:]]anther/[[:alpha:]]etupact.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-setupact.log\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (13, "Copy agent",            "Copy Pulse agent",  1, 01, "mkdir -p /mnt/Windows/Setup/Scripts\necho 'Setup scripts folder : ' $?\n\ncp /opt/winutils/Pulse-Agent-windows-FULL-latest.exe /mnt/Windows/Setup/Scripts\necho 'Agent Pulse : ' $?\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (14, "Copy setup complete",   "Copy setupcomplete.cmd",  1, 01, "mkdir -p /mnt/Windows/Setup/Scripts\necho 'Setup scripts folder : ' $?\n\ncp /opt/sysprep/SetupComplete.cmd /mnt/Windows/Setup/Scripts\necho 'setupcomplete.cmd copy : ' $?\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (15, "Create folder",         "Create a folder",  1, 01, "mkdir -p /mnt/Windows/Setup/Scripts\necho 'Setup scripts folder : ' $?\n\nmkdir -p /mnt/Windows/INF/driverpack\necho 'INF folder : ' $?\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (16, "Copy drivers",          "Copy device drivers",  1, 01, "mkdir -p /mnt/Windows/INF/driverpack\necho 'INF folder : ' $?\n\n/opt/sysprep/driverscopy Windows10\necho 'Copy device drivers : ' $?\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (17, "Copy sysprep",          "Copy sysprep answer file",  1, 01, "tail -n1 /etc/mtab\n\nCopySysprepInf /opt/sysprep/yoursysprep.xml\n\nls /mnt/Windows/Panther/u*\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (18, "Postinstall",           "SIVEO postinstall script with debug",  1, 01, "MountSystem\n\nCopySysprepInf /opt/sysprep/yoursysprep.xml\n\nmkdir -p /mnt/Windows/Setup/Scripts\nmkdir -p /mnt/Windows/INF/driverpack\n\ncp /opt/sysprep/SetupComplete.cmd /mnt/Windows/Setup/Scripts\ncp /opt/winutils/Pulse-Agent-windows-FULL-latest.exe /mnt/Windows/Setup/Scripts\n\n/opt/sysprep/driverscopy Windows10\n\nmkdir -p /imaging_server/masters/debug_imaging/`hostname`\ncp /var/log/clonezilla.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-clonezilla.log\ncp /var/log/partclone.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-partclone.log\ncp /mnt/[[:alpha:]]indows/[[:alpha:]]anther/unattend.xml /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-unattend.xml\ncp /mnt/[[:alpha:]]indows/[[:alpha:]]anther/[[:alpha:]]etuperr.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-setuperr.log\ncp /mnt/[[:alpha:]]indows/[[:alpha:]]anther/[[:alpha:]]etupact.log /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-setupact.log\n\nls /mnt/Windows/Panther/ > /imaging_server/masters/debug_imaging/`hostname`/`date '+%Y-%m-%d-%H:%M:%S'`-direct-panther\n");


UPDATE version set Number = 21;

COMMIT;
