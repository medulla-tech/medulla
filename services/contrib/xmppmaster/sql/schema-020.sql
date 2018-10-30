--
-- (c) 2018 Siveo, http://www.siveo.net/
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

--
-- Table structure for table `organization_AD`
-- AD information for machine windows
--

DROP TABLE IF EXISTS `organization_ad`;
CREATE TABLE `organization_ad` (
  `id_inventory` int(11) NOT NULL,
  `jiduser` varchar(80) NOT NULL,
  `ouuser` varchar(120) DEFAULT NULL,
  `oumachine` varchar(120) DEFAULT NULL,
  `hostname` varchar(100) DEFAULT NULL,
  `username` varchar(60) DEFAULT NULL,
  PRIMARY KEY (`id_inventory`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

UPDATE version SET Number = 20;

COMMIT;
