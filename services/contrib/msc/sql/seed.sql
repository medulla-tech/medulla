-- MySQL dump 10.9
--
-- Host: localhost    Database: msc
-- ------------------------------------------------------
-- Server version   4.1.11-Debian_4sarge7-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `commands`
--

DROP TABLE IF EXISTS `commands`;
CREATE TABLE `commands` (
  `id_command` int(11) NOT NULL auto_increment,
  `date_created` datetime default NULL,
  `start_file` tinytext,
  `parameters` text,
  `path_destination` text,
  `path_source` text,
  `create_directory` enum('enable','disable') default 'enable',
  `start_script` enum('enable','disable') default 'enable',
  `delete_file_after_execute_successful` enum('enable','disable') default 'enable',
  `files` mediumtext,
  `start_date` datetime default NULL,
  `end_date` datetime default NULL,
  `username` varchar(255) default '',
  `webmin_username` varchar(255) default '',
  `dispatched` enum('YES','NO') default 'NO',
  `title` varchar(255) default '',
  `start_inventory` enum('enable','disable') default 'disable',
  `wake_on_lan` enum('enable','disable') default 'disable',
  `next_connection_delay` int(11) default '60',
  `max_connection_attempt` int(11) default '3',
  `repeat` int(11) default '0',
  `scheduler` varchar(255) default NULL,
  `pre_command_hook` tinytext,
  `post_command_hook` tinytext,
  `pre_run_hook` tinytext,
  `post_run_hook` tinytext,
  `on_success_hook` tinytext,
  `on_failure_hook` tinytext,
  PRIMARY KEY  (`id_command`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `commands`
--


/*!40000 ALTER TABLE `commands` DISABLE KEYS */;
LOCK TABLES `commands` WRITE;
INSERT INTO `commands` VALUES
(1,'2008-01-01 02:03:04','echo','','','','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','No-computer task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(2,'2008-01-01 02:03:04','echo','','','','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','Mono-computer task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(3,'2008-01-01 02:03:04','cat /cygdrive/c/boot.ini; cat /cygdrive/c/boot.ini 2>&1','0000-00-00 00:00:00','0000-00-00 00:00:00','0000-00-00 00:00:00','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','Multi-computer task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(4,'2008-01-01 02:03:04','sleep 5','','','','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','A sleep task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(5,'2008-01-01 02:03:04','./install.bat','','/tmp','/Exemples/Firefox','enable','enable','enable','install.bat\ndata','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','A true deployment task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(6,'2008-01-01 02:03:04','echo','','','','enable','enable','enable','','2000-01-01 01:02:03','0000-00-00 00:00:00','root','root','YES','A really old task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(7,'2007-12-21 16:34:31','echo','','','','enable','enable','enable','','2099-01-01 01:02:03','0000-00-00 00:00:00','root','root','YES','A really new task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(8,'2007-12-21 16:34:31','echo','','','','enable','enable','enable','','2099-01-01 01:02:03','2000-01-01 01:02:03','root','root','YES','A task who will never be run','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(9,'2007-12-21 16:34:31','echo','','','','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','A expired task','disable','disable',60,0,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(10,'2007-12-21 16:34:31','echo','','','','enable','enable','enable','','2000-01-01 01:02:03','2099-01-01 01:02:03','root','root','YES','A regular task','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(11,'2007-12-21 16:34:31','a_non_existent_command','','','','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','This task will never work','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(12,'2007-12-21 16:34:31','true','','','','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','This task will always succeed','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(13,'2007-12-21 16:34:31','false','','','','enable','enable','enable','','0000-00-00 00:00:00','0000-00-00 00:00:00','root','root','YES','This task will always fail','disable','disable',60,3,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL);
UNLOCK TABLES;
/*!40000 ALTER TABLE `commands` ENABLE KEYS */;

--
-- Table structure for table `commands_history`
--

DROP TABLE IF EXISTS `commands_history`;
CREATE TABLE `commands_history` (
  `id_command_history` int(11) NOT NULL auto_increment,
  `id_command_on_host` int(11) NOT NULL default '0',
  `date` tinytext,
  `stderr` longtext,
  `stdout` longtext,
  `error_code` int(11) default '0',
  `state` enum('upload_in_progress','upload_done','upload_failed','execution_in_progress','execution_done','execution_failed','delete_in_progress','delete_done','delete_failed','inventory_in_progress','inventory_failed','inventory_done','not_reachable','done','pause','stop','scheduled','failed') default NULL,
  PRIMARY KEY  (`id_command_history`),
  KEY `id_command_on_host` (`id_command_on_host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `commands_history`
--


/*!40000 ALTER TABLE `commands_history` DISABLE KEYS */;
LOCK TABLES `commands_history` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `commands_history` ENABLE KEYS */;

--
-- Table structure for table `commands_on_host`
--

DROP TABLE IF EXISTS `commands_on_host`;
CREATE TABLE `commands_on_host` (
  `id_command_on_host` int(11) NOT NULL auto_increment,
  `id_command` int(11) NOT NULL default '0',
  `host` tinytext,
  `start_date` datetime default NULL,
  `end_date` datetime default NULL,
  `current_state` enum('upload_in_progress','upload_done','upload_failed','execution_in_progress','execution_done','execution_failed','delete_in_progress','delete_done','delete_failed','inventory_in_progress','inventory_failed','inventory_done','not_reachable','done','pause','stop','scheduled','failed') default NULL,
  `uploaded` enum('TODO','IGNORED','DONE','FAILED','WORK_IN_PROGRESS') default NULL,
  `executed` enum('TODO','IGNORED','DONE','FAILED','WORK_IN_PROGRESS') default NULL,
  `deleted` enum('TODO','IGNORED','DONE','FAILED','WORK_IN_PROGRESS') default NULL,
  `next_launch_date` datetime default NULL,
  `current_pid` int(11) default '0',
  `number_attempt_connection_remains` int(11) default '0',
  `next_attempt_date_time` bigint(20) default '0',
  `current_launcher` varchar(255) default NULL,
  PRIMARY KEY  (`id_command_on_host`),
  KEY `id_command` (`id_command`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `commands_on_host`
--


/*!40000 ALTER TABLE `commands_on_host` DISABLE KEYS */;
LOCK TABLES `commands_on_host` WRITE;
INSERT INTO `commands_on_host` VALUES (1,2,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL),(2,3,'127.0.0.1','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL),(3,3,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL),(4,4,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL),(5,5,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL),(6,6,'MERRE-00282','2000-01-01 01:02:03','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','2000-01-01 01:02:03',-1,3,60,NULL),(7,7,'MERRE-00282','2099-01-01 01:02:03','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','2099-01-01 01:02:03',-1,3,60,NULL),(8,8,'MERRE-00282','2099-01-01 01:02:03','2000-01-01 01:02:03','scheduled','TODO','TODO','TODO','2099-01-01 01:02:03',-1,3,60,NULL),(9,9,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,0,60,NULL),(10,10,'MERRE-00282','2000-01-01 01:02:03','2099-01-01 01:02:03','scheduled','TODO','TODO','TODO','2000-01-01 01:02:03',-1,3,60,NULL),(11,11,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL),(12,12,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL),(13,13,'MERRE-00282','0000-00-00 00:00:00','0000-00-00 00:00:00','scheduled','TODO','TODO','TODO','0000-00-00 00:00:00',-1,3,60,NULL);
UNLOCK TABLES;
/*!40000 ALTER TABLE `commands_on_host` ENABLE KEYS */;

--
-- Table structure for table `target`
--

DROP TABLE IF EXISTS `target`;
CREATE TABLE `target` (
  `id` int(11) NOT NULL auto_increment,
  `id_command` int(11) NOT NULL default '0',
  `id_command_on_host` int(11) default NULL,
  `target_name` text NOT NULL,
  `mirrors` text,
  `scheduler` text,
  `id_group` text,
  PRIMARY KEY  (`id`),
  KEY `cmd_ind` (`id_command`),
  KEY `coh_ind` (`id_command_on_host`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `target`
--


/*!40000 ALTER TABLE `target` DISABLE KEYS */;
LOCK TABLES `target` WRITE;
INSERT INTO `target` VALUES (1,1,1,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(2,3,2,'127.0.0.1','192.168.0.32||192.168.0.32','',''),(3,3,3,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(4,4,4,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(5,5,5,'MERRE-00282','file:///tftpboot/revoboot/msc','',''),(6,6,6,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(7,7,7,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(8,8,8,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(9,9,9,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(10,10,10,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(11,11,11,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(12,12,12,'MERRE-00282','192.168.0.32||192.168.0.32','',''),(13,13,13,'MERRE-00282','192.168.0.32||192.168.0.32','','');
UNLOCK TABLES;
/*!40000 ALTER TABLE `target` ENABLE KEYS */;

--
-- Table structure for table `version`
--

DROP TABLE IF EXISTS `version`;
CREATE TABLE `version` (
  `Number` tinyint(4) unsigned NOT NULL default '0'
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `version`
--


/*!40000 ALTER TABLE `version` DISABLE KEYS */;
LOCK TABLES `version` WRITE;
INSERT INTO `version` VALUES (4);
UNLOCK TABLES;
/*!40000 ALTER TABLE `version` ENABLE KEYS */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

