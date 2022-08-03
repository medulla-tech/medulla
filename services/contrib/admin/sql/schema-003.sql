--
-- (c) 2022 Siveo, http://www.siveo.net/
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

ALTER TABLE `admin`.`upd_list_package`
ADD CONSTRAINT `fk_upd_list_package_1` FOREIGN KEY (`package_id`) REFERENCES `upd_package` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

ALTER TABLE `admin`.`upd_list_package`
ADD CONSTRAINT `fk_upd_list_package_2` FOREIGN KEY (`list_id`) REFERENCES `upd_list` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

ALTER TABLE `admin`.`upd_list_package`
ADD CONSTRAINT `fk_upd_list_package_3` FOREIGN KEY (`method_id`) REFERENCES `upd_method` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

ALTER TABLE `admin`.`upd_rules`
ADD CONSTRAINT `fk_upd_method` FOREIGN KEY (`method_id`) REFERENCES `upd_method` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;

ALTER TABLE `admin`.`upd_rules`
ADD CONSTRAINT `fk_upd_pack` FOREIGN KEY (`package_id`) REFERENCES `upd_package` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION;


UPDATE version SET Number = 3;

COMMIT;
