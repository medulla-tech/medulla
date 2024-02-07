--
-- (c) 2023 Siveo, http://www.siveo.net/
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
-- Database greenit
-- ----------------------------------------------------------------------

START TRANSACTION;

--
-- Table structure for table `version`
--

CREATE TABLE if not exists `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for profils
--

CREATE TABLE IF NOT EXISTS `tests` (
        `id` int NOT NULL AUTO_INCREMENT, PRIMARY KEY(`id`),
        `name` varchar(50) NOT NULL,
        `message` varchar(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `version` VALUES (1);

COMMIT;
