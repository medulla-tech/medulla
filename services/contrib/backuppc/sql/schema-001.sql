--
-- (c) 2010 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Pulse 2, http://pulse2.mandriva.org
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

SET storage_engine=INNODB;
SET GLOBAL character_set_server=UTF8;
SET SESSION character_set_server=UTF8;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS `backup_profiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profilename` varchar(50) NOT NULL,
  `sharenames` text NOT NULL,
  `excludes` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=12 ;


INSERT INTO `backup_profiles` (`id`, `profilename`, `sharenames`, `excludes`) VALUES
(1, 'Windows 7', '/cygdrive/c/Users/', ''),
(11, 'Windows XP', '/cygdrive/c/Documents and Settings/', '');


CREATE TABLE IF NOT EXISTS `backup_servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_uuid` varchar(50) NOT NULL,
  `backupserver_url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entity_uuid` (`entity_uuid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;


INSERT INTO `backup_servers` (`id`, `entity_uuid`, `backupserver_url`) VALUES
(1, 'UUID1', '192.168.71.90/backuppc/index.cgi');


CREATE TABLE IF NOT EXISTS `hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL,
  `backup_profile` int(11) NOT NULL,
  `period_profile` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=18 ;


CREATE TABLE IF NOT EXISTS `period_profiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profilename` varchar(255) NOT NULL,
  `full` float NOT NULL,
  `incr` float NOT NULL,
  `exclude_periods` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=16 ;


INSERT INTO `period_profiles` (`id`, `profilename`, `full`, `incr`, `exclude_periods`) VALUES
(1, 'Night time backup', 7, 1, '8.00=>19.50:1,2,3,4,5');


CREATE TABLE IF NOT EXISTS `Version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



INSERT INTO `Version` (`Number`) VALUES
(1);


COMMIT;
