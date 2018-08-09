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


--

-- manage sync for syncthing

START TRANSACTION;


CREATE TABLE IF NOT EXISTS `xmppmaster`.`syncthingsync` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `uuidpackage` VARCHAR(45) NOT NULL,
    `typesynchro` VARCHAR(45) NOT NULL DEFAULT 'create',
    `relayserver_jid` INT(11) NOT NULL,
    `watching` VARCHAR(3) NULL DEFAULT 'yes',
    PRIMARY KEY (`id`));

ALTER TABLE `xmppmaster`.`syncthingsync` 
ADD COLUMN `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `watching`;

ALTER TABLE `xmppmaster`.`syncthingsync` 
CHANGE COLUMN `date` `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `id`;


UPDATE version SET Number = 17;

COMMIT;
