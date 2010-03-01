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

-- MasteredOnState
CREATE TABLE MasteredOnState (
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
  fk_default_menu INT NOT NULL,
  PRIMARY KEY (id)
);

-- Target
CREATE TABLE Target (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  uuid Text NOT NULL,
  kernel_parameters Text,
  image_parameters Text,
  `type` INT NOT NULL,
  fk_entity INT NOT NULL,
  fk_menu INT NOT NULL,
  PRIMARY KEY (id)
);

-- ImagingServer
CREATE TABLE ImagingServer (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  url Text NOT NULL,
  packageserver_uuid Text NOT NULL,
  recursive Bool NOT NULL DEFAULT 0,
  fk_entity INT NOT NULL,
  PRIMARY KEY (id)
);

-- Menu
CREATE TABLE Menu (
  id INT NOT NULL AUTO_INCREMENT,
  default_name Text NOT NULL,
  fk_name INT,
  timeout INT,
  background_uri Text DEFAULT '',
  message Text NOT NULL DEFAULT '',
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
  `size_sect` INT NOT NULL,
  start_sect INT NOT NULL,
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
  `size` INT NOT NULL,
  is_master BOOL DEFAULT FALSE,
  creation_date datetime,
  fk_creator INT NOT NULL,
  PRIMARY KEY (id)
);

-- MasteredOn
CREATE TABLE MasteredOn (
  id INT NOT NULL AUTO_INCREMENT,
  timestamp datetime,
  title Text NOT NULL,
  detail Text NOT NULL,
  fk_mastered_on_state INT NOT NULL,
  fk_image INT NOT NULL,
  fk_target INT NOT NULL,
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
  fk_post_install_script INT NOT NULL
);

-- ----------------------------------------------------------------------
-- Add unicity constraints
-- ----------------------------------------------------------------------
ALTER TABLE PostInstallScriptInImage            ADD UNIQUE (fk_image, fk_post_install_script);
ALTER TABLE BootServiceOnImagingServer          ADD UNIQUE (fk_boot_service, fk_imaging_server);
ALTER TABLE PostInstallScriptOnImagingServer    ADD UNIQUE (fk_post_install_script, fk_imaging_server);
ALTER TABLE ImageOnImagingServer                ADD UNIQUE (fk_image, fk_imaging_server);
ALTER TABLE Internationalization                ADD UNIQUE (id, fk_language);
ALTER TABLE ImageInMenu                         ADD UNIQUE (fk_image, fk_menuitem);
ALTER TABLE BootServiceInMenu                   ADD UNIQUE (fk_menuitem, fk_bootservice);

-- ----------------------------------------------------------------------
-- Add foreign constraints
-- ----------------------------------------------------------------------
ALTER TABLE Entity ADD FOREIGN KEY(fk_default_menu)     REFERENCES Menu(id);

ALTER TABLE Target ADD FOREIGN KEY(`type`)      REFERENCES TargetType(id);
ALTER TABLE Target ADD FOREIGN KEY(fk_entity)   REFERENCES Entity(id);
ALTER TABLE Target ADD FOREIGN KEY(fk_menu)     REFERENCES Menu(id);

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

ALTER TABLE MasteredOn ADD FOREIGN KEY(fk_mastered_on_state)    REFERENCES MasteredOnState(id);
ALTER TABLE MasteredOn ADD FOREIGN KEY(fk_image)                REFERENCES Image(id);
ALTER TABLE MasteredOn ADD FOREIGN KEY(fk_target)               REFERENCES Target(id);

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
CREATE INDEX fk_entity_default_menu_idx ON Entity(fk_default_menu);

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

CREATE INDEX fk_mastered_on_state_idx   ON MasteredOn(fk_mastered_on_state);
CREATE INDEX fk_mastered_on_image_idx   ON MasteredOn(fk_image);
CREATE INDEX fk_mastered_on_target_idx  ON MasteredOn(fk_target);

CREATE INDEX fk_boot_service_in_menu_menuitem_idx       ON BootServiceInMenu(fk_menuitem);
CREATE INDEX fk_boot_service_in_menu_bootservice_idx    ON BootServiceInMenu(fk_bootservice);

CREATE INDEX fk_post_install_script_in_image_image_idx                  ON PostInstallScriptInImage(fk_image);
CREATE INDEX fk_post_install_script_in_image_post_install_script_idx    ON PostInstallScriptInImage(fk_post_install_script);

-- ----------------------------------------------------------------------
-- Insert data
-- ----------------------------------------------------------------------
INSERT INTO TargetType (label) VALUES ("computer");
INSERT INTO TargetType (label) VALUES ("profile");

INSERT INTO MasteredOnState (label) VALUES ("backup_done");
INSERT INTO MasteredOnState (label) VALUES ("backup_failed");
INSERT INTO MasteredOnState (label) VALUES ("restore_done");
INSERT INTO MasteredOnState (label) VALUES ("restore_failed");

INSERT INTO Protocol (label) VALUES ("nfs");
INSERT INTO Protocol (label) VALUES ("tftp");
INSERT INTO Protocol (label) VALUES ("mtftp");

INSERT INTO Language (label) VALUES ("English");
INSERT INTO Language (label) VALUES ("Français");
INSERT INTO Language (label) VALUES ("Español");

INSERT INTO SynchroState (label) VALUES ("TODO");
INSERT INTO SynchroState (label) VALUES ("DONE");
INSERT INTO SynchroState (label) VALUES ("RUNNING");

INSERT INTO Internationalization (id, fk_language, label) VALUES (1, 2, "Menu par défaut");
INSERT INTO Internationalization (id, fk_language, label) VALUES (2, 2, "Continuer le démarrage normalement");
INSERT INTO Internationalization (id, fk_language, label) VALUES (3, 2, "Démarrer comme d\'habitude");
INSERT INTO Internationalization (id, fk_language, label) VALUES (4, 2, "Ajouter comme client Pulse 2");
INSERT INTO Internationalization (id, fk_language, label) VALUES (5, 2, "Enregistrer ce poste auprès du server Pulse 2");
INSERT INTO Internationalization (id, fk_language, label) VALUES (6, 2, "Créer une image");
INSERT INTO Internationalization (id, fk_language, label) VALUES (7, 2, "Réaliser une image de ce poste");
INSERT INTO Internationalization (id, fk_language, label) VALUES (8, 2, "Démarrage sans disque");
INSERT INTO Internationalization (id, fk_language, label) VALUES (9, 2, "Charger un environnement sans disque et obtenir une invite de commande");
INSERT INTO Internationalization (id, fk_language, label) VALUES (10, 2, "Test mémoire");
INSERT INTO Internationalization (id, fk_language, label) VALUES (11, 2, "Réaliser une vérification complète de la mémoire");

INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (1, "Continue Normal Startup", "Start as usual", 1, 2, "root (hd0)\r\nchainloader +1");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (2, "Register as Pulse 2 Client", "Record this computer in Pulse 2 Server", 3, 4, "identify L=##PULSE2_LANG## P=none\nreboot");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (3, "Create a backup", "Create a backup of this computer", 5, 6, "kernel ##PULSE2_NETDEVICE##/##PULSE2_F_DISKLESS##/##PULSE2_K_DISKLESS## revosavedir=/##PULSE2_F_MASTERS##/##PULSE2_F_IMAGE## revoroot=##PULSE2_F_BASE## quiet\ninitrd ##PULSE2_NETDEVICE##/##PULSE2_F_DISKLESS##/##PULSE2_I_DISKLESS##");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (4, "Diskless Boot", "Load diskless environment then get a prompt", 7, 8, "kernel ##PULSE2_NETDEVICE##/##PULSE2_F_DISKLESS##/##PULSE2_K_DISKLESS## revodebug revoroot=##PULSE2_F_BASE## quiet\ninitrd ##PULSE2_NETDEVICE##/##PULSE2_F_DISKLESS##/##PULSE2_I_DISKLESS##");
INSERT INTO BootService (id, default_name, default_desc, fk_name, fk_desc, `value`) VALUES (5, "Memory test", "Run a full memory check", 9, 10, "kernel --kernel-type=openbsd ##PULSE2_NETDEVICE##/##PULSE2_F_DISKLESS##/##PULSE2_MEMTEST##");

INSERT INTO Menu (id, default_name, fk_name, timeout, background_uri, message, fk_default_item, fk_default_item_WOL, fk_protocol) VALUES (1, "Default Boot Menu", 1, NULL, "/##PULSE2_F_DISKLESS##/##PULSE2_F_BOOTSPLASH##", "-- Warning! Your PC is being backed up or restored. Do not reboot !", NULL, NULL, 1);

INSERT INTO MenuItem (id, `order`, hidden, hidden_WOL, fk_menu) VALUES (1, 1, 0, 0, 1);
INSERT INTO MenuItem (id, `order`, hidden, hidden_WOL, fk_menu) VALUES (2, 2, 0, 0, 1);

INSERT INTO BootServiceInMenu (fk_bootservice, fk_menuitem) VALUES (1, 1);
INSERT INTO BootServiceInMenu (fk_bootservice, fk_menuitem) VALUES (2, 2);

UPDATE Menu SET fk_default_item = 1, fk_default_item_WOL = 1 WHERE id = 1;

INSERT INTO Entity (id, name, uuid, fk_default_menu) VALUES (1, "NEED_ASSOCIATION", "NEED_ASSOCIATION", 1);

INSERT INTO User (id, login) VALUES (1, 'UNKNOWN');

COMMIT;

