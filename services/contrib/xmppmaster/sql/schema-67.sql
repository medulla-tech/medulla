--
-- (c) 2021 Siveo, http://www.siveo.net/
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

-- ----------------------------------------------------------------------
-- Database xmppmaster add index table machineS
-- ----------------------------------------------------------------------

START TRANSACTION;

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;

ALTER TABLE `xmppmaster`.`machines`
ADD INDEX `ind_hostname` (`hostname` ASC) ;

ALTER TABLE `xmppmaster`.`cluster_resources`
ADD INDEX `ind_jid_search` (`jidmachine` ASC);
;

DROP EVENT IF EXISTS purgecluster_resource;
CREATE EVENT IF NOT EXISTS purgecluster_resource
    ON SCHEDULE
        EVERY 1 DAY
        STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 5 HOUR
        COMMENT 'Clean each day at 5 hours olds records of 30 days on table cluster ressource'
    DO
          DELETE FROM xmppmaster.cluster_resources WHERE endcmd < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- ----------------------------------------------------------------------
-- Database supprime index en doublon dans deploy table
-- ------------------ ----------------------------------------------------
 ALTER TABLE `xmppmaster`.`deploy`
DROP INDEX `ind_end_cmd` ;

ALTER TABLE `xmppmaster`.`deploy`
DROP INDEX `ind_start_cmd` ;
;
-- ----------------------------------------------------------------------
-- Database add index  dans machines table
-- ------------------ ----------------------------------------------------
ALTER TABLE `xmppmaster`.`machines`
ADD INDEX `ind_groupedeploy` (`groupdeploy` ASC)
ALTER TABLE `xmppmaster`.`machines`
ADD INDEX `ind_macadress` (`macaddress` ASC) ;
-- ----------------------------------------------------------------------
-- Database controle insertion dans table machine
-- ------------------ ----------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `afterinsertmachine`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`afterinsertmachine`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `afterinsertmachine`(IN newjid VARCHAR(255))
BEGIN
-- efface si il existe 1 ancien jid pour la meme machine.
-- si on trouve 1 machine avec le meme hostname,
-- mais avec 1 sufixe d user different
-- ou 1 domaine different
-- ou encore 1 ressource differente.
-- on supprime cette machine de la table machine.

set @userjid =  SUBSTRING_INDEX(SUBSTRING_INDEX(newjid, '@', 1),'.',1);
set @pattern = CONCAT("^" ,@userjid);-- le patern est user du newjid precede de ^

DELETE FROM `xmppmaster`.`machines`
WHERE
    `id` IN (SELECT
        id
    FROM
        `xmppmaster`.`machines`
    WHERE
        `jid` REGEXP @pattern
        AND `enabled` = 0
        AND `uuid_inventorymachine` IS NOT NULL)
    AND `jid` != newjid;
END$$

DELIMITER ;
;



SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 67;

COMMIT;
