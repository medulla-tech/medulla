--
-- (c) 2018 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Medulla 2, http://www.siveo.net/
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

START TRANSACTION;

LOCK TABLES `xmppmaster`.`qa_custom_command` WRITE;
UPDATE `xmppmaster`.`qa_custom_command` SET `customcmd` = 'net stop "medullaagent" & net start "medullaagent"'
    WHERE (`user` = 'allusers')
        AND (`os` = 'windows')
        AND (`namecmd` = 'Restart Medulla Agent service');
UNLOCK TABLES;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 39;

COMMIT;
