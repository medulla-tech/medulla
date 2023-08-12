--
-- (c) 2023 Siveo, http://www.siveo.net/
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

START TRANSACTION;
USE `xmppmaster`;

-- ----------------------------------------------------------------------
-- Trigger up_white_list_AFTER_DELETE
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_white_list_AFTER_DELETE`;

DELIMITER $$
CREATE TRIGGER `xmppmaster`.`up_white_list_AFTER_DELETE` AFTER DELETE ON `up_white_list` FOR EACH ROW
BEGIN
	delete from up_gray_list_flop where up_gray_list_flop.updateid = old.updateid;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_white_list_AFTER_INSERT
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_white_list_AFTER_INSERT`;

DELIMITER $$
CREATE TRIGGER `xmppmaster`.`up_white_list_AFTER_INSERT` AFTER INSERT ON `up_white_list` FOR EACH ROW
BEGIN
	delete from xmppmaster.up_gray_list where updateid = new.updateid;
END$$
DELIMITER ;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 81;

COMMIT;
