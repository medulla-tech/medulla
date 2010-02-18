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



--
-- Database version
--

CREATE TABLE Version (
  Number tinyint(4) unsigned NOT NULL default '0'
) ENGINE=INNODB CHARSET=UTF8;

INSERT INTO Version VALUES( '1' );

-- nomenclatures tables
-- TargetType
CREATE TABLE TargetType (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- MasteredOnState
CREATE TABLE MasteredOnState (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- Protocol
CREATE TABLE Protocol (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- Language
CREATE TABLE Language (
  id INT NOT NULL AUTO_INCREMENT,
  label Text NOT NULL,
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;
-- end of the nomenclatures tables

-- BootService
CREATE TABLE BootService (
  id INT NOT NULL AUTO_INCREMENT,
  value Text NOT NULL,
  `desc` Text NOT NULL,
  uri Text NOT NULL,
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- User
CREATE TABLE `User` (
  id INT NOT NULL AUTO_INCREMENT,
  login Text NOT NULL,
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- PostInstallScript
CREATE TABLE PostInstallScript (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  value Text NOT NULL,
  uri Text NOT NULL,
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- Entity
CREATE TABLE Entity (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  uuid Text NOT NULL,
  fk_default_menu INT NOT NULL,
  FOREIGN KEY (fk_default_menu) REFERENCES Menu(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

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
  FOREIGN KEY (`type`) REFERENCES TargetType(id),
  FOREIGN KEY (fk_entity) REFERENCES Entity(id),
  FOREIGN KEY (fk_menu) REFERENCES Menu(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- ImagingServer
CREATE TABLE ImagingServer (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  url Text NOT NULL,
  packageserver_uuid Text NOT NULL,
  recursive Bool NOT NULL DEFAULT 0,
  fk_entity INT NOT NULL,
  FOREIGN KEY (fk_entity) REFERENCES Entity(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- Menu
CREATE TABLE Menu (
  id INT NOT NULL AUTO_INCREMENT,
  default_name Text NOT NULL,
  fk_name INT NOT NULL,
  timeout INT NOT NULL,
  background_uri Text DEFAULT '',
  message Text NOT NULL DEFAULT '', -- Warning! Your PC is being backed up or restored. Do not reboot !',
  fk_default_item INT NOT NULL,
  fk_default_item_WOL INT NOT NULL,
  fk_protocol INT DEFAULT 0,
  FOREIGN KEY (fk_name) REFERENCES Internationalization(id),
  FOREIGN KEY (fk_default_item) REFERENCES MenuItem(id),
  FOREIGN KEY (fk_default_item_WOL) REFERENCES MenuItem(id),
  FOREIGN KEY (fk_protocol) REFERENCES Protocol(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- BootServiceOnImagingServer
CREATE TABLE BootServiceOnImagingServer (
  fk_boot_service INT NOT NULL,
  fk_imaging_server INT NOT NULL,
  FOREIGN KEY(fk_boot_service) REFERENCES BootService(id),
  FOREIGN KEY(fk_imaging_server) REFERENCES ImagingServer(id)
) ENGINE=INNODB CHARSET=UTF8;

-- ImageOnImagingServer
CREATE TABLE ImageOnImagingServer (
  fk_image INT NOT NULL,
  fk_imaging_server INT NOT NULL,
  FOREIGN KEY(fk_image) REFERENCES Image(id),
  FOREIGN KEY(fk_imaging_server) REFERENCES ImagingServer(id)
) ENGINE=INNODB CHARSET=UTF8;

-- Partition
CREATE TABLE Partition (
  id INT NOT NULL AUTO_INCREMENT,
  name Text NOT NULL,
  filesystem Text NOT NULL,
  `size_sect` INT NOT NULL,
  start_sect INT NOT NULL,
  fk_image INT NOT NULL,
  FOREIGN KEY(fk_image) REFERENCES Image(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- Internationalization
CREATE TABLE Internationalization (
  id INT NOT NULL,
  label Text NOT NULL,
  fk_language INT NOT NULL,
  FOREIGN KEY(fk_language) REFERENCES Language(id)
) ENGINE=INNODB CHARSET=UTF8;

-- MenuItem
CREATE TABLE MenuItem (
  id INT NOT NULL AUTO_INCREMENT,
  default_name Text NOT NULL,
  `order` INT NOT NULL,
  hidden Bool DEFAULT 1,
  hidden_WOL Bool DEFAULT 1,
  fk_menu INT NOT NULL,
  fk_name INT NOT NULL,
  `desc` Text,
  FOREIGN KEY(fk_menu) REFERENCES Menu(id),
  FOREIGN KEY(fk_name) REFERENCES Internationalization(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- ImageInMenu
CREATE TABLE ImageInMenu (
  fk_image INT NOT NULL,
  fk_menuitem INT NOT NULL,
  FOREIGN KEY(fk_image) REFERENCES Image(id),
  FOREIGN KEY(fk_menuitem) REFERENCES MenuItem(id)
) ENGINE=INNODB CHARSET=UTF8;

-- Image
CREATE TABLE Image (
  id INT NOT NULL AUTO_INCREMENT,
  path Text NOT NULL,
  checksum Text NOT NULL,
  `size` INT NOT NULL,
  `desc` Text NOT NULL,
  is_master Bool DEFAULT 0,
  creation_date datetime,
  fk_creator INT NOT NULL,
  FOREIGN KEY(fk_creator) REFERENCES `User`(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- MasteredOn
CREATE TABLE MasteredOn (
  id INT NOT NULL AUTO_INCREMENT,
  timestamp datetime,
  title Text NOT NULL,
  detail Text NOT NULL,
  fk_mastered_on_state INT NOT NULL,
  fk_image INT NOT NULL,
  fk_target INT NOT NULL,
  FOREIGN KEY(fk_mastered_on_state) REFERENCES MasteredOnState(id),
  FOREIGN KEY(fk_image) REFERENCES Image(id),
  FOREIGN KEY(fk_target) REFERENCES Target(id),
  PRIMARY KEY (id)
) ENGINE=INNODB CHARSET=UTF8;

-- BootServiceInMenu
CREATE TABLE BootServiceInMenu (
  fk_menuitem INT NOT NULL,
  fk_bootservice INT NOT NULL,
  FOREIGN KEY(fk_menuitem) REFERENCES MenuItem(id),
  FOREIGN KEY(fk_bootservice) REFERENCES BootService(id)
) ENGINE=INNODB CHARSET=UTF8;


-- PostInstallScriptInImage
CREATE TABLE PostInstallScriptInImage (
  fk_image INT NOT NULL,
  fk_post_install_script INT NOT NULL,
  FOREIGN KEY(fk_image) REFERENCES Image(id),
  FOREIGN KEY(fk_post_install_script) REFERENCES PostInstallScript(id)
) ENGINE=INNODB CHARSET=UTF8;

-- ----------------------------------------------------------------------
-- Add unicity constraints
-- ----------------------------------------------------------------------
ALTER TABLE PostInstallScriptInImage    ADD UNIQUE (fk_image, fk_post_install_script);
ALTER TABLE BootServiceOnImagingServer  ADD UNIQUE (fk_boot_service, fk_imaging_server);
ALTER TABLE ImageOnImagingServer        ADD UNIQUE (fk_image, fk_imaging_server);
ALTER TABLE Internationalization        ADD UNIQUE (id, fk_language);
ALTER TABLE ImageInMenu                 ADD UNIQUE (fk_image, fk_menuitem);
ALTER TABLE BootServiceInMenu           ADD UNIQUE (fk_menuitem, fk_bootservice);

-- ----------------------------------------------------------------------
-- Add indexes
-- ----------------------------------------------------------------------
CREATE INDEX fk_entity_default_menu_idx ON Entity(fk_default_menu);

CREATE INDEX fk_target_type_idx ON Target(`type`);
CREATE INDEX fk_target_entity_idx ON Target(fk_entity);
CREATE INDEX fk_target_menu_idx ON Target(fk_menu);

CREATE INDEX fk_imaging_server_entity_idx ON ImagingServer(fk_entity);

CREATE INDEX fk_menu_name_idx ON Menu(fk_name);
CREATE INDEX fk_menu_default_item_idx ON Menu(fk_default_item);
CREATE INDEX fk_menu_default_item_WOL_idx ON Menu(fk_default_item_WOL);
CREATE INDEX fk_menu_protocol_idx ON Menu(fk_protocol);

CREATE INDEX fk_boot_service_on_imaging_server_boot_service_idx ON BootServiceOnImagingServer(fk_boot_service);
CREATE INDEX fk_boot_service_on_imaging_server_imaging_server_idx ON BootServiceOnImagingServer(fk_imaging_server);

CREATE INDEX fk_image_on_imaging_server_image_idx ON ImageOnImagingServer(fk_image);
CREATE INDEX fk_image_on_imaging_server_imaging_server_idx ON ImageOnImagingServer(fk_imaging_server);

CREATE INDEX fk_partition_image_idx ON Partition(fk_image);

CREATE INDEX fk_menu_item_menu_idx ON MenuItem(fk_menu);
CREATE INDEX fk_menu_item_name_idx ON MenuItem(fk_name);

CREATE INDEX fk_image_in_menu_image_idx ON ImageInMenu(fk_image);
CREATE INDEX fk_image_in_menu_menuitem_idx ON ImageInMenu(fk_menuitem);

CREATE INDEX fk_image_creator_idx ON Image(fk_creator);

CREATE INDEX fk_mastered_on_state_idx ON MasteredOn(fk_mastered_on_state);
CREATE INDEX fk_mastered_on_image_idx ON MasteredOn(fk_image);
CREATE INDEX fk_mastered_on_target_idx ON MasteredOn(fk_target);

CREATE INDEX fk_boot_service_in_menu_menuitem_idx ON BootServiceInMenu(fk_menuitem);
CREATE INDEX fk_boot_service_in_menu_bootservice_idx ON BootServiceInMenu(fk_bootservice);

CREATE INDEX fk_post_install_script_in_image_image_idx ON PostInstallScriptInImage(fk_image);
CREATE INDEX fk_post_install_script_in_image_post_install_script_idx ON PostInstallScriptInImage(fk_post_install_script);

-- ----------------------------------------------------------------------
-- Insert data
-- ----------------------------------------------------------------------
INSERT INTO TargetType (label) values ('computer');
INSERT INTO TargetType (label) values ('profile');

INSERT INTO MasteredOnState (label) values ('backup_done');
INSERT INTO MasteredOnState (label) values ('backup_failed');
INSERT INTO MasteredOnState (label) values ('restore_done');
INSERT INTO MasteredOnState (label) values ('restore_failed');

INSERT INTO Protocol (label) values ('');
INSERT INTO Protocol (label) values ('tftp');
INSERT INTO Protocol (label) values ('nfs');
INSERT INTO Protocol (label) values ('mtftp');

INSERT INTO Language (label) values ('English');
INSERT INTO Language (label) values ('Français');
INSERT INTO Language (label) values ('Español');

