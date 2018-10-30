--
-- (c) 2018 Siveo, http://www.siveo.net/
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



DROP TABLE IF EXISTS `xmppmaster`.`historylogs` ;

CREATE TABLE IF NOT EXISTS `xmppmaster`.`historylogs` (
  `id` int(10),
  `date` timestamp,
  `type` varchar(6),
  `module` varchar(45),
  `text` varchar(255),
  `fromuser` varchar(45),
  `touser` varchar(45),
  `action` varchar(45),
  `sessionname` varchar(20),
  `how` varchar(255),
  `why` varchar(255),
  `priority` int(11),
  `who` varchar(45)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ici quand on supprime un enregistrement dans la table logs. celui ci est ajouté par trigger dans la base history.


DROP TRIGGER IF EXISTS trig_apres_delete_logs;
DELIMITER //
CREATE TRIGGER trig_apres_delete_logs
AFTER DELETE ON logs FOR EACH ROW
  BEGIN
    INSERT INTO historylogs
      (id, date, type, module, text,fromuser,touser,action,sessionname,how,why,priority,who)
    VALUES
      (OLD.id, OLD.date, OLD.type, OLD.module, OLD.text,OLD.fromuser,OLD.touser,OLD.action,OLD.sessionname,OLD.how,OLD.why,OLD.priority,OLD.who);
  END //
DELIMITER ;

-- ici le system scheduler de mysql.
-- system event scheduler mysql enable
-- demande super privilege
-- SET GLOBAL event_scheduler = 1 ;

-- see status system event scheduler mysql
-- SHOW GLOBAL VARIABLES LIKE 'event_scheduler';


-- Delete  one month old record table logs
-- DELETE FROM logs WHERE date < DATE_SUB(NOW(), INTERVAL 30 DAY);
CREATE EVENT IF NOT EXISTS purgelogs
  ON SCHEDULE
  AT
  (CURRENT_TIMESTAMP + INTERVAL 1 DAY) ON COMPLETION PRESERVE ENABLE
  DO
    DELETE FROM logs WHERE date < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Delete  one month old record table logs
-- DELETE FROM logs WHERE date < DATE_SUB(NOW(), INTERVAL 30 DAY);
CREATE EVENT IF NOT EXISTS purgehistorylogs
  ON SCHEDULE
  AT
  (CURRENT_TIMESTAMP + INTERVAL 2 DAY) ON COMPLETION PRESERVE ENABLE
  DO
    DELETE FROM historylogs WHERE date < DATE_SUB(NOW(), INTERVAL 60 DAY);

-- creation  bandwidth
ALTER TABLE `xmppmaster`.`has_login_command`
ADD COLUMN `bandwidth` INT(11) NULL DEFAULT '0' AFTER `shutdownrequired`;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 12;

COMMIT;
