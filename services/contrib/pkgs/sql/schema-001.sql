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

CREATE TABLE IF NOT EXISTS version (
  Number tinyint(4) unsigned NOT NULL default '0'
);

CREATE TABLE IF NOT EXISTS `pkgs`.`packages`
(
  id INT AUTO_INCREMENT NOT NULL PRIMARY KEY,
  label varchar(45)  null,
  description varchar(255) null,
  uuid varchar(36)  null,
  version varchar(50)  null,
  os varchar(20)  null,
  metagenerator varchar(10)  null,
  entity_id int          null,
  sub_packages varchar(255) null,
  reboot int(1)       null,
  inventory_associateinventory varchar(10)  null,
  inventory_licenses varchar(20)  null,
  Qversion varchar(50)  null,
  Qvendor varchar(50)  null,
  Qsoftware varchar(50)  null,
  boolcnd varchar(50)  null,
  postCommandSuccess_command varchar(50)  null,
  postCommandSuccess_name varchar(50)  null,
  installInit_command varchar(50)  null,
  installInit_name varchar(50)  null,
  postCommandFailure_command varchar(50)  null,
  postCommandFailure_name varchar(50)  null,
  command_command varchar(50)  null,
  command_name varchar(50)  null,
  preCommand_command varchar(50)  null,
  preCommand_name varchar(50)  null,
  UNIQUE INDEX `uuid_UNIQUE` (`uuid` ASC));
  CREATE INDEX `id_packages_uuid` ON `packages` (`uuid`);

  create table if not exists extensions
  (
    id            int auto_increment
      primary key,
    rule_order    int null          comment 'The order of the rule determines which one is run firstly',
    rule_name     varchar(255) null comment 'The rule name',
    name          varchar(255) null comment 'basename for software',
    extension     varchar(255) null comment 'Ext file or empty',
    magic_command varchar(255) null comment 'Magic number of the file',
    bang          varchar(255) null comment 'The bang file can be declared',
    file          varchar(255) null comment 'Elements found by the file command',
    strings       varchar(255) null comment 'Elements found by the strings command in the head of the file',
    proposition   varchar(255) null comment 'The proposed result for the researched file',
    description   varchar(255) null comment 'A description for the rule'
  );

create table if not exists dependencies
(
    id            int auto_increment
      primary key,
    uuid_package    varchar(255) not null comment 'UUID of the package',
    uuid_dependency varchar(255) not null comment 'UUID of the corresponding dependency'
  );

create table if not exists syncthingsync
(
  id              int auto_increment
    primary key,
  date            timestamp   default CURRENT_TIMESTAMP not null,
  uuidpackage     varchar(45)                           not null,
  typesynchro     varchar(45) default 'create'          not null,
  relayserver_jid varchar(255)                          not null,
  watching        varchar(3)  default 'yes'             null
);

INSERT INTO extensions VALUES(NULL, 1, "Firefox Rule", "firefox", "exe", "", "", "", "", '"%s" -ms', "Rule for Firefox");
INSERT INTO extensions VALUES(NULL, 2, "7zip Rule","7z", "exe", "", "", "", "7zipInstall", '"%s" /S', "Rule for 7-zip");
insert into extensions values(null, 3, "Bash Rule","", "", "", "bash", "", "", './"%s"', "Rule for bash scripts");
insert into extensions values(null, 4, "Nullsoft Rule", '', 'exe', '', '', ' Nullsoft', '', '"%s" /S', 'Rule for NSIS installer');
insert into extensions values(null, 5, "InnoSetup Rule", '', 'exe', '', '', '', 'JR.Inno.Setup', '"%s" /SP /VERYSILENT /NORESTART', "Rule for Inno installer");

INSERT INTO version VALUES( '1' );

COMMIT;
