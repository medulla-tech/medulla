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

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

SET storage_engine=INNODB;
SET GLOBAL character_set_server=UTF8;
SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';


START TRANSACTION;

CREATE TABLE version (
  Number tinyint(4) unsigned NOT NULL default '0'
);

INSERT INTO version VALUES( '1' );

-- nomenclatures tables
-- TargetType
CREATE TABLE TargetType (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
);

-- ImagingLogState
CREATE TABLE ImagingLogState (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
);

-- ImagingLogLevel
CREATE TABLE ImagingLogLevel (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
);

-- Protocol
CREATE TABLE Protocol (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
);

-- Language
CREATE TABLE Language (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
);

-- SynchroState
CREATE TABLE SynchroState (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
);

-- end of the nomenclatures tables

-- BootService
CREATE TABLE BootService (
  id INT NOT NULL AUTO_INCREMENT,
  default_name Text NOT NULL,
  default_desc Text NOT NULL,
  fk_name INT,
  fk_desc INT,
  value Text NOT NULL,
  PRIMARY KEY (id)
) AUTO_INCREMENT=1000;

-- User
CREATE TABLE `User` (
  id INT NOT NULL AUTO_INCREMENT,
  login Text NOT NULL,
  PRIMARY KEY (id)
);

-- PostInstallScript
CREATE TABLE PostInstallScript (
  id INT NOT NULL AUTO_INCREMENT,
  default_name Text NOT NULL,
  default_desc Text NOT NULL,
  fk_name INT,
  fk_desc INT,
  value Text NOT NULL,
  PRIMARY KEY (id)
) AUTO_INCREMENT=1000;

-- Entity
CREATE TABLE Entity (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  uuid Text NOT NULL,
  PRIMARY KEY (id)
);

-- Target
CREATE TABLE Target (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  uuid Text NOT NULL,
  kernel_parameters Text,
  image_parameters Text,
  exclude_parameters Text,
  raw_mode TINYINT(1) NOT NULL DEFAULT 0,
  `type` INT NOT NULL,
  is_registered_in_package_server TINYINT(1) NOT NULL DEFAULT 0,
  fk_entity INT NOT NULL,
  fk_menu INT NOT NULL,
  PRIMARY KEY (id)
);

-- List the disks of a target
CREATE TABLE ComputerDisk (
  id INT NOT NULL AUTO_INCREMENT,
  num BIGINT DEFAULT '-1',
  cyl BIGINT DEFAULT '0',
  head BIGINT DEFAULT '0',
  sector BIGINT DEFAULT '0',
  capacity BIGINT DEFAULT '0',
  fk_target INT NOT NULL,
  PRIMARY KEY (id)
);

-- List the partitions of a disk of a target
CREATE TABLE ComputerPartition (
  id INT NOT NULL AUTO_INCREMENT,
  num INT DEFAULT '-1',
  type varchar(32) DEFAULT NULL,
  length BIGINT DEFAULT '0',
  start BIGINT DEFAULT '0',
  fk_disk INT NOT NULL,
  PRIMARY KEY (id)
);

-- ImagingServer
CREATE TABLE ImagingServer (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  url Text NOT NULL,
  fk_default_menu INT NOT NULL,
  packageserver_uuid Text NOT NULL,
  recursive Bool NOT NULL DEFAULT 1,
  associated Bool NOT NULL DEFAULT 0,
  fk_language INT NOT NULL DEFAULT 1,
  fk_entity INT NOT NULL,
  PRIMARY KEY (id)
);

-- Menu
CREATE TABLE Menu (
  id INT NOT NULL AUTO_INCREMENT,
  default_name Text NOT NULL,
  fk_name INT,
  timeout INT,
  mtftp_restore_timeout INT NOT NULL DEFAULT 0,
  background_uri Text DEFAULT '',
  message Text NOT NULL DEFAULT '',
  ethercard INT NOT NULL DEFAULT 0,
  bootcli TINYINT(1) NOT NULL DEFAULT 0,
  disklesscli TINYINT(1) NOT NULL DEFAULT 0,
  dont_check_disk_size TINYINT(1) NOT NULL DEFAULT 0,
  hidden_menu TINYINT(1) NOT NULL DEFAULT 0,
  debug TINYINT(1) NOT NULL DEFAULT 0,
  update_nt_boot TINYINT(1) NOT NULL DEFAULT 0,
  fk_default_item INT,
  fk_default_item_WOL INT,
  fk_protocol INT DEFAULT 1,
  fk_synchrostate INT NOT NULL DEFAULT 1,
  PRIMARY KEY (id)
) AUTO_INCREMENT = 1000;

-- PostInstallScriptOnImagingServer
CREATE TABLE PostInstallScriptOnImagingServer (
  fk_post_install_script INT NOT NULL,
  fk_imaging_server INT NOT NULL
);

-- BootServiceOnImagingServer
CREATE TABLE BootServiceOnImagingServer (
  fk_boot_service INT NOT NULL,
  fk_imaging_server INT NOT NULL
);

-- ImageOnImagingServer
CREATE TABLE ImageOnImagingServer (
  fk_image INT NOT NULL,
  fk_imaging_server INT NOT NULL
);

-- Partition
CREATE TABLE Partition (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  filesystem Text NOT NULL,
  size_sect BIGINT NOT NULL,
  start_sect BIGINT NOT NULL,
  fk_image INT NOT NULL,
  PRIMARY KEY (id)
);

-- Internationalization
CREATE TABLE Internationalization (
  id INT NOT NULL,
  label Text NOT NULL,
  fk_language INT NOT NULL
) AUTO_INCREMENT=10000;

-- MenuItem
CREATE TABLE MenuItem (
  id INT NOT NULL AUTO_INCREMENT,
  `order` INT NOT NULL,
  hidden Bool DEFAULT 1,
  hidden_WOL Bool DEFAULT 1,
  fk_menu INT NOT NULL,
  PRIMARY KEY (id)
) AUTO_INCREMENT=1000;

-- ImageInMenu
CREATE TABLE ImageInMenu (
  fk_image INT NOT NULL,
  fk_menuitem INT NOT NULL
);

-- Image
CREATE TABLE Image (
  id INT NOT NULL AUTO_INCREMENT,
  path Text NOT NULL,
  name Text NOT NULL,
  uuid Text NOT NULL,
  `desc` Text NOT NULL,
  checksum Text NOT NULL,
  `size` BIGINT NOT NULL,
  is_master TINYINT(1) DEFAULT FALSE,
  creation_date datetime,
  fk_creator INT NOT NULL,
  ntblfix TINYINT(1) NOT NULL DEFAULT 0,
  fk_state INT NOT NULL,
  PRIMARY KEY (id)
);

-- Image State
CREATE TABLE ImageState (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
);

-- MasteredOn
CREATE TABLE MasteredOn (
  fk_image INT NOT NULL,
  fk_imaging_log INT NOT NULL
);

-- ImagingLog
CREATE TABLE ImagingLog (
  id INT NOT NULL AUTO_INCREMENT,
  timestamp datetime,
  detail Text NOT NULL,
  fk_imaging_log_state INT NOT NULL,
  fk_target INT NOT NULL,
  fk_imaging_log_level INT NOT NULL,
  PRIMARY KEY (id)
);

-- BootServiceInMenu
CREATE TABLE BootServiceInMenu (
  fk_menuitem INT NOT NULL,
  fk_bootservice INT NOT NULL
);

-- PostInstallScriptInImage
CREATE TABLE PostInstallScriptInImage (
  fk_image INT NOT NULL,
  fk_post_install_script INT NOT NULL,
  `order` INT NOT NULL DEFAULT 0
);

-- ----------------------------------------------------------------------
-- Add unicity constraints
-- ----------------------------------------------------------------------
ALTER TABLE PostInstallScriptInImage            ADD UNIQUE (fk_image, fk_post_install_script, `order`);
ALTER TABLE BootServiceOnImagingServer          ADD UNIQUE (fk_boot_service, fk_imaging_server);
ALTER TABLE PostInstallScriptOnImagingServer    ADD UNIQUE (fk_post_install_script, fk_imaging_server);
ALTER TABLE ImageOnImagingServer                ADD UNIQUE (fk_image, fk_imaging_server);
ALTER TABLE Internationalization                ADD UNIQUE (id, fk_language);
ALTER TABLE ImageInMenu                         ADD UNIQUE (fk_image, fk_menuitem);
ALTER TABLE BootServiceInMenu                   ADD UNIQUE (fk_menuitem, fk_bootservice);
ALTER TABLE MasteredOn                          ADD UNIQUE (fk_image, fk_imaging_log);

-- ----------------------------------------------------------------------
-- Add foreign constraints
-- ----------------------------------------------------------------------
ALTER TABLE ImagingServer ADD FOREIGN KEY(fk_default_menu)     REFERENCES Menu(id);

ALTER TABLE Target ADD FOREIGN KEY(`type`)      REFERENCES TargetType(id);
ALTER TABLE Target ADD FOREIGN KEY(fk_entity)   REFERENCES Entity(id);
ALTER TABLE Target ADD FOREIGN KEY(fk_menu)     REFERENCES Menu(id);

ALTER TABLE ComputerDisk ADD FOREIGN KEY(fk_target) REFERENCES Target(id)
ON DELETE CASCADE;
ALTER TABLE ComputerPartition ADD FOREIGN KEY(fk_disk)
REFERENCES ComputerDisk(id);

ALTER TABLE ImagingServer ADD FOREIGN KEY(fk_entity)    REFERENCES Entity(id);

ALTER TABLE Menu ADD FOREIGN KEY(fk_name)               REFERENCES Internationalization(id);
ALTER TABLE Menu ADD FOREIGN KEY(fk_default_item)       REFERENCES MenuItem(id);
ALTER TABLE Menu ADD FOREIGN KEY(fk_default_item_WOL)   REFERENCES MenuItem(id);
ALTER TABLE Menu ADD FOREIGN KEY(fk_protocol)           REFERENCES Protocol(id);
ALTER TABLE Menu ADD FOREIGN KEY(fk_synchrostate)       REFERENCES SynchroState(id);

ALTER TABLE BootServiceOnImagingServer ADD FOREIGN KEY(fk_boot_service)     REFERENCES BootService(id);
ALTER TABLE BootServiceOnImagingServer ADD FOREIGN KEY(fk_imaging_server)   REFERENCES ImagingServer(id);

ALTER TABLE PostInstallScriptOnImagingServer ADD FOREIGN KEY(fk_post_install_script)    REFERENCES PostInstallScript(id);
ALTER TABLE PostInstallScriptOnImagingServer ADD FOREIGN KEY(fk_imaging_server)         REFERENCES ImagingServer(id);

ALTER TABLE ImageOnImagingServer ADD FOREIGN KEY(fk_image)          REFERENCES Image(id);
ALTER TABLE ImageOnImagingServer ADD FOREIGN KEY(fk_imaging_server) REFERENCES ImagingServer(id);

ALTER TABLE Partition ADD FOREIGN KEY(fk_image) REFERENCES Image(id);

ALTER TABLE Internationalization ADD FOREIGN KEY(fk_language) REFERENCES Language(id);

ALTER TABLE MenuItem ADD FOREIGN KEY(fk_menu) REFERENCES Menu(id);

ALTER TABLE ImageInMenu ADD FOREIGN KEY(fk_image)       REFERENCES Image(id);
ALTER TABLE ImageInMenu ADD FOREIGN KEY(fk_menuitem)    REFERENCES MenuItem(id);

ALTER TABLE Image ADD FOREIGN KEY(fk_creator) REFERENCES `User`(id);
ALTER TABLE Image ADD FOREIGN KEY(fk_state)   REFERENCES `ImageState`(id);

ALTER TABLE ImagingLog ADD FOREIGN KEY(fk_imaging_log_state)    REFERENCES ImagingLogState(id);
ALTER TABLE ImagingLog ADD FOREIGN KEY(fk_imaging_log_level)    REFERENCES ImagingLogLevel(id);
ALTER TABLE ImagingLog ADD FOREIGN KEY(fk_target)               REFERENCES Target(id);

ALTER TABLE MasteredOn ADD FOREIGN KEY(fk_image)                REFERENCES Image(id);
ALTER TABLE MasteredOn ADD FOREIGN KEY(fk_imaging_log)          REFERENCES ImagingLog(id);

ALTER TABLE BootServiceInMenu ADD FOREIGN KEY(fk_menuitem)      REFERENCES MenuItem(id);
ALTER TABLE BootServiceInMenu ADD FOREIGN KEY(fk_bootservice)   REFERENCES BootService(id);

ALTER TABLE PostInstallScriptInImage ADD FOREIGN KEY(fk_image)                  REFERENCES Image(id);
ALTER TABLE PostInstallScriptInImage ADD FOREIGN KEY(fk_post_install_script)    REFERENCES PostInstallScript(id);

ALTER TABLE BootService ADD FOREIGN KEY(fk_name)    REFERENCES Internationalization(id);
ALTER TABLE BootService ADD FOREIGN KEY(fk_desc)    REFERENCES Internationalization(id);

ALTER TABLE PostInstallScript ADD FOREIGN KEY(fk_name)  REFERENCES Internationalization(id);
ALTER TABLE PostInstallScript ADD FOREIGN KEY(fk_desc)  REFERENCES Internationalization(id);

-- ----------------------------------------------------------------------
-- Add indexes
-- ----------------------------------------------------------------------
CREATE INDEX fk_entity_default_menu_idx ON ImagingServer(fk_default_menu);

CREATE INDEX fk_target_type_idx     ON Target(`type`);
CREATE INDEX fk_target_entity_idx   ON Target(fk_entity);
CREATE INDEX fk_target_menu_idx     ON Target(fk_menu);

CREATE INDEX fk_imaging_server_entity_idx ON ImagingServer(fk_entity);

CREATE INDEX fk_menu_name_idx               ON Menu(fk_name);
CREATE INDEX fk_menu_default_item_idx       ON Menu(fk_default_item);
CREATE INDEX fk_menu_default_item_WOL_idx   ON Menu(fk_default_item_WOL);
CREATE INDEX fk_menu_protocol_idx           ON Menu(fk_protocol);
CREATE INDEX fk_menu_state_idx              ON Menu(fk_synchrostate);

CREATE INDEX fk_boot_service_on_imaging_server_boot_service_idx     ON BootServiceOnImagingServer(fk_boot_service);
CREATE INDEX fk_boot_service_on_imaging_server_imaging_server_idx   ON BootServiceOnImagingServer(fk_imaging_server);

CREATE INDEX fk_post_install_script_on_imaging_server_post_install_script_idx   ON PostInstallScriptOnImagingServer(fk_post_install_script);
CREATE INDEX fk_post_install_script_on_imaging_server_imaging_server_idx        ON PostInstallScriptOnImagingServer(fk_imaging_server);

CREATE INDEX fk_image_on_imaging_server_image_idx           ON ImageOnImagingServer(fk_image);
CREATE INDEX fk_image_on_imaging_server_imaging_server_idx  ON ImageOnImagingServer(fk_imaging_server);

CREATE INDEX fk_partition_image_idx ON Partition(fk_image);

CREATE INDEX fk_menu_item_menu_idx ON MenuItem(fk_menu);

CREATE INDEX fk_image_in_menu_image_idx     ON ImageInMenu(fk_image);
CREATE INDEX fk_image_in_menu_menuitem_idx  ON ImageInMenu(fk_menuitem);

CREATE INDEX fk_image_creator_idx ON Image(fk_creator);

CREATE INDEX fk_imaging_log_state_idx   ON ImagingLog(fk_imaging_log_state);
CREATE INDEX fk_imaging_log_level_idx   ON ImagingLog(fk_imaging_log_level);
CREATE INDEX fk_imaging_log_target_idx  ON ImagingLog(fk_target);

CREATE INDEX fk_mastered_on_image_idx         ON MasteredOn(fk_image);
CREATE INDEX fk_mastered_on_imaging_log_idx   ON MasteredOn(fk_imaging_log);

CREATE INDEX fk_boot_service_in_menu_menuitem_idx       ON BootServiceInMenu(fk_menuitem);
CREATE INDEX fk_boot_service_in_menu_bootservice_idx    ON BootServiceInMenu(fk_bootservice);

CREATE INDEX fk_post_install_script_in_image_image_idx                  ON PostInstallScriptInImage(fk_image);
CREATE INDEX fk_post_install_script_in_image_post_install_script_idx    ON PostInstallScriptInImage(fk_post_install_script);

-- ----------------------------------------------------------------------
-- Insert data
-- ----------------------------------------------------------------------
INSERT INTO TargetType (id, label) VALUES (01, "computer");
INSERT INTO TargetType (id, label) VALUES (02, "profile");
INSERT INTO TargetType (id, label) VALUES (03, "computer_in_profile");
-- WARNING the 04 is a fake type used in the code!
INSERT INTO TargetType (id, label) VALUES (05, "deleted_computer");

INSERT INTO ImagingLogState (id, label) VALUES (01, "unknown");
INSERT INTO ImagingLogState (id, label) VALUES (02, "boot");
INSERT INTO ImagingLogState (id, label) VALUES (03, "menu");
INSERT INTO ImagingLogState (id, label) VALUES (04, "restoration");
INSERT INTO ImagingLogState (id, label) VALUES (05, "backup");
INSERT INTO ImagingLogState (id, label) VALUES (06, "postinstall");
INSERT INTO ImagingLogState (id, label) VALUES (07, "error");
INSERT INTO ImagingLogState (id, label) VALUES (08, "delete");
INSERT INTO ImagingLogState (id, label) VALUES (09, "inventory");

/* Logs levels are shifted by one */
INSERT INTO ImagingLogLevel (id, label) VALUES (1, "LOG_EMERG");
INSERT INTO ImagingLogLevel (id, label) VALUES (2, "LOG_ALERT");
INSERT INTO ImagingLogLevel (id, label) VALUES (3, "LOG_CRIT");
INSERT INTO ImagingLogLevel (id, label) VALUES (4, "LOG_ERR");
INSERT INTO ImagingLogLevel (id, label) VALUES (5, "LOG_WARNING");
INSERT INTO ImagingLogLevel (id, label) VALUES (6, "LOG_NOTICE");
INSERT INTO ImagingLogLevel (id, label) VALUES (7, "LOG_INFO");
INSERT INTO ImagingLogLevel (id, label) VALUES (8, "LOG_DEBUG");

/* Default Image States */
INSERT INTO ImageState (id, label) VALUES (1, "UNKNOWN");
INSERT INTO ImageState (id, label) VALUES (2, "DONE");
INSERT INTO ImageState (id, label) VALUES (3, "TODO");
INSERT INTO ImageState (id, label) VALUES (4, "FAILED");
INSERT INTO ImageState (id, label) VALUES (5, "EMPTY");
INSERT INTO ImageState (id, label) VALUES (6, "INPROGRESS");
INSERT INTO ImageState (id, label) VALUES (7, "INVALID");

INSERT INTO Protocol (label) VALUES ("nfs");
INSERT INTO Protocol (label) VALUES ("mtftp");

INSERT INTO Language (id, label) VALUES (1, "English");
INSERT INTO Language (id, label) VALUES (2, "Français");
INSERT INTO Language (id, label) VALUES (3, "Español");

INSERT INTO SynchroState (label) VALUES ("TODO");
INSERT INTO SynchroState (label) VALUES ("DONE");
INSERT INTO SynchroState (label) VALUES ("RUNNING");
INSERT INTO SynchroState (label) VALUES ("INIT_ERROR");

INSERT INTO Internationalization (id, fk_language, label) VALUES (01, 2, "NOTTRANSLATED");
INSERT INTO Internationalization (id, fk_language, label) VALUES (02, 2, "Continuer le démarrage normalement");
INSERT INTO Internationalization (id, fk_language, label) VALUES (03, 2, "Démarrer comme d\'habitude");
INSERT INTO Internationalization (id, fk_language, label) VALUES (04, 2, "Ajouter comme client Pulse 2");
INSERT INTO Internationalization (id, fk_language, label) VALUES (05, 2, "Enregistrer ce poste auprès du server Pulse 2");
INSERT INTO Internationalization (id, fk_language, label) VALUES (06, 2, "Créer une image");
INSERT INTO Internationalization (id, fk_language, label) VALUES (07, 2, "Réaliser une image de ce poste");
INSERT INTO Internationalization (id, fk_language, label) VALUES (08, 2, "Démarrage sans disque");
INSERT INTO Internationalization (id, fk_language, label) VALUES (09, 2, "Charger un environnement sans disque et obtenir une invite de commande");
INSERT INTO Internationalization (id, fk_language, label) VALUES (10, 2, "Test mémoire");
INSERT INTO Internationalization (id, fk_language, label) VALUES (11, 2, "Réaliser une vérification complète de la mémoire");
INSERT INTO Internationalization (id, fk_language, label) VALUES (12, 2, "Menu d\'inscription d\'un ordinateur");
INSERT INTO Internationalization (id, fk_language, label) VALUES (13, 2, "Inscrit la date dans C:\\date.txt");
INSERT INTO Internationalization (id, fk_language, label) VALUES (14, 2, "Copie du fichier sysprep.inf sur C:\\");
INSERT INTO Internationalization (id, fk_language, label) VALUES (15, 2, "Changement à la fois le SID et le Netbios");
INSERT INTO Internationalization (id, fk_language, label) VALUES (16, 2, "Éteindre le client apres restoration");
INSERT INTO Internationalization (id, fk_language, label) VALUES (17, 2, "Shell de debug");
INSERT INTO Internationalization (id, fk_language, label) VALUES (18, 2, "La seule et unique partition FAT ou EXT2 sera étendue à l\'intégralité du disque dur");
INSERT INTO Internationalization (id, fk_language, label) VALUES (19, 2, "La seule et unique partition NTFS sera étendue à l\'intégralité du disque dur");
INSERT INTO Internationalization (id, fk_language, label) VALUES (20, 2, "Installer le Pack d\'agents Pulse 2");
INSERT INTO Internationalization (id, fk_language, label) VALUES (21, 2, "RAID1 synchro pour chipset ICH5 du 1er disque vers le 2ème");
INSERT INTO Internationalization (id, fk_language, label) VALUES (22, 2, "Menu par défaut");

INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (1, "Continue Usual Startup", "Start as usual", 2, 3, "root (hd0)\nchainloader +1");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (2, "Register as Pulse 2 Client", "Record this computer in Pulse 2 Server", 4, 5, "identify L=##PULSE2_LANG## P=none\nreboot");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (3, "Create a backup", "Create a backup of this computer", 6, 7, "kernel ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL## ##PULSE2_KERNEL_OPTS## ##PULSE2_REVO_RAW## revosavedir=##PULSE2_MASTERS_DIR## revoinfodir=##PULSE2_COMPUTERS_DIR## revobase=##PULSE2_BASE_DIR## ##PULSE2_DISKLESS_OPTS##\ninitrd ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (4, "Diskless Boot", "Load diskless environment then get a prompt", 8, 9, "kernel ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_KERNEL## ##PULSE2_KERNEL_OPTS## revobase=##PULSE2_BASE_DIR## ##PULSE2_DISKLESS_OPTS## revodebug\ninitrd ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_INITRD##");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (5, "Memory test", "Run a full memory check", 10, 11, "kernel --type=openbsd ##PULSE2_NETDEVICE##/##PULSE2_DISKLESS_DIR##/##PULSE2_DISKLESS_MEMTEST##");

INSERT INTO Menu (id, default_name, fk_name, timeout, background_uri, message, ethercard, bootcli, disklesscli, dont_check_disk_size, fk_default_item, fk_default_item_WOL, fk_protocol) VALUES (1, "Default Boot Menu", 22, 10, "/##PULSE2_BOOTLOADER_DIR##/##PULSE2_BOOTSPLASH_FILE##", "-- Warning! Your PC is being backed up or restored. Do not reboot !", 0, 0, 0, 0, NULL, NULL, 1);
INSERT INTO Menu (id, default_name, fk_name, timeout, background_uri, message, ethercard, bootcli, disklesscli, dont_check_disk_size, fk_default_item, fk_default_item_WOL, fk_protocol) VALUES (2, "Register Boot Menu", 12, 10, "/##PULSE2_BOOTLOADER_DIR##/##PULSE2_BOOTSPLASH_FILE##", "-- Warning! Your PC is being backed up or restored. Do not reboot !", 0, 0, 0, 0, NULL, NULL, 1);

INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (01, "Date",                 "Write the current date in file C:\\date.txt",                                          1, 13, "Mount 1\n\ndate | unix2dos >> /mnt/date.txt\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (02, "Sysprep",              "Copy sysprep.inf on C:\\",                                                             1, 14, "Mount 1\nCopySysprepInf /revoinfo/sysprep.inf\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (03, "SID",                  "Change both SID and Netbios name",                                                     1, 15, "Mount 1\nChangeSIDAndName");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (04, "Shutdown",             "Halt client",                                                                          1, 16, "halt\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (05, "Debug",                "Debug Shell",                                                                          1, 17, "sh </dev/console >/dev/console\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (06, "Partition extension",  "The first (and only) FAT or EXT2 partition will be extend across the whole disk.",     1, 18, "ResizeMax 1\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (07, "NTFS Resize",          "The first (and only) NTFS partition will be extend across the whole disk.",            1, 19, "NtfsResizeMax 1\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (08, "Agent Pack",           "Install the Pulse 2 Agent Pack (VNC, OpenSSH, OCS Inventory and the SSH key).",        1, 20, "Mount 1\n\nmkdir -p /mnt/tmp\n\ncp /opt/winutils/setupssh.exe /mnt/tmp\ncp /opt/winutils/tightvncssh.exe /mnt/tmp\ncp /revoinfo/data/id_dsa.pub /mnt\n\necho -en 'cd c:\\tmp\\nsetupssh.exe /S\\ntightvncssh.exe /sp- /silent /norestart\\ndel c:\\tmp\\setupssh.exe' | unix2dos > /mnt/tmp/setup.bat\n\nRegistryAddRunOnce 'c:\tmp\setup.bat'\n");
INSERT INTO PostInstallScript (id, default_name, default_desc, fk_name, fk_desc, value) VALUES (09, "ICH 5 sync",           "RAID1 synchronization for ICH5 chipsets, duplicate the first disk on the second one",  1, 21, "/opt/bin/dd_rescue -b 10485760 /dev/sda /dev/sdb\n");

INSERT INTO MenuItem (id, `order`, hidden, hidden_WOL, fk_menu) VALUES (1, 0, 0, 0, 1);
INSERT INTO MenuItem (id, `order`, hidden, hidden_WOL, fk_menu) VALUES (2, 1, 0, 0, 1);
INSERT INTO MenuItem (id, `order`, hidden, hidden_WOL, fk_menu) VALUES (3, 0, 0, 0, 2);
INSERT INTO MenuItem (id, `order`, hidden, hidden_WOL, fk_menu) VALUES (4, 1, 0, 0, 2);

INSERT INTO BootServiceInMenu (fk_bootservice, fk_menuitem) VALUES (1, 1);
INSERT INTO BootServiceInMenu (fk_bootservice, fk_menuitem) VALUES (3, 2);
INSERT INTO BootServiceInMenu (fk_bootservice, fk_menuitem) VALUES (1, 3);
INSERT INTO BootServiceInMenu (fk_bootservice, fk_menuitem) VALUES (2, 4);

UPDATE Menu SET fk_default_item = 1, fk_default_item_WOL = 1 WHERE id = 1;
UPDATE Menu SET fk_default_item = 3, fk_default_item_WOL = 3 WHERE id = 2;

/* This corresponds to our root entity, inventory-side */
INSERT INTO Entity (id, name, uuid) VALUES (1, "root", "UUID1");

/* Default user */
INSERT INTO User (id, login) VALUES (1, 'UNKNOWN');

COMMIT;
