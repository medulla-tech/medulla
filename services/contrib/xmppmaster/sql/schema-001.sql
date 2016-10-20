--
-- (c) 2016 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://www.siveo.net/
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



CREATE DATABASE  IF NOT EXISTS `xmppmaster` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `xmppmaster`;

--
-- Table structure for table `has_machinesusers`
--

DROP TABLE IF EXISTS `has_machinesusers`;
CREATE TABLE `has_machinesusers` (
  `users_id` int(11) NOT NULL,
  `machines_id` int(11) NOT NULL,
  PRIMARY KEY (`users_id`,`machines_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `has_relayserverrules`
--

DROP TABLE IF EXISTS `has_relayserverrules`;
CREATE TABLE `has_relayserverrules` (
  `rules_id` int(11) NOT NULL,
  `order` varchar(45) NOT NULL DEFAULT '0',
  `subject` varchar(45) NOT NULL,
  `relayserver_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `machines`
--

DROP TABLE IF EXISTS `machines`;
CREATE TABLE `machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jid` varchar(45) NOT NULL,
  `platform` varchar(60) NOT NULL,
  `archi` varchar(45) DEFAULT NULL,
  `hostname` varchar(45) NOT NULL,
  `uuid_inventorymachine` varchar(45) DEFAULT NULL,
  `ip_xmpp` varchar(45) NOT NULL,
  `macaddress` varchar(45) DEFAULT NULL,
  `subnetxmpp` varchar(45) DEFAULT NULL,
  `agenttype` varchar(20) CHARACTER SET big5 DEFAULT NULL,
  `classutil` varchar(10) NOT NULL DEFAULT 'private',
  `groupdeploy` VARCHAR(80) DEFAULT NULL,
  `urlguacamole` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `jid_UNIQUE` (`jid`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;

--
-- Table structure for table `network`
--

DROP TABLE IF EXISTS `network`;
CREATE TABLE `network` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `macaddress` varchar(45) DEFAULT NULL,
  `ipaddress` varchar(45) DEFAULT NULL,
  `broadcast` varchar(45) DEFAULT NULL,
  `gateway` varchar(45) DEFAULT NULL,
  `mask` varchar(45) DEFAULT NULL,
  `mac` varchar(45) DEFAULT NULL,
  `machines_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8;

--
-- Table structure for table `rules`
--

DROP TABLE IF EXISTS `rules`;
CREATE TABLE `rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(45) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `rules`
--

LOCK TABLES `rules` WRITE;
INSERT INTO `rules` VALUES (1,'user','Associate relay server based on user',1),
(2,'hostname','Associate relay server based on hostname',2),
(3,'geoposition','Select relay server based on best location',3),
(4,'subnet','Select relay server in same subnet',4),
(5,'default','Use default relay server',5);
UNLOCK TABLES;


--
-- Table structure for table `relayserver`
--

DROP TABLE IF EXISTS `relayserver`;
CREATE TABLE `relayserver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `urlguacamole` varchar(255) NOT NULL,
  `subnet` varchar(45) NOT NULL,
  `nameserver` varchar(45) NOT NULL,
  `ipserver` varchar(45) NOT NULL,
  `ipconnection` varchar(45) NOT NULL,
  `port` int(11) NOT NULL,
  `portconnection` int(11) NOT NULL,
  `mask` varchar(45) NOT NULL,
  `jid` varchar(45) NOT NULL,
  `longitude` varchar(45) DEFAULT NULL,
  `latitude` varchar(45) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT '0',
  `classutil` varchar(10) NOT NULL DEFAULT 'public',
  `groupdeploy` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

--
-- Table structure for table `userlog`
--

DROP TABLE IF EXISTS `userlog`;
CREATE TABLE `userlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `msg` text NOT NULL,
  `type` varchar(45) NOT NULL DEFAULT 'info',
  `datelog` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `namesession` varchar(45) NOT NULL,
  `hostname` varchar(45) NOT NULL,
  `city` varchar(45) DEFAULT '',
  `region_name` varchar(45) DEFAULT '',
  `time_zone` varchar(45) DEFAULT '',
  `longitude` varchar(45) DEFAULT '',
  `latitude` varchar(45) DEFAULT '',
  `postal_code` varchar(45) DEFAULT '',
  `country_code` varchar(45) DEFAULT '',
  `country_name` varchar(45) DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

--
-- Table structure for table `has_guacamole`
--

DROP TABLE IF EXISTS `has_guacamole`;
CREATE TABLE `has_guacamole` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idguacamole` int(11) NOT NULL,
  `idinventory` int(11) NOT NULL,
  `protocol` varchar(10) NOT NULL,
  PRIMARY KEY (`id`,`idguacamole`,`idinventory`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;

--
-- Table structure for table `version`
--

DROP TABLE IF EXISTS `version`;
CREATE TABLE `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


LOCK TABLES `version` WRITE;
INSERT INTO `version` VALUES (1);
UNLOCK TABLES;


GRANT ALL PRIVILEGES ON `xmppmaster`.*  TO 'mmc'@'localhost' ;
