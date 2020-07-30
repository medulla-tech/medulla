--
-- (c) 2020 Siveo, http://www.siveo.net/
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

USE `xmppmaster`;
DROP procedure IF EXISTS `afterinsertmachine`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `afterinsertmachine`(IN newjid VARCHAR(255))
BEGIN
set @userjid =  SUBSTRING_INDEX(SUBSTRING_INDEX(newjid, '@', 1),'.',1);
set @tmpval = SUBSTRING_INDEX(newjid, '@', -1);
set @domain = SUBSTRING_INDEX(@tmpval, '/', 1);
set @resource = SUBSTRING_INDEX(@tmpval, '/', -1);
-- SELECT @userjid, @domain, @resource;
DELETE FROM `xmppmaster`.`machines`

WHERE
    jid LIKE CONCAT(@resource, '%');
END$$

DELIMITER ;


UPDATE version SET Number = 46;

COMMIT;
