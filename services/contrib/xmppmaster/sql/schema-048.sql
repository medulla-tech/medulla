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
  `statusmsg` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT 'statusmsg json lists all alerts and messages coming from the devices.\n[  {"device" : "machine" ,\n           "status" : "ready",\n            "msg" : "msgalert"},\n     {"device" : "thermalPrinter", \n	    "status":"error",\n	     "msgalert" :""}\n]',
  PRIMARY KEY (`id`),
  KEY `fk_Monitoring_machine_machines_idx` (`machines_id`),
  CONSTRAINT `fk_Monitoring_machine_machines` FOREIGN KEY (`machines_id`) REFERENCES `machines` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='"system" : {\n            "cpu"       : "18%",\n            "memory"    : "45%",\n            "storage1"  : "65%",  \n            "storage2"  : "43%",\n            "cpuTemp"   : "40",\n            "mbTemp"    : "35",\n            "cpuFan"    : "1250",\n            "status" : "warning"     \n            "alarms"   : "ALARM_INTRUSION",\n            "counters"  : {\n                "intrusions"    : "nnn"\n            },\n            "average"  : {\n                "cpuTemp"    : "nnn",\n                "mbTemp"     : "nnn",   \n                "cpuFan"     : "nnn",\n                "memory"     : "nnn"\n            },\n            "maximum"  : {\n                "cpuTemp"    : "nnn",\n                "mbTemp"     : "nnn",   \n                "cpuFan"     : "nnn",\n                "memory"     : "nnn",\n            }\n\n        }, ' ;

--
-- Table structure for table `mon_devices`
--

DROP TABLE IF EXISTS `mon_devices`;

CREATE TABLE `mon_devices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mon_machine_id` int(11) NOT NULL,
  `device_type` enum('thermalPrinter','nfcReader','opticalReader','cpu','memory','storage','network','system') NOT NULL,
  `serial` varchar(255) DEFAULT NULL COMMENT 'can be null, but if defined, it has to be unique',
  `firmware` varchar(10) DEFAULT NULL COMMENT 'firmware version eg. "2.45"\n',
  `status` enum('ready','busy','warning','error','disable') COMMENT 'device status eg. "ready", "busy", "warning", "error"      ',
  `alarm_msg` varchar(255) DEFAULT NULL COMMENT 'message giving more details on the status. eg. "HOOD_OPEN", "NO_PAPER", "NO_DEVICE", "..."',
  `doc` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  PRIMARY KEY (`id`),
  KEY `fk_mon_reader_mon_machine1_idx` (`mon_machine_id`),
  CONSTRAINT `fk_mon_reader_mon_machine1` FOREIGN KEY (`mon_machine_id`) REFERENCES `mon_machine` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='this table defines the parameters for a device. eg.\n\n "serial" : "IMA3C08298",\n            "firmware"  : "2.45",\n            "status" : "error"      \n            "message"   : "HOOD_OPEN",\n            "counters"  : {\n                "receipts"      : "nnn",\n                "noPaper"       : "nnn",\n                "hoodOpen"      : "nnn",\n                "initErrors"    : "nnn",\n                "printErrors"   : "nnn",\n                "cutErrors"     : "nnn",\n                "loadingFaults" : "nnn",\n                "comErrors"     : "nnn"\n\n';

--
-- Table structure for table `mon_event`
--

DROP TABLE IF EXISTS `mon_event`;
 CREATE TABLE `mon_event` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status_event` int(11) DEFAULT '1',
  `type_event` varchar(255) DEFAULT NULL,
  `cmd` varchar(255) DEFAULT NULL,
  `id_rule` int(11) NOT NULL,
  `machines_id` int(11) NOT NULL,
  `id_device` int(11) NOT NULL COMMENT 'defines the device or service concerned by this action.',
  PRIMARY KEY (`id`),
  KEY `fk_mon_event_1_idx` (`machines_id`),
  CONSTRAINT `fk_mon_event_1` FOREIGN KEY (`machines_id`) REFERENCES `mon_machine` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `mon_device_service`
--

DROP TABLE IF EXISTS `mon_device_service`;
CREATE TABLE `mon_device_service` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_type` varchar(255) DEFAULT NULL,
  `enable` int(11) NOT NULL DEFAULT '1',
  `structure_json_controle` text NOT NULL COMMENT 'json structure defining the object and bindings',
  `html_form` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `mon_rules`
--


DROP TABLE IF EXISTS `mon_rules`;
CREATE TABLE `mon_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(255) DEFAULT NULL COMMENT 'to bind this rule to a unique machine',
  `device_type` varchar(255) NOT NULL,
  `binding` text NOT NULL COMMENT 'code that will be executed on the information sent from the device or service for defining the actions that will be carried out',
  `succes_binding_cmd` text COMMENT 'command to run if binding test result is True',
  `no_success_binding_cmd` text COMMENT 'command to run if binding test result is False',
  `error_on_binding` text COMMENT 'command to run if binding test returns Error',
  `type_event` varchar(255) NOT NULL DEFAULT 'log' COMMENT 'defines corresponding event',
  `user` varchar(255) DEFAULT NULL COMMENT 'the user who defined this rule',
  `comment` varchar(1024) DEFAULT NULL COMMENT 'explains the contents of this rule',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `mon_panels_template`
--


DROP TABLE IF EXISTS `mon_panels_template`;
CREATE TABLE `mon_panels_template` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_graphe` varchar(255) NOT NULL,
  `template_json` text NOT NULL,
  `type_graphe` varchar(255) NOT NULL,
  `parameters` varchar(1024) DEFAULT NULL COMMENT 'json to define optional parameters',
  `status` int(11) NOT NULL DEFAULT '1',
  `comment` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP procedure IF EXISTS `mon-onlineoffline`;
DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mon-onlineoffline` (IN param_hostname VARCHAR(45))
BEGIN
  SELECT
    date AS 'time',
    status
FROM
    uptime_machine
WHERE
	hostname = param_hostname
ORDER BY date;
END$$
DELIMITER ;

INSERT INTO mon_panels_template(name_graphe, type_graphe, template_json, parameters) VALUES ('Online-Offline Status', 'graph', '{"id":1,"datasource":"xmppmaster","type":"@_type_graphe_@","legend":{"show":true,"current":true,"values":true},"lines":true,"steppedLine":true,"fill":1,"title":"@_name_graphe_@","xaxis":{"mode":"time","show":true},"yaxes":[{"show":false},{"show":true}],"targets":[{"format":"time_series","group":[],"metricColumn":"none","rawQuery":true,"rawSql":"call `mon-onlineoffline`(\'@_hostname_@\');"}]}', '{}');

UPDATE version SET Number = 48;

COMMIT;
