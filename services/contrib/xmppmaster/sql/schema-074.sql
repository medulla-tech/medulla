--
-- (c) 2022 Siveo, http://www.siveo.net/
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

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------

START TRANSACTION;
USE `xmppmaster`;

-- ----------------------------------------------------------------------
-- ALTER command_qa
-- Add a column command_qa.jid_machine to have a ref to the machine even if there is no inventory
-- ----------------------------------------------------------------------
ALTER TABLE command_qa ADD COLUMN jid_machine varchar(255) NOT NULL AFTER command_machine;

-- ----------------------------------------------------------------------
-- ALTER command_action
-- Add a column command_action.jid_target to have a ref to the machine even if there is no inventory
-- ----------------------------------------------------------------------
ALTER TABLE command_action ADD COLUMN jid_target varchar(255) NOT NULL AFTER target;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 74;

COMMIT;
