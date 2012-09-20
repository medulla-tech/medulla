--
-- (c) 2012 Mandriva, http://www.mandriva.com/
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

-- Indexes to speed up the scheduler

CREATE INDEX current_state_idx ON commands_on_host(current_state);
CREATE INDEX attempts_left_idx ON commands_on_host(attempts_left);
CREATE INDEX next_launch_date_idx ON commands_on_host(next_launch_date);
CREATE INDEX scheduler_idx ON commands_on_host(scheduler);

CREATE INDEX start_date_idx ON commands(start_date);
CREATE INDEX end_date_idx ON commands(end_date);

-- Bump version
DELETE FROM version;
INSERT INTO version VALUES( "17" );
