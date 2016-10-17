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
-- MySQL dump 10.13  Distrib 5.5.47, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: xmppmaster
-- ------------------------------------------------------
-- Server version	5.5.47-0+deb7u1



CREATE DATABASE  IF NOT EXISTS `xmppmaster` /*!40100 DEFAULT CHARACTER SET latin1 */;
USE `xmppmaster`;
-- MySQL dump 10.13  Distrib 5.6.28, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: xmppmaster
-- ------------------------------------------------------
-- Server version       5.5.47-0+deb7u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
                                                                                                                                                                                                                                                                               
--                                                                                                                                                                                                                                                                             
-- Table structure for table `has_machinesusers`                                                                                                                                                                                                                               
--                                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                               
DROP TABLE IF EXISTS `has_machinesusers`;                                                                                                                                                                                                                                      
/*!40101 SET @saved_cs_client     = @@character_set_client */;                                                                                                                                                                                                                 
/*!40101 SET character_set_client = utf8 */;                                                                                                                                                                                                                                   
CREATE TABLE `has_machinesusers` (                                                                                                                                                                                                                                             
  `users_id` int(11) NOT NULL,                                                                                                                                                                                                                                                 
  `machines_id` int(11) NOT NULL,                                                                                                                                                                                                                                              
  PRIMARY KEY (`users_id`,`machines_id`)                                                                                                                                                                                                                                       
) ENGINE=InnoDB DEFAULT CHARSET=utf8;                                                                                                                                                                                                                                          
/*!40101 SET character_set_client = @saved_cs_client */;                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                               
--                                                                                                                                                                                                                                                                             
-- Table structure for table `has_relayserverregles`                                                                                                                                                                                                                          
--                                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                               
DROP TABLE IF EXISTS `has_relayserverregles`;                                                                                                                                                                                                                                 
/*!40101 SET @saved_cs_client     = @@character_set_client */;                                                                                                                                                                                                                 
/*!40101 SET character_set_client = utf8 */;                                                                                                                                                                                                                                   
CREATE TABLE `has_relayserverregles` (                                                                                                                                                                                                                                        
  `regles_id` int(11) NOT NULL,                                                                                                                                                                                                                                                
  `order` varchar(45) NOT NULL DEFAULT '0',                                                                                                                                                                                                                                    
  `sujet` varchar(45) NOT NULL,
  `relayserver_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `machines`
--

DROP TABLE IF EXISTS `machines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jid` varchar(45) NOT NULL,
  `plateform` varchar(60) NOT NULL,
  `archi` varchar(45) DEFAULT NULL,
  `hostname` varchar(45) NOT NULL,
  `uuid_inventorymachine` varchar(45) DEFAULT NULL,
  `ip_xmpp` varchar(45) NOT NULL,
  `macadress` varchar(45) DEFAULT NULL,
  `subnetxmpp` varchar(45) DEFAULT NULL,
  `agenttype` varchar(20) CHARACTER SET big5 DEFAULT NULL,
  `classutil` varchar(10) NOT NULL DEFAULT 'private',
  `groupedeploy` VARCHAR(80) DEFAULT NULL,
  `urlguacamole` VARCHAR(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `jid_UNIQUE` (`jid`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `network`
--

DROP TABLE IF EXISTS `network`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `network` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `macadress` varchar(45) DEFAULT NULL,
  `ipadress` varchar(45) DEFAULT NULL,
  `broadcast` varchar(45) DEFAULT NULL,
  `gateway` varchar(45) DEFAULT NULL,
  `mask` varchar(45) DEFAULT NULL,
  `mac` varchar(45) DEFAULT NULL,
  `machines_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `regles`
--

DROP TABLE IF EXISTS `regles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `regles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `description` varchar(45) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regles`
--

LOCK TABLES `regles` WRITE;
INSERT INTO `regles` VALUES (1,'user','impose relais server pour user',1),
(2,'hostname','asocie a hostname has a relay server',2),
(3,'geoposition','selectionne relais meilleur position',3),
(4,'subnet','selectionne relais server meme subnet',4),
(5,'default','selectionne relais par defaut ',5);
UNLOCK TABLES;


--
-- Table structure for table `relayserver`
--

DROP TABLE IF EXISTS `relayserver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relayserver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `urlguacamole` varchar(80) NOT NULL,
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
  `actif` tinyint(1) DEFAULT '0',
  `classutil` varchar(10) NOT NULL DEFAULT 'public',
  `groupedeploy` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `userlog`
--

DROP TABLE IF EXISTS `userlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `userlog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `msg` text NOT NULL,
  `type` varchar(45) NOT NULL DEFAULT 'info',
  `datelog` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
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
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `has_guacamole`
--

DROP TABLE IF EXISTS `has_guacamole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `has_guacamole` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `idguacamole` int(11) NOT NULL,
  `idinventory` int(11) NOT NULL,
  `protocole` varchar(10) NOT NULL,
  PRIMARY KEY (`id`,`idguacamole`,`idinventory`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `version`
--

DROP TABLE IF EXISTS `version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'xmppmaster'
--

--
-- Dumping routines for database 'xmppmaster'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-05-03 12:23:52

LOCK TABLES `version` WRITE;
/*!40000 ALTER TABLE `version` DISABLE KEYS */;
INSERT INTO `version` VALUES (1);
/*!40000 ALTER TABLE `version` ENABLE KEYS */;
UNLOCK TABLES;


GRANT ALL PRIVILEGES ON `xmppmaster`.*  TO 'mmc'@'localhost' ;














































