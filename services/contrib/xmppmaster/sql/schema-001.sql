--
-- (c) 2016 Mandriva, http://www.siveo.net/
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
-- Dumping data for table `has_machinesusers`
--

LOCK TABLES `has_machinesusers` WRITE;
/*!40000 ALTER TABLE `has_machinesusers` DISABLE KEYS */;
/*!40000 ALTER TABLE `has_machinesusers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `has_relaisserverregles`
--

DROP TABLE IF EXISTS `has_relaisserverregles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `has_relaisserverregles` (
  `regles_id` int(11) NOT NULL,
  `order` varchar(45) NOT NULL DEFAULT '0',
  `sujet` varchar(45) NOT NULL,
  `relaisserver_id` int(11) NOT NULL,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `has_relaisserverregles`
--

LOCK TABLES `has_relaisserverregles` WRITE;
/*!40000 ALTER TABLE `has_relaisserverregles` DISABLE KEYS */;
/*!40000 ALTER TABLE `has_relaisserverregles` ENABLE KEYS */;
UNLOCK TABLES;

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
  `classutil` varchar(10) NOT NULL DEFAULT 'both',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `jid_UNIQUE` (`jid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machines`
--

LOCK TABLES `machines` WRITE;
/*!40000 ALTER TABLE `machines` DISABLE KEYS */;
/*!40000 ALTER TABLE `machines` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `network`
--

LOCK TABLES `network` WRITE;
/*!40000 ALTER TABLE `network` DISABLE KEYS */;
/*!40000 ALTER TABLE `network` ENABLE KEYS */;
UNLOCK TABLES;

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
/*!40000 ALTER TABLE `regles` DISABLE KEYS */;
INSERT INTO `regles` VALUES (1,'user','impose relais server pour user',1),(2,'hostname','impose relais serveur pour hostname',2),(3,'subnet','selectionne relais server meme subnet',4),(4,'default','selectionne relais par defaut ',5),(5,'geoposition','selectionne relais meilleur position',3);
/*!40000 ALTER TABLE `regles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary table structure for view `relais_server_actif_private`
--

DROP TABLE IF EXISTS `relais_server_actif_private`;
/*!50001 DROP VIEW IF EXISTS `relais_server_actif_private`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `relais_server_actif_private` (
  `id` tinyint NOT NULL,
  `urlguacamole` tinyint NOT NULL,
  `subnet` tinyint NOT NULL,
  `nameserver` tinyint NOT NULL,
  `ipserver` tinyint NOT NULL,
  `mask` tinyint NOT NULL,
  `jid` tinyint NOT NULL,
  `longitude` tinyint NOT NULL,
  `latitude` tinyint NOT NULL,
  `actif` tinyint NOT NULL,
  `classutil` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `relaisserver`
--

DROP TABLE IF EXISTS `relaisserver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `relaisserver` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `urlguacamole` varchar(80) DEFAULT NULL,
  `subnet` varchar(45) NOT NULL,
  `nameserver` varchar(45) NOT NULL,
  `ipserver` varchar(45) NOT NULL,
  `mask` varchar(45) NOT NULL,
  `jid` varchar(45) NOT NULL,
  `longitude` varchar(45) DEFAULT NULL,
  `latitude` varchar(45) DEFAULT NULL,
  `actif` tinyint(1) DEFAULT '0',
  `classutil` varchar(10) NOT NULL DEFAULT 'public',
  `port` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `relaisserver`
--



--
-- Temporary table structure for view `relaisservergeo`
--

DROP TABLE IF EXISTS `relaisservergeo`;
/*!50001 DROP VIEW IF EXISTS `relaisservergeo`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE TABLE `relaisservergeo` (
  `id` tinyint NOT NULL,
  `urlguacamole` tinyint NOT NULL,
  `subnet` tinyint NOT NULL,
  `nameserver` tinyint NOT NULL,
  `ipserver` tinyint NOT NULL,
  `mask` tinyint NOT NULL,
  `jid` tinyint NOT NULL,
  `longitude` tinyint NOT NULL,
  `latitude` tinyint NOT NULL,
  `actif` tinyint NOT NULL,
  `classutil` tinyint NOT NULL
) ENGINE=MyISAM */;
SET character_set_client = @saved_cs_client;

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
) ENGINE=InnoDB AUTO_INCREMENT=156 DEFAULT CHARSET=latin1;
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
-- Dumping data for table `version`
--

LOCK TABLES `version` WRITE;
/*!40000 ALTER TABLE `version` DISABLE KEYS */;
INSERT INTO `version` VALUES (1);
/*!40000 ALTER TABLE `version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Final view structure for view `relais_server_actif_private`
--

/*!50001 DROP TABLE IF EXISTS `relais_server_actif_private`*/;
/*!50001 DROP VIEW IF EXISTS `relais_server_actif_private`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `relais_server_actif_private` AS select `relaisserver`.`id` AS `id`,`relaisserver`.`urlguacamole` AS `urlguacamole`,`relaisserver`.`subnet` AS `subnet`,`relaisserver`.`nameserver` AS `nameserver`,`relaisserver`.`ipserver` AS `ipserver`,`relaisserver`.`mask` AS `mask`,`relaisserver`.`jid` AS `jid`,`relaisserver`.`longitude` AS `longitude`,`relaisserver`.`latitude` AS `latitude`,`relaisserver`.`actif` AS `actif`,`relaisserver`.`classutil` AS `classutil` from `relaisserver` where ((`relaisserver`.`classutil` = 'private') and (`relaisserver`.`actif` = 1)) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `relaisservergeo`
--

/*!50001 DROP TABLE IF EXISTS `relaisservergeo`*/;
/*!50001 DROP VIEW IF EXISTS `relaisservergeo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `relaisservergeo` AS select `relaisserver`.`id` AS `id`,`relaisserver`.`urlguacamole` AS `urlguacamole`,`relaisserver`.`subnet` AS `subnet`,`relaisserver`.`nameserver` AS `nameserver`,`relaisserver`.`ipserver` AS `ipserver`,`relaisserver`.`mask` AS `mask`,`relaisserver`.`jid` AS `jid`,`relaisserver`.`longitude` AS `longitude`,`relaisserver`.`latitude` AS `latitude`,`relaisserver`.`actif` AS `actif`,`relaisserver`.`classutil` AS `classutil` from `relaisserver` where ((`relaisserver`.`longitude` <> '') and (`relaisserver`.`latitude` <> '')) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-04-28  8:23:29



GRANT ALL PRIVILEGES ON `xmppmaster`.*  TO 'mmc'@'localhost' ;