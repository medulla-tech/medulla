--
-- (c) 2020 Siveo, http://www.siveo.net/
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

USE `xmppmaster`;

-- resize fild type  in table log
TRUNCATE `xmppmaster`.`logs`;
ALTER TABLE `xmppmaster`.`logs`
CHANGE COLUMN `type` `type` VARCHAR(25) NOT NULL DEFAULT 'noset' ;

-- add 2 filds in table user for event registers  machine
ALTER TABLE `xmppmaster`.`users`
ADD COLUMN `creation_user` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP AFTER `country_name`,
ADD COLUMN `last_modif` TIMESTAMP NULL AFTER `creation_user`;

-- add uui_serial_machine in table machine
ALTER TABLE `xmppmaster`.`machines`
ADD COLUMN `uuid_serial_machine` VARCHAR(45) NULL DEFAULT '' AFTER `jid`;

-- Increase table size to 100
ALTER TABLE has_relayserverrules MODIFY subject varchar(100);

UPDATE version SET Number = 50;
COMMIT;
