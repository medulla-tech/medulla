--
-- (c) 2013 Mandriva, http://www.mandriva.com/
--
-- This file is part of Medulla 2, http://medulla.mandriva.org
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

-- Tranforming the workflow to dynamic.
-- Each record in commands_on_hosts_phase corrensponds to one phase
-- in the actual workflow.


CREATE INDEX target_uuid_idx ON pull_targets(target_uuid);

DELETE FROM version;
INSERT INTO version VALUES("24");
