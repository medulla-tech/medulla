--
-- (c) 2008 Mandriva, http://www.mandriva.com/
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

-- taken from old "14b" dummy version
ALTER TABLE `commands` \
    MODIFY `do_halt` VARCHAR(255) NOT NULL DEFAULT '';

-- to limit client number on a same proxy the same time
ALTER TABLE `commands_on_host` \
    ADD COLUMN `max_clients_per_proxy` INT NOT NULL DEFAULT 0;

-- changing column name and type requier a little processing
-- no = none (obviously)
-- yes = queue as it was the only mode available previously
ALTER TABLE `commands` ADD COLUMN `proxy_mode` ENUM("split", "queue", "none") DEFAULT "none" NOT NULL AFTER `use_local_proxy`;
UPDATE `commands` SET `proxy_mode` = "none" where `use_local_proxy` = "no";
UPDATE `commands` SET `proxy_mode` = "queue" where `use_local_proxy` = "yes";
ALTER TABLE `commands` DROP COLUMN `use_local_proxy`;

-- to speed-up MSC cleanups (see http://pulse2.mandriva.org/ticket/493)
CREATE INDEX fk_target_idx ON commands_on_host(fk_target);

-- Bump version
DELETE FROM version;
INSERT INTO version VALUES( "15" );
