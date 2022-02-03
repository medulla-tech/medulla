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

-- Add login column to Entity table
ALTER TABLE Entity ADD COLUMN pxe_login VARCHAR(255) NOT NULL DEFAULT "" AFTER uuid;

-- --------------------------------
-- Updating current BootServices --
-- --------------------------------
-- continue
-- continue action is special, because it is used both in protected menu and normal menu
-- if the login failed, load ${loaded-menu}. If MENU is always loaded, the password is not checked and we have access to the main menu
UPDATE BootService SET value="set url_path http://${next-server}/downloads/davos/
iseq ${platform} pcbios && sanboot --no-describe --drive 0x80 ||
imgfetch ${next-server}/downloads/davos/refind.conf
iseq ${buildarch} x86_64 && chain -ar ${url_path}refind_x64.efi ||
iseq ${buildarch} i386 && chain -ar ${url_path}refind_ia32.efi ||
iseq ${buildarch} arm32 && chain -ar ${url_path}refind_aa32.efi ||
iseq ${buildarch} arm64 && chain -ar ${url_path}refind_aa64.efi ||
goto MENU" WHERE default_name = 'continue';

-- register
UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_DISKLESS_DIR##/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_action=REGISTER  dump_path=##PULSE2_INVENTORIES_DIR## timereboot=##PULSE2_PXE_TIME_REBOOT## initrd=##PULSE2_DISKLESS_INITRD##
kernel ${url_path}##PULSE2_DISKLESS_KERNEL## ${kernel_args}
initrd ${url_path}initrd.img
boot || goto MENU" WHERE default_name = 'register';
-- reboot
UPDATE BootService SET value="reboot || goto MENU" WHERE default_name = 'reboot';

-- poweroff
UPDATE BootService SET value="poweroff || goto MENU" WHERE default_name = 'poweroff';

-- backup
UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_DISKLESS_DIR##/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_action=SAVE_IMAGE mac=##MACADDRESS##  timereboot=2 initrd=initrd.img
kernel ${url_path}vmlinuz ${kernel_args}
initrd ${url_path}initrd.img
boot || goto MENU" WHERE default_name = 'backup';

-- gparted
UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_TOOLS_DIR##/gparted/
kernel ${url_path}vmlinuz boot=live config components union=overlay username=user noswap noeject ip= vga=788 fetch=${url_path}filesystem.squashfs
initrd ${url_path}initrd.img
boot || goto MENU" WHERE default_name = 'gparted';

-- diskless
UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_TOOLS_DIR##/avg/
kernel ${url_path}vmlinuz max_loop=255 vga=791 video=vesafb init=linuxrc
initrd ${url_path}initrd.lzm
boot || goto MENU" WHERE default_name = 'avg';

UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_DISKLESS_DIR##/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_debug=i timereboot=##PULSE2_PXE_TIME_REBOOT## initrd=##PULSE2_DISKLESS_INITRD##
kernel ${url_path}##PULSE2_DISKLESS_KERNEL## ${kernel_args}
initrd ${url_path}##PULSE2_DISKLESS_INITRD## " WHERE default_name = 'diskless';

UPDATE version set Number = 22;

COMMIT;
