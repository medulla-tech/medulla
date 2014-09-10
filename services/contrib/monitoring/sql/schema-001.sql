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
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.


SET storage_engine=INNODB;
SET GLOBAL character_set_server=UTF8;
SET SESSION character_set_server=UTF8;

CREATE TABLE IF NOT EXISTS `monitoring_detection` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `ip` varchar(15) NOT NULL,
    `os` text NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

CREATE TABLE IF NOT EXISTS `monitoring_options` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `result` varchar(255) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

CREATE TABLE IF NOT EXISTS `monitoring_ack` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `username` varchar(255) NOT NULL,
    `ackid` varchar(255) NOT NULL,
    `ackmessage` text NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 ;

CREATE TABLE IF NOT EXISTS `version` (
    `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `version` (`Number`) VALUES(1);

COMMIT;
