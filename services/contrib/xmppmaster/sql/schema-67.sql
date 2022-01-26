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
-- Database add index
-- ------------------ ----------------------------------------------------
ALTER TABLE `xmppmaster`.`has_cluster_ars`
ADD INDEX `ind_id_ars` (`id_ars` ASC) ;
ALTER TABLE `xmppmaster`.`has_cluster_ars`
ADD INDEX `ind_id_cluster` (`id_cluster` ASC) ;

ALTER TABLE `xmppmaster`.`relayserver`
ADD INDEX `ind_server_name` (`nameserver` ASC);
autre
ALTER TABLE `xmppmaster`.`relayserver`
ADD INDEX `ind_mode_ars` (`moderelayserver` ASC)

-- ----------------------------------------------------------------------
-- Database add index
-- ------------------ ----------------------------------------------------
ALTER TABLE `xmppmaster`.`agent_subscription`
ADD INDEX `ind_name` (`name` ASC) ;
-- ----------------------------------------------------------------------
-- Database supprime index en doublon dans deploy table
-- ------------------ ----------------------------------------------------
 ALTER TABLE `xmppmaster`.`deploy`
DROP INDEX `ind_end_cmd` ;

ALTER TABLE `xmppmaster`.`deploy`
DROP INDEX `ind_start_cmd` ;
;

-- ----------------------------------------------------------------------
-- Database add index
-- ------------------ ----------------------------------------------------
ALTER TABLE `xmppmaster`.`deploy`
ADD INDEX `ind_syncthing` (`syncthing` ASC) ;

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_session` (`sessionid` ASC) ;

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

-- ----------------------------------------------------------------------
-- Database history for deploy table
-- ----------------------------------------------------------------------
-- Database creation historydeploy table
CREATE TABLE `historydeploy` (
  `id` int(11) NOT NULL DEFAULT 0,
  `title` varchar(255) DEFAULT NULL,
  `jidmachine` varchar(255) NOT NULL,
  `jid_relay` varchar(255) NOT NULL,
  `pathpackage` varchar(100) NOT NULL,
  `state` varchar(45) NOT NULL,
  `sessionid` varchar(45) NOT NULL,
  `start` timestamp NOT NULL DEFAULT current_timestamp(),
  `startcmd` timestamp NULL DEFAULT NULL,
  `endcmd` timestamp NULL DEFAULT NULL,
  `inventoryuuid` varchar(11) NOT NULL,
  `host` varchar(255) DEFAULT NULL,
  `user` varchar(45) DEFAULT NULL,
  `command` int(11) DEFAULT NULL,
  `group_uuid` varchar(11) DEFAULT NULL,
  `login` varchar(45) DEFAULT NULL,
  `macadress` varchar(255) DEFAULT NULL,
  `syncthing` int(11) DEFAULT 0,
  `result` mediumtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- add index deploy table on status
ALTER TABLE `xmppmaster`.`deploy`
ADD INDEX `ind_state` (`state` ASC) ;

-- delete old historydeploy

DROP EVENT IF EXISTS purge_historydeploy;
CREATE EVENT IF NOT EXISTS purge_historydeploy
    ON SCHEDULE
        EVERY 1 DAY
        STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 6 HOUR
        COMMENT 'Clean each day at 6 hours olds records of 60 days on table historydeploy'
    DO
          DELETE FROM xmppmaster.historydeploy
WHERE
    endcmd < DATE_SUB(NOW(), INTERVAL 60 DAY);

-- add trigger suppression deploy

DROP TRIGGER IF EXISTS `xmppmaster`.`deploy_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER = CURRENT_USER TRIGGER `xmppmaster`.`deploy_AFTER_DELETE` AFTER DELETE ON `deploy` FOR EACH ROW
BEGIN
INSERT INTO historydeploy
      (id,
      title,
      jidmachine,
      jid_relay,
      pathpackage,state,sessionid,
      start,
      startcmd,
      endcmd,
      inventoryuuid,
      host,
      user,
      command,
      group_uuid,
      login,
      macadress,
      syncthing,
      result)
    VALUES
      (OLD.id,
      OLD.title,
      OLD.jidmachine,
      OLD.jid_relay,
      OLD.pathpackage,
      OLD.state,
      OLD.sessionid,
      OLD.start,
      OLD.startcmd,
      OLD.endcmd,
      OLD.inventoryuuid,
      OLD.host,
      OLD.user,
      OLD.command,
      OLD.group_uuid,
      OLD.login,
      OLD.macadress,
      OLD.syncthing,
      OLD.result);
END$$
DELIMITER ;

-- delete old deploy

DROP EVENT IF EXISTS purge_deploy;
CREATE EVENT IF NOT EXISTS purge_deploy
    ON SCHEDULE
        EVERY 1 DAY
        STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 4 HOUR
        COMMENT 'Clean each day at 4 hours olds records of 30 days on table deploy. the deployment deleted are copy to table historydeploy'
    DO
          DELETE FROM xmppmaster.deploy
WHERE
    endcmd < DATE_SUB(NOW(), INTERVAL 30 DAY);

SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 67;

COMMIT;
