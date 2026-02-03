
--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/>.

USE mastering;

START TRANSACTION;

CREATE TABLE `servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) NOT NULL,
  `jid` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `masters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL DEFAULT '',
  `description` varchar(255) DEFAULT NULL,
  `uuid` varchar(50) NOT NULL,
  `path` varchar(255) NOT NULL,
  `size` bigint(20) DEFAULT 0,
  `os` varchar(100) DEFAULT '',
  `os_type` varchar(50) DEFAULT '',
  `creation_date` datetime DEFAULT current_timestamp(),
  `modification_date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `mastersEntities` (
  `master_id` int(11) NOT NULL,
  `entity_id` int(11) NOT NULL
);


UPDATE version SET Number = 2;
COMMIT;
