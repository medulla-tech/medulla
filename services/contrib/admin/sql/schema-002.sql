--
-- (c) 2022 Siveo, http://www.siveo.net/
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


START TRANSACTION;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
--
-- Table structure for table `upd_list`
--

DROP TABLE IF EXISTS `upd_list`;
CREATE TABLE `upd_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `list_name` varchar(90) NOT NULL,
  `comment` varchar(255) DEFAULT NULL,
  `priority` int(11) DEFAULT 10 COMMENT 'The list with the highest priority is applied last\n',
  `action` varchar(45) DEFAULT 'admin' COMMENT 'action : admin, exclude, include\n',
  `deleted` int(11) DEFAULT 0 COMMENT 'Three lists cannot be deleted:\nAdmin List, Blacklist and Whitelist.\n\n',
  PRIMARY KEY (`id`),
  KEY `id_unique` (`list_name`),
  KEY `idx_list_name` (`list_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
--
-- Dumping data for table `upd_list`
--

LOCK TABLES `upd_list` WRITE;
    INSERT INTO `upd_list` VALUES (1,'white_list','The Whitelist, is the list of packages allowed to be installed',2,'include',0),(2,'black_list','The Blacklist, is the list of packages not allowed to be installed',1,'exclude',0),(3,'grey_list','The Greylist, is the list of the packages for which we need to take a look',3,'exclude',0);
UNLOCK TABLES;

--
-- Table structure for table `upd_method`
--

DROP TABLE IF EXISTS `upd_method`;
CREATE TABLE `upd_method` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `method` varchar(45) NOT NULL,
  `transfert_method` varchar(45) DEFAULT 'pull curl cdn',
  `nb_remise` int(11) DEFAULT 3,
  `delta_time` int(11) DEFAULT 3600,
  `comment` varchar(45) DEFAULT NULL,
  `msg_method` text DEFAULT '{}',
  PRIMARY KEY (`id`),
  UNIQUE KEY `method_UNIQUE` (`method`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
--
-- Dumping data for table `upd_method`
--

LOCK TABLES `upd_method` WRITE;
INSERT INTO `upd_method` VALUES (1,'interactif','pull curl cdn',3,45,'Delay 3 time the update','{\n    \"messagelist\": {\n        \"1\": \"Accept or deny the update\", \n        \"3\": \"The update will start in 5 minutes. Please save your work.\", \n        \"2\": \"Accept the second update\", \n        \"warning\": \"Please save your work\"\n    }\n}\n'),(2,'direct','pull curl cdn',0,0,'Update without user interaction.','{}'),(3,'conditionnel','pull curl cdn',3,45,'Delay the install 3 times if the user is connected. If not, we install','{\n    \"messagelist\": {\n        \"1\": \"Accept or deny the update\", \n        \"3\": \"The update will start in 5 minutes. Please save your work.\", \n        \"2\": \"Accept the second update\", \n        \"warning\": \"Please save your work\"\n    }\n}\n'),(4,'no_process','pull curl cdn',0,0,'Do not install','{ }');
UNLOCK TABLES;

--
-- Table structure for table `upd_package`
--

DROP TABLE IF EXISTS `upd_package`;
CREATE TABLE `upd_package` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package` varchar(100) NOT NULL,
  `version` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT 'secutity',
  `platform` varchar(45) NOT NULL,
  `cmd_before` varchar(512) DEFAULT NULL,
  `cmd_after` varchar(512) DEFAULT NULL,
  `script` text DEFAULT NULL,
  `comment` varchar(45) DEFAULT NULL,
  `url_info` varchar(512) DEFAULT NULL,
  `creation_date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_name_package` (`package`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `upd_package`
--

LOCK TABLES `upd_package` WRITE;
UNLOCK TABLES;

--
-- Table structure for table `upd_package_unknown`
--

DROP TABLE IF EXISTS `upd_package_unknown`;
CREATE TABLE `upd_package_unknown` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `jid` varchar(45) DEFAULT NULL,
  `platform` varchar(45) DEFAULT NULL,
  `reception_date` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
--
-- Dumping data for table `upd_package_unknown`
--

LOCK TABLES `upd_package_unknown` WRITE;
UNLOCK TABLES;


--
-- Table structure for table `upd_list_package`
--

DROP TABLE IF EXISTS `upd_list_package`;
CREATE TABLE `upd_list_package` (
  `package_id` int(11) NOT NULL,
  `list_id` int(11) NOT NULL,
  `method_id` int(11) NOT NULL,
  `actif` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`package_id`,`list_id`,`method_id`),
  KEY `fk_pack` (`package_id`),
  KEY `fk_list` (`list_id`),
  KEY `fk_methode` (`method_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
--
-- Dumping data for table `upd_list_package`
--

LOCK TABLES `upd_list_package` WRITE;
UNLOCK TABLES;



--
-- Table structure for table `upd_msg_send`
--

DROP TABLE IF EXISTS `upd_msg_send`;
CREATE TABLE `upd_msg_send` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  `jid` varchar(255) NOT NULL,
  `json_msg` text NOT NULL,
  `ars` varchar(255) DEFAULT NULL COMMENT 'ars\n',
  `session_id` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `upd_msg_send`
--

LOCK TABLES `upd_msg_send` WRITE;
UNLOCK TABLES;
--
-- Table structure for table `upd_rules`
--

DROP TABLE IF EXISTS `upd_rules`;
CREATE TABLE `upd_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `package_id` int(11) NOT NULL,
  `method_id` int(11) NOT NULL,
  `jid` varchar(255) DEFAULT NULL,
  `name` varchar(90) DEFAULT NULL,
  `software_exist` varchar(255) DEFAULT NULL,
  `software_no_exist` varchar(255) DEFAULT NULL,
  `list_list` varchar(512) DEFAULT '0',
  `include_exclude` int(11) NOT NULL DEFAULT 1 COMMENT 'include or exclude\n',
  `actif` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `pack_id` (`package_id`),
  KEY `method_id` (`method_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `upd_rules`
--

LOCK TABLES `upd_rules` WRITE;
-- insert
UNLOCK TABLES;

--
-- Dumping data for table `version`
--

UPDATE version SET Number = 2;

COMMIT;
