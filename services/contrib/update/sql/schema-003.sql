--
-- (c) 2010 Mandriva, http://www.mandriva.com/
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

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

ALTER TABLE  `os_classes` ADD  `pattern` TEXT NOT NULL;
UPDATE  `os_classes` SET  `pattern` =  '*windows xp*' WHERE  `os_classes`.`id` =1;
UPDATE  `os_classes` SET  `pattern` =  '*windows vista*' WHERE  `os_classes`.`id` =2;
UPDATE  `os_classes` SET  `pattern` =  '*windows 7*' WHERE  `os_classes`.`id` =3;

UPDATE  `version` SET  `Number` =  '3';

COMMIT;
