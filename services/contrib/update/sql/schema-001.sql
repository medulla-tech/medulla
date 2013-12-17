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

-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Dec 16, 2013 at 05:55 PM
-- Server version: 5.5.31
-- PHP Version: 5.4.4-14+deb7u5

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `update`
--

-- --------------------------------------------------------

--
-- Table structure for table `os_classes`
--

CREATE TABLE IF NOT EXISTS `os_classes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `os_classes`
--

INSERT INTO `os_classes` (`id`, `name`) VALUES
(1, 'Windows XP'),
(2, 'Windows Vista'),
(3, 'Windows 7');

-- --------------------------------------------------------

--
-- Table structure for table `targets`
--

CREATE TABLE IF NOT EXISTS `targets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `update_id` int(11) NOT NULL,
  `uuid` int(11) NOT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `is_installed` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `updates`
--

CREATE TABLE IF NOT EXISTS `updates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `uuid` varchar(255) NOT NULL,
  `kb_number` varchar(255) NOT NULL,
  `os_class_id` int(11) NOT NULL,
  `type_id` int(11) NOT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  `need_reboot` int(11) NOT NULL,
  `request_user_input` int(11) NOT NULL,
  `info_url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `update_types`
--

CREATE TABLE IF NOT EXISTS `update_types` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `status` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `update_types`
--

INSERT INTO `update_types` (`id`, `name`, `status`) VALUES
(1, 'Software', 0),
(2, 'Driver', 0);

-- --------------------------------------------------------

CREATE TABLE IF NOT EXISTS `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `version` (`Number`) VALUES(1);

COMMIT;
