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

INSERT INTO version VALUES( '1' );

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


  create table if not exists extensions
  (
    id            int auto_increment
      primary key,
    name          varchar(255) null comment 'basename for software',
    extension     varchar(255) null comment 'Ext file or empty',
    magic_command varchar(255) null comment 'Magic number of the file',
    bang          varchar(255) null comment 'The bang file can be declared',
    file          varchar(255) null comment 'Elements found by the file command',
    string_head   varchar(255) null comment 'Elements found by the strings command in the head of the file',
    string_tail   varchar(255) null comment 'Elements found by the strings command in the end of the file.
  10 lines are efficient',
    proposition   varchar(255) null comment 'The proposed result for the researched file'
  );

COMMIT;
