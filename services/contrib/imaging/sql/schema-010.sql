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
UPDATE Internationalization SET label = 'Continuer le démarrage normalement' WHERE id = 3 AND fk_language = 2;
UPDATE Internationalization SET label = 'Iniciar normalmente' WHERE id = 3 AND fk_language = 3;
UPDATE Internationalization SET label = 'Gewohnten Start fortsetzen' WHERE id = 3 AND fk_language = 4;
UPDATE BootService SET default_name = 'register', default_desc = 'Register as Pulse client', value = 'COM32 inventory.c32\nAPPEND dump_path=##PULSE2_INVENTORIES_DIR##' WHERE id = 2;
UPDATE Internationalization SET label = 'register' WHERE id = 4;
UPDATE Internationalization SET label = 'Ajouter comme client Pulse' WHERE id = 5 AND fk_language = 2;
UPDATE Internationalization SET label = 'Registrar Cliente Pulse' WHERE id = 5 AND fk_language = 3;
UPDATE Internationalization SET label = 'Als Pulse-Client registrieren' WHERE id = 5 AND fk_language = 4;
UPDATE BootService SET default_name = 'backup', default_desc = 'Create a Backup', value = 'KERNEL ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL##\nAPPEND ##PULSE2_KERNEL_OPTS## ##PULSE2_REVO_RAW## ##PULSE2_DISKLESS_OPTS## davos_action=SAVE_IMAGE\nINITRD ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##' WHERE id = 3;
UPDATE Internationalization SET label = 'backup' WHERE id = 6;
UPDATE Internationalization SET label = 'Créer une image' WHERE id = 7 AND fk_language = 2;
UPDATE Internationalization SET label = 'Criar um Backup' WHERE id = 7 AND fk_language = 3;
UPDATE Internationalization SET label = 'Sicherung erstellen' WHERE id = 7 AND fk_language = 4;
UPDATE BootService SET default_name = 'diskless', default_desc = 'Diskless Boot', value = 'KERNEL ../##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL##\nAPPEND ##PULSE2_KERNEL_OPTS## ##PULSE2_DISKLESS_OPTS## davos_debug=1' WHERE id = 4;
UPDATE Internationalization SET label = 'diskless' WHERE id = 8;
UPDATE Internationalization SET label = 'Démarrage sans disque' WHERE id = 9 AND fk_language = 2;
UPDATE Internationalization SET label = 'Iniciar sem disco' WHERE id = 9 AND fk_language = 3;
UPDATE Internationalization SET label = 'Plattenloses Booten' WHERE id = 9 AND fk_language = 4;
UPDATE BootService SET default_name = 'memtest', default_desc = 'Memory Test', value = 'KERNEL ../##PULSE2_TOOLS_DIR##/memtest/memtest\nAPPEND --type=openbsd' WHERE id = 5;
UPDATE Internationalization SET label = 'memtest' WHERE id = 10;
UPDATE Internationalization SET label = 'Test mémoire' WHERE id = 11 AND fk_language = 2;
UPDATE Internationalization SET label = 'Teste de Memória' WHERE id = 11 AND fk_language = 3;
UPDATE Internationalization SET label = 'Speichertest' WHERE id = 11 AND fk_language = 4;
UPDATE BootService SET default_name = 'dban', default_desc = 'Shred Hard Drive', value = 'KERNEL ../##PULSE2_TOOLS_DIR##/dban/dban.bzi\nAPPEND nuke="dban"' WHERE id = 6;
UPDATE Internationalization SET label = 'dban' WHERE id = 23;
UPDATE Internationalization SET label = 'Effacement de disque sécurisé' WHERE id = 24 AND fk_language = 2;
UPDATE Internationalization SET label = 'Limpeza de disco e dados' WHERE id = 24 AND fk_language = 3;
UPDATE Internationalization SET label = 'Platten und Daten löschen' WHERE id = 24 AND fk_language = 4;
INSERT INTO Internationalization (id, label, fk_language) VALUES (33, 'hdt', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (34, 'Données Matérielles', 2);
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (7, 'hdt','Hardware Information',33,34,'COM32 hdt.c32');
INSERT INTO Internationalization (id, label, fk_language) VALUES (35, 'reboot', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (36, 'Redémarrer', 2);
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (8, 'reboot','Reboot',35,36,'COM32 reboot.c32');
INSERT INTO Internationalization (id, label, fk_language) VALUES (37, 'poweroff', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (38, 'Eteindre', 2);
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (9, 'poweroff','Power Off',37,38,'COM32 poweroff.c32');
INSERT INTO Internationalization (id, label, fk_language) VALUES (39, 'gparted', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (40, 'Editeur de partitions GParted', 2);
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (10, 'gparted','GParted Partition Editor',39,40,'KERNEL ../##PULSE2_TOOLS_DIR##/gparted/vmlinuz\nINITRD ../##PULSE2_TOOLS_DIR##/gparted/initrd.img\nAPPEND boot=live config components union=overlay username=user noswap noeject ip= vga=788 fetch=tftp://##PULSE2_PUBLIC_IP##/##PULSE2_TOOLS_DIR##/gparted/filesystem.squashfs');
INSERT INTO Internationalization (id, label, fk_language) VALUES (41, 'avg', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (42, 'Antivirus AVG', 2);
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (11, 'avg','AVG Antivirus',41,42,'KERNEL ../##PULSE2_TOOLS_DIR##/avg/vmlinuz\nINITRD ../##PULSE2_TOOLS_DIR##/avg/initrd.lzm\nAPPEND max_loop=255 vga=791  video=vesafb init=linuxrc reboot=bios');
INSERT INTO Internationalization (id, label, fk_language) VALUES (43, 'pulse_utilities', 2);
INSERT INTO Internationalization (id, label, fk_language) VALUES (44, 'Utilitaires', 2);
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (12, 'pulse_utilities','Pulse Utilities',43,44,'KERNEL vesamenu.c32\nAPPEND ../##PULSE2_TOOLS_DIR##/utilitaires.menu');
INSERT INTO MenuItem VALUES (5,2,0,0,2);
INSERT INTO BootServiceInMenu VALUES (5,12);

-- Update bootsplash location
UPDATE Menu SET background_uri = '##PULSE2_BOOTSPLASH_FILE##' WHERE id = 1;
UPDATE Menu SET background_uri = '##PULSE2_BOOTSPLASH_FILE##' WHERE id = 2;

UPDATE version set Number = 10;
