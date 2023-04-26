--
-- (c) 2022 Siveo, http://siveo.net/
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

START TRANSACTION;

-- --------------------------------
-- Updating current BootServices --
-- --------------------------------
-- continue
UPDATE BootService SET value="set url_path http://${next-server}/downloads/davos/
iseq ${product:uristring} OptiPlex%203050 && goto exceptions ||
iseq ${platform} pcbios && sanboot --no-describe --drive 0x80 ||
imgfetch ${url_path}refind.conf
iseq ${buildarch} x86_64 && chain -ar ${url_path}refind_x64.efi ||
iseq ${buildarch} i386 && chain -ar ${url_path}refind_ia32.efi ||
iseq ${buildarch} arm32 && chain -ar ${url_path}refind_aa32.efi ||
iseq ${buildarch} arm64 && chain -ar ${url_path}refind_aa64.efi ||
goto MENU" WHERE default_name = 'continue';
UPDATE version set Number = 23;

COMMIT;
