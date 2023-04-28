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
-- Database add colunms in table mon_event
--    - parameter_other : Field reserved for 1 subsequent use 
--    - ack_user        : field used to indicate the user who acquitted the alarm
--    - ack_date        : field used to indicate when the alarm was acquired. 
-- ----------------------------------------------------------------------

ALTER TABLE `xmppmaster`.`mon_event`
    ADD COLUMN `parameter_other` VARCHAR(1024) NULL DEFAULT NULL AFTER `id_device`,
    ADD COLUMN `ack_user` VARCHAR(90) NULL DEFAULT NULL AFTER `parameter_other`;
ALTER TABLE `xmppmaster`.`mon_event` 
    ADD COLUMN `ack_date` TIMESTAMP NULL DEFAULT NULL AFTER `ack_user`;

ALTER TABLE `xmppmaster`.`cluster_resources`
ADD INDEX IF NOT EXISTS `jidindex` (`jidmachine` ASC);

SET FOREIGN_KEY_CHECKS=1;

UPDATE version SET Number = 65;

COMMIT;
