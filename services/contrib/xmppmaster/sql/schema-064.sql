--
-- (c) 2021 Siveo, http://www.siveo.net/
--
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
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------
-- ----------------------------------------------------------------------
-- Creation table update_machine
-- This table is used to define the update state of a machine.
-- ----------------------------------------------------------------------

DROP TABLE IF EXISTS `update_machine`;
CREATE  TABLE IF NOT EXISTS  `update_machine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `hostname` varchar(120) NOT NULL,
  `jid` varchar(255) NOT NULL,
  `status` varchar(15) NOT NULL DEFAULT 'ready',
  `descriptor` text NOT NULL DEFAULT '""',
  `md5` varchar(45) NOT NULL,
  `date_creation` timestamp NOT NULL DEFAULT current_timestamp(),
  `ars` varchar(255) DEFAULT NULL COMMENT 'This information is needed if the machine needs to use an ARS to be updated',
  PRIMARY KEY (`id`),
  UNIQUE KEY `jid_UNIQUE` (`jid`),
  KEY `ind_jid` (`jid`),
  KEY `ind_status` (`status`),
  KEY `ind_hostname` (`hostname`),
  KEY `ind_date` (`date_creation`),
  KEY `ind_ars` (`ars`)
) ENGINE=InnoDB AUTO_INCREMENT=93368 DEFAULT CHARSET=utf8 COMMENT='This table is used to define the update state of a machine.';
-- ----------------------------------------------------------------------
-- Creation table ban_machine
-- This table allow to define banned machines.
-- ----------------------------------------------------------------------
DROP TABLE IF EXISTS `ban_machines`;
CREATE TABLE if not exists `ban_machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT, PRIMARY KEY (`id`),
  `jid` varchar(100) DEFAULT NULL COMMENT 'Allow to know the account name,\nBanned machine\'s jid.',
  `ars_server` varchar(100) DEFAULT NULL COMMENT 'define the ars where the ejabberd command have to be executed.',
  `reason` varchar(100) DEFAULT NULL COMMENT 'Specify the reason why the machine is banned',
  `start_date` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'The datetime when the machine started to be banned',
  `end_date` timestamp NULL COMMENT 'If specified, the datetime of the end of the ban for the machine.\nIf not specified: permanantly ban',
  UNIQUE KEY `jid_UNIQUE` (`jid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='This table give the possibility to exclude machines from relay. To reallow banned machines on the relay we must delete its account on the xmpp server';

SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 64;

COMMIT;
