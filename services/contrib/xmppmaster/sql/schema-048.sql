--
-- (c) 2020 Siveo, http://www.siveo.net/
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

USE `xmppmaster`;
--
-- Table structure for table `mon_machine`
--

DROP TABLE IF EXISTS `mon_machine`;

 CREATE TABLE `mon_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `machines_id` int(11) NOT NULL,
  `date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `hostname` varchar(255) NOT NULL,
  `statusmsg` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'statusmsg JSON reprend la liste de toutes les alerts et message des devices.\n[  {"device" : "machine" ,\n           "status" : "ready",\n            "msg" : "msgalert"},\n     {"device" : "hermalPrinter", \n	    "status":"error",\n	     "msgalert" :""}\n]',
  PRIMARY KEY (`id`),
  KEY `fk_Monitoring_machine_machines_idx` (`machines_id`),
  CONSTRAINT `fk_Monitoring_machine_machines` FOREIGN KEY (`machines_id`) REFERENCES `machines` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=145 DEFAULT CHARSET=utf8 COMMENT='"system" : {\n            "cpu"       : "18%",\n            "memory"    : "45%",\n            "storage1"  : "65%",  \n            "storage2"  : "43%",\n            "cpuTemp"   : "40",\n            "mbTemp"    : "35",\n            "cpuFan"    : "1250",\n            "status" : "warning", // "ready", "warning", "error"     \n            "alarms"   : ["ALARM_INTRUSION","ALARM_TEMP_CPU","ALARM_TEMP_MAINBOARD", "..."],\n            "counters"  : {\n                "intrusions"    : "nnn"\n            },\n            "average"  : {\n                "cpuTemp"    : "nnn",\n                "mbTemp"     : "nnn",   \n                "cpuFan"     : "nnn",\n                "memory"     : "nnn"\n            },\n            "maximum"  : {\n                "cpuTemp"    : "nnn",\n                "mbTemp"     : "nnn",   \n                "cpuFan"     : "nnn",\n                "memory"     : "nnn",\n            }\n\n        }, ' ;

--
-- Table structure for table `mon_devices`
--

DROP TABLE IF EXISTS `mon_devices`;

CREATE TABLE `mon_devices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mon_machine_id` int(11) NOT NULL,
  `device_type` enum('thermalprinter','nfcReader','opticalReader','cpu','memory','storage','network','system') NOT NULL DEFAULT 'opticalReader',
  `serial` varchar(255) DEFAULT NULL COMMENT 'le num serial  peut etre null mais si definie il doit etre unique',
  `firmware` varchar(10) DEFAULT NULL COMMENT 'version du firmware  "2.45"\n',
  `status` enum('ready','busy','warning','error','disable') DEFAULT 'disable' COMMENT 'status du peripherique\\\\n"status" domaine  "ready", "busy", "warning", "error"      ',
  `alarm_msg` varchar(255) DEFAULT NULL COMMENT '     "message"  chaine adapter au status  ["HOOD_OPEN","NO_PAPER", "NO_DEVICE", "..."],',
  `doc` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  PRIMARY KEY (`id`),
  KEY `fk_mon_reader_mon_machine1_idx` (`mon_machine_id`),
  CONSTRAINT `fk_mon_reader_mon_machine1` FOREIGN KEY (`mon_machine_id`) REFERENCES `mon_machine` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=241 DEFAULT CHARSET=utf8 COMMENT='Monitoring reader\nCette table definie les parametres d''un reader\n\n "serial" : "IMA3C08298",\n            "firmware"  : "2.45",\n            "status" : "error", // "ready", "busy", "warning", "error"      \n            "message"   : ["HOOD_OPEN","NO_PAPER", "NO_DEVICE", "..."],\n            "counters"  : {\n                "receipts"      : "nnn",\n                "noPaper"       : "nnn",\n                "hoodOpen"      : "nnn",\n                "initErrors"    : "nnn",\n                "printErrors"   : "nnn",\n                "cutErrors"     : "nnn",\n                "loadingFaults" : "nnn",\n                "comErrors"     : "nnn"\n\n';

--
-- Table structure for table `mom_event`
--

DROP TABLE IF EXISTS `mom_event`;
 CREATE TABLE `mon_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_event` int(11) DEFAULT '1',
  `type_event` varchar(255) DEFAULT NULL COMMENT 'recuperation du ',
  `cmd` varchar(255) DEFAULT NULL,
  `id_rule` int(11) NOT NULL,
  `machines_id` int(11) NOT NULL,
  `id_device` int(11) NOT NULL COMMENT 'permet de definir la defice ou le service conserner par cette action.',
  PRIMARY KEY (`id`),
  KEY `fk_mon_event_1_idx` (`machines_id`),
  CONSTRAINT `fk_mon_event_1` FOREIGN KEY (`machines_id`) REFERENCES `mon_machine` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

--
-- Table structure for table `mon_device_service`
--

DROP TABLE IF EXISTS `mon_device_service`;
CREATE TABLE `mon_device_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_type` varchar(255) DEFAULT NULL COMMENT 'definition du type de device ou de service.\\\\n',
  `enable` int(11) NOT NULL DEFAULT '1',
  `structure_json_controle` text NOT NULL COMMENT 'structure json permettant de presenter l''object pour definir les binding.',
  `html_form` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

--
-- Table structure for table `mon_rules`
--


DROP TABLE IF EXISTS `mon_rules`;
CREATE TABLE `mon_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) DEFAULT NULL COMMENT 'rattacher cette regle a 1 machine unique',
  `device_type` varchar(255) NOT NULL COMMENT 'Permet la selection des regle pour  device ou  service.\\\\\\\\n',
  `binding` text NOT NULL COMMENT 'binding permet de definir le code de la regle a appliquer sur  les infiormation remonter par le device ou service.\npermet de definir les actions par rapport au contrainte.\n',
  `succes_binding_cmd` text COMMENT 'commande a effectuer si binding test renvoi True\n',
  `no_success_binding_cmd` text COMMENT 'commande a effectuer si binding test renvoi False\n',
  `error_on_binding` text COMMENT 'commande a effectuer si binding test renvoi Error\n',
  `type_event` varchar(255) NOT NULL DEFAULT 'log' COMMENT 'permet de deinir evenement associe.\\\\n',
  `user` varchar(255) DEFAULT NULL COMMENT 'user definifant cette regle\\n',
  `comment` varchar(1024) DEFAULT NULL COMMENT 'permet de rappeler la consistance de cette regle\\n',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;


UPDATE version SET Number = 48;

COMMIT;
