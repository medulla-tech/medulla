--
-- (c) 2024 Siveo, http://siveo.net/
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


START TRANSACTION;

create table if not exists Multicast(
    id int not null auto_increment, primary key(id),
    location varchar(255),
    target_uuid varchar(50) not null,
    image_uuid varchar(255) not null,
    image_name varchar(255) not null
);

ALTER TABLE ImagingServer add diskless_dir varchar(255) not null default "davos";
ALTER TABLE ImagingServer add diskless_kernel varchar(255) not null default "vmlinuz";
ALTER TABLE ImagingServer add inventories_dir varchar(255) not null default "inventories";
ALTER TABLE ImagingServer add pxe_time_reboot int not null default 2;
ALTER TABLE ImagingServer add diskless_initrd varchar(255) not null default "initrd.img";
ALTER TABLE ImagingServer add tools_dir varchar(255) not null default "tools";
ALTER TABLE ImagingServer add davos_opts varchar(255) not null default "nfs_server= nfs_share_masters= nfs_share_postinst=";

-- Update register BootService
UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_DISKLESS_DIR##/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_action=REGISTER ##PULSE2_DAVOS_OPTS## dump_path=##PULSE2_INVENTORIES_DIR## timereboot=##PULSE2_PXE_TIME_REBOOT## initrd=##PULSE2_DISKLESS_INITRD##
kernel ${url_path}##PULSE2_DISKLESS_KERNEL## ${kernel_args}
initrd ${url_path}initrd.img
boot || goto MENU" WHERE default_name = 'register';


-- Update backup BootService
UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_DISKLESS_DIR##/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_action=SAVE_IMAGE ##PULSE2_DAVOS_OPTS## mac=##MACADDRESS##  timereboot=2 initrd=initrd.img
kernel ${url_path}vmlinuz ${kernel_args}
initrd ${url_path}initrd.img
boot || goto MENU" WHERE default_name = 'backup';

-- Update diskless BootService
UPDATE BootService SET value="set url_path http://${next-server}/downloads/##PULSE2_DISKLESS_DIR##/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_debug=i ##PULSE2_DAVOS_OPTS## timereboot=##PULSE2_PXE_TIME_REBOOT## initrd=##PULSE2_DISKLESS_INITRD##
kernel ${url_path}##PULSE2_DISKLESS_KERNEL## ${kernel_args}
initrd ${url_path}##PULSE2_DISKLESS_INITRD## " WHERE default_name = 'diskless';

UPDATE version set Number = 26;
COMMIT;
