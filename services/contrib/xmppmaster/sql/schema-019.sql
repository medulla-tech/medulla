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

ALTER TABLE `xmppmaster`.`relayserver` CHANGE COLUMN `jid` `jid` VARCHAR(255) NOT NULL ;
ALTER TABLE `xmppmaster`.`machines` CHANGE COLUMN `jid` `jid` VARCHAR(255) NOT NULL ;
-- table Deploy
ALTER TABLE `xmppmaster`.`deploy`
CHANGE COLUMN `jid_relay` `jid_relay` VARCHAR(255) NOT NULL ,
CHANGE COLUMN `jidmachine` `jidmachine` VARCHAR(255) NOT NULL ;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 19;

COMMIT;
