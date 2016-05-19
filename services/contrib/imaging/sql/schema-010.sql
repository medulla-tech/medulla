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

-- Update menu items for Davos and PXELINUX
UPDATE BootService SET default_name = 'continue', default_desc = 'Continue Usual Startup', value = 'LOCALBOOT 0' WHERE id = 1;
UPDATE Internationalization SET label = 'continue' WHERE id = 2;
UPDATE BootService SET default_name = 'register', default_desc = 'Register as Pulse client', value = 'COM32 inventory.c32' WHERE id = 2;
UPDATE Internationalization SET label = 'register' WHERE id = 4;
UPDATE BootService SET default_name = 'backup', default_desc = 'Create a Backup', value = 'KERNEL ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL##\nAPPEND ##PULSE2_KERNEL_OPTS## ##PULSE2_REVO_RAW## ##PULSE2_DISKLESS_OPTS## davos_action=SAVE_IMAGE\nINITRD ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##' WHERE id = 3;
UPDATE Internationalization SET label = 'backup' WHERE id = 6;
UPDATE BootService SET default_name = 'diskless', default_desc = 'Diskless Boot', value = 'KERNEL ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL##\nAPPEND ##PULSE2_KERNEL_OPTS## ##PULSE2_DISKLESS_OPTS## davos_debug=1' WHERE id = 4;
UPDATE Internationalization SET label = 'diskless' WHERE id = 8;
UPDATE BootService SET default_name = 'memtest', default_desc = 'Memory Test', value = 'KERNEL ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_MEMTEST##\nAPPEND --type=openbsd' WHERE id = 5;
UPDATE Internationalization SET label = 'memtest' WHERE id = 10;
INSERT INTO Internationalization (id, label, fk_language) VALUES (33, 'hdt', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (34, 'Données Matérielles', 2);
INSERT INTO BootService (default_name, default_desc, fk_name, fk_desc, value) VALUES ('hdt','Hardware Information',33,34,'COM32 hdt.c32');
INSERT INTO Internationalization (id, label, fk_language) VALUES (35, 'reboot', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (36, 'Redémarrer', 2);
INSERT INTO BootService (default_name, default_desc, fk_name, fk_desc, value) VALUES ('reboot','Reboot',35,36,'COM32 reboot.c32');
INSERT INTO Internationalization (id, label, fk_language) VALUES (37, 'poweroff', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (38, 'Eteindre', 2);
INSERT INTO BootService (default_name, default_desc, fk_name, fk_desc, value) VALUES ('poweroff','Power Off',37,38,'COM32 poweroff.c32');

-- Update bootsplash location
UPDATE Menu SET background_uri = '##PULSE2_BOOTSPLASH_FILE##' WHERE id = 1;
UPDATE Menu SET background_uri = '##PULSE2_BOOTSPLASH_FILE##' WHERE id = 2;

UPDATE version set Number = 10;
