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


-- check exist index before creation




START TRANSACTION;

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------------------------------------------------
-- Database change type champ add index
-- ----------------------------------------------------------------------

ALTER TABLE `msc`.`target`
CHANGE COLUMN `id_group` `id_group` VARCHAR(12) NULL DEFAULT NULL ;

ALTER TABLE `msc`.`target`
ADD INDEX `index_id_group` (`id_group` ASC);
;


SET FOREIGN_KEY_CHECKS=1;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 30;

COMMIT;

