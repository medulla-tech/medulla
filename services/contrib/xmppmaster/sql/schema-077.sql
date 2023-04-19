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
-- Database xmppmaster add procedure stockee
-- ----------------------------------------------------------------------

START TRANSACTION;

-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
USE `xmppmaster`;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `mmc_view_deployment_status_last_line_of_logs` AS
    SELECT distinct
        `deploy`.`sessionid` AS `sessionid`,
        `deploy`.`title` AS `title`,
        `deploy`.`state` AS `state`,
        FS_JIDUSERTRUE(`deploy`.`jidmachine`) AS `mach`,
        FS_JIDUSERTRUE(`deploy`.`jid_relay`) AS `ars`,
        `logs`.`text` AS `text`,
        `logs`.`date` AS `date`,
        `logs`.`id` AS `id`
    FROM
        (`deploy`
        JOIN `logs` ON (`logs`.`sessionname` = `deploy`.`sessionid`))
    WHERE
        `logs`.`type` = 'deploy'
            AND !( `deploy`.`state` REGEXP '^ABORT DEPLOYMENT CANCELLED|DEPLOYMENT SUCCESS')
            AND !( `logs`.`date` REGEXP '^.*ABORT DEPLOYMENT CANCELLED BY USER.*$')
            AND CURRENT_TIMESTAMP() BETWEEN `deploy`.`startcmd` AND `deploy`.`endcmd`
            AND `deploy`.`title` NOT LIKE 'Convergence%'
            AND `logs`.`id` IN (SELECT
                MAX(`logs`.`id`)
            FROM
                `logs`
            WHERE
                `logs`.`sessionname` = `deploy`.`sessionid`);

-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------

USE `xmppmaster`;
CREATE   OR REPLACE VIEW `mmc_view_deployment_status_last_line_of_logs_convergence` AS
    SELECT
        `deploy`.`sessionid` AS `sessionid`,
        `deploy`.`title` AS `title`,
        `deploy`.`state` AS `state`,
        FS_JIDUSERTRUE(`deploy`.`jidmachine`) AS `mach`,
        FS_JIDUSERTRUE(`deploy`.`jid_relay`) AS `ars`,
        `logs`.`text` AS `text`,
        `logs`.`date` AS `date`,
        `logs`.`id` AS `id`
    FROM
        (`deploy`
        JOIN `logs` ON (`logs`.`sessionname` = `deploy`.`sessionid`))
    WHERE
        `logs`.`type` = 'deploy'
            AND !( `deploy`.`state` REGEXP '^ABORT DEPLOYMENT CANCELLED|DEPLOYMENT SUCCESS')
            AND !( `logs`.`date` REGEXP '^.*ABORT DEPLOYMENT CANCELLED BY USER.*$')
            AND CURRENT_TIMESTAMP() BETWEEN `deploy`.`startcmd` AND `deploy`.`endcmd`
            AND `deploy`.`title` LIKE 'Convergence%'
            AND `logs`.`id` IN (SELECT
                MAX(`logs`.`id`)
            FROM
                `logs`
            WHERE
                `logs`.`sessionname` = `deploy`.`sessionid`);

-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------

USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_delete_blocked_convergence_transfer_error`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_delete_blocked_convergence_transfer_error`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `mmc_delete_blocked_convergence_transfer_error`()
BEGIN
DECLARE finished INTEGER DEFAULT 0;
DECLARE session_string varchar(100) DEFAULT "";
DECLARE machine_name varchar(50) DEFAULT "";
DECLARE ars_name varchar(50) DEFAULT "";
DECLARE title_deploy varchar(100) DEFAULT "";
DECLARE history_log_msg varchar (1024) default "";
DECLARE date_log timestamp default "";
DECLARE id_log varchar (12) default "";
DECLARE message_log varchar (1024) default "";
DECLARE limit_deploy integer default 10000000;
DECLARE nombreselect INTEGER DEFAULT 0;

DECLARE cursor_session_reload CURSOR FOR
	SELECT
		sessionid,title,mach,ars,text,date,id
	from
		mmc_view_deployment_status_last_line_of_logs_convergence
	where
         `mmc_view_deployment_status_last_line_of_logs_convergence`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 1 HOUR;

DECLARE CONTINUE HANDLER
    FOR NOT FOUND SET finished = 1;

OPEN cursor_session_reload;
nextsessionid: LOOP
	FETCH cursor_session_reload INTO session_string,title_deploy,machine_name,ars_name,history_log_msg, date_log, id_log  ;
	IF finished = 1 THEN LEAVE nextsessionid;
	END IF;

    call `mmc_delete_deploy_session_id`(session_string);

	SELECT CONCAT('Delete locked deploy [', title_deploy, '] previous session  ', session_string, ' on machine ', machine_name, ' via relay ', ars_name, ' [blocked on message :', history_log_msg, ' ]')
	INTO message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`)
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
END$$

DELIMITER ;
;

-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------

DROP VIEW IF EXISTS `xmppmaster`.`mmc_view_of_deployments_to_be_relaunched` ;
USE `xmppmaster`;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `mmc_view_of_deployments_to_be_relaunched` AS
    SELECT
        `mmc_view_deployment_status_last_line_of_logs`.`sessionid` AS `sessionid`,
        `mmc_view_deployment_status_last_line_of_logs`.`title` AS `title`,
        `mmc_view_deployment_status_last_line_of_logs`.`state` AS `state`,
        `mmc_view_deployment_status_last_line_of_logs`.`mach` AS `mach`,
        `mmc_view_deployment_status_last_line_of_logs`.`ars` AS `ars`,
        `mmc_view_deployment_status_last_line_of_logs`.`text` AS `text`,
        `mmc_view_deployment_status_last_line_of_logs`.`date` AS `date`,
        `mmc_view_deployment_status_last_line_of_logs`.`id` AS `id`
    FROM
        `mmc_view_deployment_status_last_line_of_logs`
    WHERE

        `mmc_view_deployment_status_last_line_of_logs`.`state` REGEXP 'ERROR TRANSFER FAILED|ERROR UNKNOWN ERROR|ERROR HASH MISSING|ABORT RELAY DOWN|ABORT HASH INVALID'
            OR `mmc_view_deployment_status_last_line_of_logs`.`state` = 'DEPLOYMENT START'
            AND (`mmc_view_deployment_status_last_line_of_logs`.`text` REGEXP '^First WOL|^Second WOL|^Third WOL|.*Trying to continue deployment|Starting deployment|^Key successfully present|^Transfer Method is pullcurl|^File transfer is enabled|^Package server is.*'
            AND `mmc_view_deployment_status_last_line_of_logs`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 900 SECOND
            OR `mmc_view_deployment_status_last_line_of_logs`.`text` REGEXP '^Taking resource'
            AND `mmc_view_deployment_status_last_line_of_logs`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 1 DAY
            OR `mmc_view_deployment_status_last_line_of_logs`.`text` REGEXP '.*Transfer successful'
            AND `mmc_view_deployment_status_last_line_of_logs`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 1 HOUR
            OR `mmc_view_deployment_status_last_line_of_logs`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 1 HOUR)
            OR `mmc_view_deployment_status_last_line_of_logs`.`state` REGEXP 'ABORT TRANSFER FAILED|ABORT PACKAGE EXECUTION ERROR'
            AND `mmc_view_deployment_status_last_line_of_logs`.`text` REGEXP '.*Transfer error .* : curl download.*';

-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------

USE `xmppmaster`;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `xmppmaster`.`mmc_view_select_status_and_last_log` AS
    SELECT DISTINCT
        `xmppmaster`.`deploy`.`state` AS `state`,
        `xmppmaster`.`logs`.`text` AS `text`
    FROM
        (`xmppmaster`.`deploy`
        JOIN `xmppmaster`.`logs` ON (`xmppmaster`.`logs`.`sessionname` = `xmppmaster`.`deploy`.`sessionid`))
    WHERE
        `xmppmaster`.`deploy`.`title` NOT LIKE 'Convergence%'
            AND `xmppmaster`.`logs`.`type` = 'deploy'
            AND CURRENT_TIMESTAMP() BETWEEN `xmppmaster`.`deploy`.`startcmd` AND `xmppmaster`.`deploy`.`endcmd`
            AND `xmppmaster`.`logs`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 900 SECOND
            AND `xmppmaster`.`logs`.`id` IN (SELECT
                MAX(`xmppmaster`.`logs`.`id`)
            FROM
                `xmppmaster`.`logs`
            WHERE
                `xmppmaster`.`logs`.`sessionname` = `xmppmaster`.`deploy`.`sessionid`);

-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------

DROP VIEW IF EXISTS `xmppmaster`.`mmc_view_select_status_and_last_log_time` ;
USE `xmppmaster`;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `xmppmaster`.`mmc_view_select_status_and_last_log_time` AS
    SELECT DISTINCT
        `xmppmaster`.`deploy`.`state` AS `state`,
        `xmppmaster`.`logs`.`text` AS `text`,
        TIMESTAMPDIFF(MINUTE,
            `xmppmaster`.`deploy`.`startcmd`,
            CURRENT_TIMESTAMP()) AS `from_minutes`
    FROM
        (`xmppmaster`.`deploy`
        JOIN `xmppmaster`.`logs` ON (`xmppmaster`.`logs`.`sessionname` = `xmppmaster`.`deploy`.`sessionid`))
    WHERE
        `xmppmaster`.`deploy`.`title` NOT LIKE 'Convergence%'
            AND `xmppmaster`.`logs`.`type` = 'deploy'
            AND CURRENT_TIMESTAMP() BETWEEN `xmppmaster`.`deploy`.`startcmd` AND `xmppmaster`.`deploy`.`endcmd`
            AND `xmppmaster`.`logs`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 900 SECOND
            AND `xmppmaster`.`logs`.`id` IN (SELECT
                MAX(`xmppmaster`.`logs`.`id`)
            FROM
                `xmppmaster`.`logs`
            WHERE
                `xmppmaster`.`logs`.`sessionname` = `xmppmaster`.`deploy`.`sessionid`);


-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------


USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_blocked_deployments`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `mmc_restart_blocked_deployments`(in nombre_reload integer)
BEGIN
DECLARE finished INTEGER DEFAULT 0;
DECLARE session_string varchar(100) DEFAULT "";
DECLARE machine_name varchar(50) DEFAULT "";
DECLARE ars_name varchar(50) DEFAULT "";
DECLARE title_deploy varchar(100) DEFAULT "";
DECLARE history_log_msg varchar (1024) default "";
DECLARE message_log varchar (1024) default "";
DECLARE limit_deploy integer default 10000000;
DECLARE nombreselect INTEGER DEFAULT 0;
DECLARE cursor_session_reload CURSOR FOR
	select
		sessionid,title,mach,ars,text
	from
		xmppmaster.mmc_view_of_deployments_to_be_relaunched
	limit nombre_reload;

DECLARE CONTINUE HANDLER
    FOR NOT FOUND SET finished = 1;
if  nombre_reload != -1 then
    set limit_deploy = nombre_reload;
end if;

OPEN cursor_session_reload;
nextsessionid: LOOP
	FETCH cursor_session_reload INTO session_string,title_deploy,machine_name,ars_name,history_log_msg;
	IF finished = 1 THEN
		LEAVE nextsessionid;
	END IF;

	call `mmc_restart_deploy_sessionid_with_reconf`(session_string, 1, 0);

	SELECT
			CONCAT('Restarting deployment [',
					title_deploy,
					'] previous session  ',
					session_string,
					' on machine ',
					machine_name,
					' via relay ',
					ars_name,
					' [blocked on message :',
					history_log_msg,
					' ]')
		INTO message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`)
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
END$$

DELIMITER ;
;


-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------

USE `xmppmaster`;
CREATE
     OR REPLACE ALGORITHM = UNDEFINED
    DEFINER = `root`@`localhost`
    SQL SECURITY DEFINER
VIEW `mmc_view_restart_blocked_deployments_transfer_error` AS
    SELECT
        `mmc_view_deployment_status_last_line_of_logs`.`sessionid` AS `sessionid`,
        `mmc_view_deployment_status_last_line_of_logs`.`title` AS `title`,
        `mmc_view_deployment_status_last_line_of_logs`.`state` AS `state`,
        `mmc_view_deployment_status_last_line_of_logs`.`mach` AS `mach`,
        `mmc_view_deployment_status_last_line_of_logs`.`ars` AS `ars`,
        `mmc_view_deployment_status_last_line_of_logs`.`text` AS `text`,
        `mmc_view_deployment_status_last_line_of_logs`.`date` AS `date`,
        `mmc_view_deployment_status_last_line_of_logs`.`id` AS `id`
    FROM
        `mmc_view_deployment_status_last_line_of_logs`
    WHERE
        `mmc_view_deployment_status_last_line_of_logs`.`state` REGEXP '^TRANSFER ERROR|TRANSFER FAILED$|ERROR HASH MISSING$'
            AND `mmc_view_deployment_status_last_line_of_logs`.`date` < CURRENT_TIMESTAMP() + INTERVAL - 1 HOUR;

-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------


USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_restart_blocked_deployments_transfer_error`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_blocked_deployments_transfer_error`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `mmc_restart_blocked_deployments_transfer_error`(in nombre_reload integer)
BEGIN
DECLARE finished INTEGER DEFAULT 0;
DECLARE session_string varchar(100) DEFAULT "";
DECLARE machine_name varchar(50) DEFAULT "";
DECLARE ars_name varchar(50) DEFAULT "";
DECLARE title_deploy varchar(100) DEFAULT "";
DECLARE history_log_msg varchar (1024) default "";
DECLARE date_log timestamp default "";
DECLARE id_log varchar (12) default "";
DECLARE message_log varchar (1024) default "";
DECLARE limit_deploy integer default 10000000;
DECLARE nombreselect INTEGER DEFAULT 0;
DECLARE cursor_session_reload CURSOR FOR
	SELECT
		sessionid,title,mach,ars,text,date,id
	from
		mmc_view_restart_blocked_deployments_transfer_error
	limit nombre_reload;
 DECLARE CONTINUE HANDLER
    FOR NOT FOUND SET finished = 1;

call  mmc_delete_blocked_convergence_transfer_error ();
if  nombre_reload != -1 then
    set limit_deploy = nombre_reload;
end if;

OPEN cursor_session_reload;
nextsessionid: LOOP
	FETCH cursor_session_reload INTO session_string,title_deploy,machine_name,ars_name,history_log_msg, date_log, id_log  ;
	IF finished = 1 THEN LEAVE nextsessionid;
	END IF;
	set nombreselect = nombreselect + 1;
    -- reconf machine pour refaire deployement
	call `mmc_restart_deploy_sessionid_with_reconf`(session_string, 1, 0);
	SELECT
    CONCAT('Restarting deployment [',
            title_deploy,
            '] previous session  ',
            session_string,
            ' on machine ',
            machine_name,
            ' via relay ',
            ars_name,
            ' [blocked on message :',
            history_log_msg,
            ' ]')
INTO message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`)
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
SELECT nombreselect;
END$$

DELIMITER ;
;


-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------
-- ------------------------------------------------------------------------


USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_restart_deploy_sessionid_with_reconf`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_deploy_sessionid_with_reconf`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `mmc_restart_deploy_sessionid_with_reconf`(IN IN_sessid VARCHAR(255), in force_redeploy integer, in rechedule_deploy integer)
BEGIN
-- cette procedure stockee restart le deployement de session id input
-- ON lance 1 reconf de la machine sur laquel le deployement est demande.
-- on rechedule le debut du deployement a time_waitting_reconf en minutes
-- cela pour permettre que la reconf soit faite.

SET @ignorestatus0 = "DEPLOYMENT SUCCESS";
SET @ignorestatus1 = "WAITING MACHINE ONLINE";
set @total = 0;
SET @time_waitting_reconf = 15;
 IF force_redeploy > 0 THEN
	set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid limit 1);
 else
     set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid and state not in (@ignorestatus0,@ignorestatus1) limit 1);
 END IF;
 SELECT  COUNT(*) from    xmppmaster.deploy  where sessionid like IN_sessid into @total;
if @total != 0 THEN
	set @grp = (select group_uuid from xmppmaster.deploy where sessionid like IN_sessid limit 1);
    set @name_mach = (select FS_JIDUSERTRUE(host) as host from  xmppmaster.deploy where sessionid like IN_sessid limit 1);
    set @fk_commands_on_host = (select id from msc.commands_on_host where FS_JIDUSERTRUE(host)=@name_mach and fk_commands = @cmd limit 1);
    DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
	DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
    IF rechedule_deploy > 0 THEN
	   UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` =  @cmd);
	END IF;
	UPDATE `msc`.`commands` SET `start_date` = now() + INTERVAL @time_waitting_recong MINUTE WHERE (`id` =  @cmd);

    UPDATE `xmppmaster`.`machines` SET `need_reconf` = '1' WHERE (`hostname` like @name_mach);
    UPDATE `msc`.`phase` SET `state` = 'ready' WHERE (`msc`.`phase`.`fk_commands_on_host` = @fk_commands_on_host );
 END IF;
END$$

DELIMITER ;
;

-- -----------------------------------------------------------------------------------------------------------
-- -----------------------------------------------------------------------------------------------------------
-- -----------------------------------------------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 75;

COMMIT;
