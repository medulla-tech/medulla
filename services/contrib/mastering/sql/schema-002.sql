
--
--  (c) 2024-2026 Medulla, http://www.medulla-tech.io
--
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/>.

USE mastering;

START TRANSACTION;

drop table if exists `actions`;
CREATE TABLE `actions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` varchar(50) DEFAULT '' COMMENT 'if only server_id is specified means the action is an action by default',
  `entity_id` int(11) DEFAULT -1,
  `gid` varchar(30) DEFAULT '' COMMENT 'The group gid. If empty, the machine is not member of a group',
  `uuid` varchar(50) DEFAULT '' COMMENT 'The Machine uuid',
  `target` varchar(255) DEFAULT '',
  `name` varchar(50) NOT NULL,
  `config` text DEFAULT '',
  `content` text DEFAULT '' COMMENT 'Store the action to do as json',
  `status` varchar(50) DEFAULT 'TODO',
  `date_creation` datetime DEFAULT current_timestamp(),
  `date_start` datetime DEFAULT current_timestamp(),
  `date_end` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
);


drop table if exists servers;
CREATE TABLE if not exists `servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) NOT NULL,
  `jid` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

drop table if exists `masters`;
CREATE TABLE if not exists `masters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL DEFAULT '',
  `description` varchar(255) DEFAULT NULL,
  `uuid` varchar(50) NOT NULL,
  `path` varchar(255) NOT NULL,
  `size` bigint(20) DEFAULT 0,
  `os` varchar(100) DEFAULT '',
  `os_type` varchar(50) DEFAULT '',
  `creation_date` datetime DEFAULT current_timestamp(),
  `modification_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
);

drop table if exists `mastersEntities`;
CREATE TABLE if not exists `mastersEntities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `master_id` int(11) NOT NULL,
  `entity_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
);


DROP TABLE IF EXISTS `results`;
CREATE TABLE if not exists`results` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_id` int(11) NOT NULL,
  `session_id` varchar(30) DEFAULT '' COMMENT 'Use this sessionid to find xmpp related logs and actions',
  `uuid` varchar(50) DEFAULT '',
  `content` varchar(255) DEFAULT '',
  `creation_date` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `scripts`;
CREATE TABLE if not exists`scripts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` varchar(50) default "",
  `name` varchar(50) NOT NULL,
  `content` text DEFAULT '',
  `creation_date` datetime DEFAULT current_timestamp(),
  `modification_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
);

DROP TABLE IF EXISTS `scriptsEntities`;
CREATE TABLE if not exists `scriptsEntities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_script` int(11) NOT NULL,
  `id_entity` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
);

drop table if exists `actionStatus`;
create table if not exists actionStatus(
    id int auto_increment primary key,
    action_id int not null,
    uuid varchar(255) not null,
    status varchar(50) not null,
    creation_date datetime not null default NOW()
);

UPDATE version SET Number = 2;
COMMIT;
