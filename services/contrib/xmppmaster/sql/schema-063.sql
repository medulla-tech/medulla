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

START TRANSACTION;

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------
-- ----------------------------------------------------------------------
-- Creation table pulse_users
-- This table is used to define users. We attribute them preferences and permissions to allow to visualize shares
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `pulse_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `login` varchar(255) NOT NULL,
  `comment` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `login_UNIQUE` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
-- ----------------------------------------------------------------------
-- Creation table pulse_teams
-- This table is used to define the teams
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `pulse_teams` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Define the team',
  `name` varchar(120) NOT NULL,
  `comment` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Creation table pulse_preferences
-- This table allow to attribute preferences in a key/value format to one user
-- ----------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS `pulse_preferences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(120) NOT NULL,
  `value` text DEFAULT '""',
  `id_user` int(11) NOT NULL,
  `domain` varchar(80) DEFAULT NULL COMMENT 'This field can set preferences to a domain ( a domain can be a web page for ex. )',
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_UNIQUE` (`key`,`id_user`,`domain`),
  KEY `fk_pulse_preferences_1_idx` (`id_user`),
  CONSTRAINT `fk_pulse_preferences_1` FOREIGN KEY (`id_user`) REFERENCES `pulse_users` (`id`)
  ON DELETE NO ACTION
  ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------------------------------------------------
-- Creation table pulse_team_user
-- This table is used to create teams
-- ----------------------------------------------------------------------

 CREATE TABLE IF NOT EXISTS `pulse_team_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) DEFAULT NULL,
  `id_team` int(11) DEFAULT NULL,
  `comment` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unix_team_user` (`id_user`,`id_team`),
  KEY `fk_pulse_team_user_1_idx` (`id_user`),
  KEY `fk_pulse_team_user_2_idx` (`id_team`),
  CONSTRAINT `fk_pulse_team_user_1` FOREIGN KEY (`id_user`) REFERENCES `pulse_users` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE,
  CONSTRAINT `fk_pulse_team_user_2` FOREIGN KEY (`id_team`) REFERENCES `pulse_teams` (`id`)
  ON DELETE CASCADE
  ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- ----------------------------------------------------------------------
-- create use root
-- ----------------------------------------------------------------------

INSERT IGNORE INTO `xmppmaster`.`pulse_users` (`login`) VALUES ('root');

-- ----------------------------------------------------------------------
-- Add in table logs index on date
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`logs`
ADD INDEX IF NOT EXISTS `ind_date_log` (`date` ASC) ;

-- ----------------------------------------------------------------------
-- change size coluum in table logs field text
-- -----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`logs`
CHANGE COLUMN `text` `text` VARCHAR(4096) NOT NULL ;

-- les champs de la tables historylogs doivent correspondre au champ de la table logs. ------------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `text` `text` VARCHAR(4096) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `type` `type` VARCHAR(25) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `module` `module` VARCHAR(255) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `fromuser` `fromuser` VARCHAR(255) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `touser` `touser` VARCHAR(255) NULL DEFAULT NULL ;

ALTER TABLE `xmppmaster`.`historylogs`
CHANGE COLUMN `who` `who` VARCHAR(255) NULL DEFAULT NULL ;


-- ----------------------------------------------------------------------
-- Definition procedure stockee for support
-- ces procedure sont prefixe par support.
-- -----------------------------------------------------------------------
-- /#####################################################################\
-- | creation table help command                                         |
-- \#####################################################################/
 CREATE TABLE `support_help_command` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `description` varchar(5000) DEFAULT NULL,
  `example` varchar(5000) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `result` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- /##########################################################################\
-- | function  fs_help                                                        |
-- | cette function permet de demander de l'aide sur 1 function siveo definie |
-- | exemple : select fs_help("%restart_deploy%" );                           |
-- \##########################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_help`;

USE `xmppmaster`;
DROP function IF EXISTS `xmppmaster`.`fs_help`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `fs_help`(command char(255) ) RETURNS text CHARSET utf8
BEGIN
set @typestr = "No definie type";
SELECT
    name, description, example, result, type
INTO @namects , @descriptioncts , @examplects , @resultcts , @typects FROM
    support_help_command
WHERE
    name LIKE command
    limit 1;

if @typects = "p" then
	set @typestr = "Procedure" ;
 else
	if @typects = "f" then
		set @typestr = "Function" ;
    else
        if @typects = "v" then
            set  @typestr = "View" ;
		end if;
	end if;
end if;

SELECT
    CONCAT(@typestr,
            ' : ',
            @namects,
            '\nDecription : \n\t',
             COALESCE(@descriptioncts,''),
            '\n\nExemple :\n\t',
            COALESCE(@examplects, '')) INTO @re1;

SELECT CONCAT("\nresult :\n",COALESCE(@resultcts, '')) INTO @re2;

SELECT CONCAT( @re1, @re2) into @re1;

RETURN @re1;
END$$

DELIMITER ;
;

-- /#####################################################################\
-- | support_restart_deploy procedure                                    |
-- | This procedure is used to restart a deploy                          |
-- | The session's logs are removed                                      |
-- | exemple: call support_restart_deploy('command3bd50e905a4f4c4e82');  |
-- \#####################################################################/
USE `xmppmaster`;
DROP procedure IF EXISTS `support_restart_deploy`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`support_restart_deploy`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `support_restart_deploy`(IN IN_sessid VARCHAR(255))
BEGIN
set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid);
set @grp = (select group_uuid from  xmppmaster.deploy where sessionid like IN_sessid );
DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` = @cmd) and  NOW() > end_date;
UPDATE `msc`.`phase` SET `state` = 'ready' WHERE (`msc`.`phase`.`fk_commands_on_host` = @cmd );
END$$

DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`) VALUES ('support_restart_deploy', 'This prodecure is used to restart deploys.\nThe old logs are replaced by the new ones.', 'call support_restart_deploy(\'command3bd50e905a4f4c4e82\');', 'P');

-- ----------------------------------------------------------------------
-- Definition functions for support
-- ces fonctions sont prfixe par fs_
-- ----------------------------------------------------------------------
-- /#####################################################################\
-- | function fs_jiduser                                                 |
-- | cette function renvoi user d'un jid                                 |
-- | exemple select fs_jiduser("jfk@pulse/ressource1");                   |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jiduser`;
;
DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `fs_jiduser`(jid char(255) ) RETURNS char(255) CHARSET utf8
BEGIN
-- return le user d'un jid
RETURN  substring_index(jid, '@', 1);
END$$
DELIMITER ;
;
-- /#####################################################################\
-- | function fs_jidresource                                               |
-- | cette function renvoi resource d'un jid                               |
-- | exemple select fs_jidresource("jfk@pulse/ressource1");                 |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jidresource`;
DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `fs_jidresource`(jid char(255)) RETURNS char(255) CHARSET utf8
BEGIN
-- return la resource d'un jid
RETURN  substring_index(jid, '/', -1);
END$$
DELIMITER ;
INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('fs_jidresource', ' cette function renvoi resource d\'un jid      ', 'select fs_jidresource(\"jfk@pulse/ressource1\");    ', 'F', '+----------------------------------------+\n| fs_jidresource(\"jfk@pulse/ressource1\") |\n+----------------------------------------+\n| ressource1                             |\n+----------------------------------------+\n');


-- /#####################################################################\
-- | function fs_jiddomain                                               |
-- | cette function renvoi domain d'un jid          |
-- | exemple select fs_jiddomain("jfk.xya@pulse/ressource1");             |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jiddomain`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jiddomain` (jid char(255))
	RETURNS char(255) CHARSET utf8
BEGIN
-- return le domaine d'un jid
RETURN  substring_index(substring_index(jid, '/', 1), '@', -1);
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`id`, `name`, `description`, `example`, `type`, `result`) VALUES ('', 'fs_jiddomain', 'cette function renvoi domain d\'un jid', 'select fs_jiddomain(\"jfk.xya@pulse/ressource1\");', 'F', '+------------------------------------------+\n| fs_jiddomain(\"jfk.xya@pulse/ressource1\") |\n+------------------------------------------+\n| pulse                                    |\n+------------------------------------------+\n');


-- /#####################################################################\
-- | function fs_jidusertrue                                             |
-- | cette function renvoi domain d'un jid sans le .xxx de user          |
-- | exemple select fs_jidusertrue("jfk.xya@pulse/ressource1");          |
-- \#####################################################################/
USE `xmppmaster`;
DROP function IF EXISTS `fs_jidusertrue`;
DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jidusertrue` (jid char(255))
	RETURNS char(255) CHARSET utf8
BEGIN
-- return le user d'un jid sans .xxx
RETURN  substring_index(substring_index(jid, '@', 1), '.', 1);
END$$
DELIMITER ;

INSERT INTO `xmppmaster`.`support_help_command` (`id`, `name`, `description`, `example`, `type`, `result`) VALUES ('', 'fs_jidusertrue', 'cette function renvoi domain d\'un jid sans le .xxx de user ', 'select fs_jidusertrue(\"jfk.xya@pulse/ressource1\");', 'F', '+--------------------------------------------+\n| fs_jidusertrue(\"jfk.xya@pulse/ressource1\") |\n+--------------------------------------------+\n| jfk                                        |\n+--------------------------------------------+\n');


-- /#####################################################################\
-- | function fs_tablefields                                              |
-- | cette function renvoila list des champ de la table xmppmaster passe |
-- | exemple select fs_jidusershort("jfk.xya@pulse/ressource1);          |
-- \#####################################################################/


USE `xmppmaster`;
DROP function IF EXISTS `fs_tablefields`;

USE `xmppmaster`;
DROP function IF EXISTS `xmppmaster`.`fs_tablefields`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` FUNCTION `fs_tablefields`(tablename char(255)) RETURNS text CHARSET utf8
BEGIN
select listcolumn  into @malist from (
  SELECT GROUP_CONCAT(COLUMN_NAME) as listcolumn

  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = 'xmppmaster' AND TABLE_NAME like tablename ) as dede;
 RETURN @malist;
END$$

DELIMITER ;
;

INSERT INTO `xmppmaster`.`support_help_command` (`id`, `name`, `description`, `example`, `type`, `result`) VALUES ('', 'fs_tablefields', 'cette function renvoila list des champs de la table xmppmaster passee', 'select fs_tablefields(\'logs\');', 'F', '+----------------------------------------------------------------------------------+\n| fs_tablefields(\'logs\')                                                            |\n+----------------------------------------------------------------------------------+\n| id,date,type,module,text,fromuser,touser,action,sessionname,how,why,priority,who |\n+----------------------------------------------------------------------------------+\n');



-- /#####################################################################\
-- | View vs_stats_ars                                                   |
-- | cette vue permet de voir la repartition des machine des ars         |
-- | exemple select * from vs_stats_ars;                                 |
-- \#####################################################################/
USE `xmppmaster`;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `vs_stats_ars` AS
    SELECT
        `machines`.`groupdeploy` AS `groupdeploy`,
        SUM(CASE
            WHEN LOCATE('linux', `machines`.`platform`) THEN 1
            ELSE 0
        END) AS `nblinuxmachine`,
        SUM(CASE
            WHEN LOCATE('windows', `machines`.`platform`) THEN 1
            ELSE 0
        END) AS `nbwindows`,
        SUM(CASE
            WHEN LOCATE('darwin', `machines`.`platform`) THEN 1
            ELSE 0
        END) AS `nbdarwin`,
        SUM(CASE
            WHEN `machines`.`enabled` = '1' THEN 1
            ELSE 0
        END) AS `mach_on`,
        SUM(CASE
            WHEN `machines`.`enabled` = '0' THEN 1
            ELSE 0
        END) AS `mach_off`,
        SUM(CASE
            WHEN
                SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U'
            THEN
                0
            ELSE 1
        END) AS `uninventoried`,
        SUM(CASE
            WHEN
                SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U'
            THEN
                1
            ELSE 0
        END) AS `inventoried`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = '1'
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) <> 'U')
            THEN
                1
            ELSE 0
        END) AS `uninventoried_online`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = '0'
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) <> 'U')
            THEN
                1
            ELSE 0
        END) AS `uninventoried_offline`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = 1
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U')
            THEN
                1
            ELSE 0
        END) AS `inventoried_online`,
        SUM(CASE
            WHEN
                (`machines`.`enabled` = '0'
                    AND SUBSTR(`machines`.`uuid_inventorymachine`,
                    1,
                    1) = 'U')
            THEN
                1
            ELSE 0
        END) AS `inventoried_offline`,
        SUM(CASE
            WHEN `machines`.`id` THEN 1
            ELSE 0
        END) AS `nbmachine`,
        SUM(CASE
            WHEN COALESCE(`machines`.`uuid_serial_machine`, '') <> '' THEN 1
            ELSE 0
        END) AS `with_uuid_serial`,
        SUM(CASE
            WHEN `machines`.`classutil` = 'both' THEN 1
            ELSE 0
        END) AS `bothclass`,
        SUM(CASE
            WHEN `machines`.`classutil` = 'public' THEN 1
            ELSE 0
        END) AS `publicclass`,
        SUM(CASE
            WHEN `machines`.`classutil` = 'private' THEN 1
            ELSE 0
        END) AS `privateclass`,
        SUM(CASE
            WHEN COALESCE(`machines`.`ad_ou_user`, '') <> '' THEN 1
            ELSE 0
        END) AS `nb_ou_user`,
        SUM(CASE
            WHEN COALESCE(`machines`.`ad_ou_machine`, '') <> '' THEN 1
            ELSE 0
        END) AS `nb_OU_mach`,
        SUM(CASE
            WHEN `machines`.`kiosk_presence` = 'True' THEN 1
            ELSE 0
        END) AS `kioskon`,
        SUM(CASE
            WHEN `machines`.`kiosk_presence` = 'FALSE' THEN 1
            ELSE 0
        END) AS `kioskoff`,
        SUM(CASE
            WHEN `machines`.`need_reconf` THEN 1
            ELSE 0
        END) AS `nbmachinereconf`
    FROM
        `machines`
    WHERE
        `machines`.`groupdeploy` IN (SELECT
                `relayserver`.`jid`
            FROM
                `relayserver`)
            AND `machines`.`agenttype` = 'machine'
    GROUP BY `machines`.`groupdeploy`;


    INSERT INTO `xmppmaster`.`support_help_command` (`name`, `description`, `example`, `type`, `result`) VALUES ('vs_stats_ars', 'cette vue donne la répartition des machines pour les ars', ' select * from vs_stats_ars; ', 'V', '*************************** 1. row ***************************\n          groupdeploy: rspulse@pulse/000c29f61ff6\n       nblinuxmachine: 2\n            nbwindows: 1\n             nbdarwin: 0\n              mach_on: 1\n             mach_off: 2\n        uninventoried: 0\n          inventoried: 3\n uninventoried_online: 0\nuninventoried_offline: 0\n   inventoried_online: 1\n  inventoried_offline: 2\n            nbmachine: 3\n     with_uuid_serial: 3\n            bothclass: 3\n          publicclass: 0\n         privateclass: 0\n           nb_ou_user: 0\n           nb_OU_mach: 0\n              kioskon: 0\n             kioskoff: 3\n      nbmachinereconf: 0\n');



SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 63;

COMMIT;
