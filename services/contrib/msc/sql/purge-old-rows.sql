--
-- (c) 2008 Mandriva, http://www.mandriva.com/
--
-- $Id$
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
--
-- This query delete old lsc commands (now - 1 month)
--

DELETE
    commands,
    commands_on_host,
    commands_history
FROM
    commands A,
    commands_on_host B,
    commands_history C
WHERE
    A.creation_date < (DATE_SUB(NOW(), INTERVAL 1 MONTH)) AND
    A.id_command = B.id_command AND
    B.id_command_on_host = C.id_command_on_host
