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
-- Database version 3
-- ----------------------------------------------------------------------

UPDATE data SET entity_id = REPLACE(entity_id, 'UUID', '') WHERE 1;
ALTER TABLE  `data` CHANGE  `value`  `value` INT NOT NULL;
ALTER TABLE  `data` CHANGE  `entity_id`  `entity_id` INT NOT NULL;
ALTER TABLE  `report`.`data` ADD INDEX  `indicator_id` (  `indicator_id` );
ALTER TABLE  `report`.`data` ADD INDEX  `entity_id` (  `entity_id` );

-- ADDING DATA_TEXT AND DATA_FLOAT

--
-- Table structure for table `data_float`
--

CREATE TABLE IF NOT EXISTS `data_float` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `indicator_id` int(11) NOT NULL,
  `timestamp` bigint(20) NOT NULL,
  `value` double NOT NULL,
  `entity_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_id` (`entity_id`),
  KEY `indicator_id` (`indicator_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `data_text`
--

CREATE TABLE IF NOT EXISTS `data_text` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `indicator_id` int(11) NOT NULL,
  `timestamp` bigint(20) NOT NULL,
  `value` varchar(255) NOT NULL,
  `entity_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `entity_id` (`entity_id`),
  KEY `indicator_id` (`indicator_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

UPDATE `version` SET Number = 3;

COMMIT;
