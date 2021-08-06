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

CREATE TABLE `ban_machines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `jid` varchar(100) DEFAULT NULL COMMENT 'Allow to know the account name,\nBanned machines jid.',
  `ars_server` varchar(100) DEFAULT NULL COMMENT 'define the ars where the ejabberd command have to be executed.',
  `reason` varchar(100) DEFAULT NULL COMMENT 'Specify the reason why the machine is banned',
  `start_date` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'The datetime when the machine started to be banned',
  `end_date` timestamp NULL DEFAULT NULL COMMENT 'If specified, the datetime of the end of the ban for the machine.\nIf not specified: permanantly ban',
  PRIMARY KEY (`id`),
  UNIQUE KEY `jid_UNIQUE` (`jid`),
  KEY `ind_start_date` (`start_date`),
  KEY `ind_end_date` (`end_date`),
  KEY `jid_machine` (`jid`),
  KEY `jud_ars` (`ars_server`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8 COMMENT='This table give the possibility to exclude machines from relay. To reallow banned machines on the relay we must delete its account on the xmpp server';

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 65;

COMMIT;
