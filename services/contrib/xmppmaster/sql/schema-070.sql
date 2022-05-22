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
-- Database xmppmaster
-- ----------------------------------------------------------------------

START TRANSACTION;

USE `xmppmaster`;
DROP function IF EXISTS `fs_jidusertrue`;

USE `xmppmaster`;
DROP function IF EXISTS `xmppmaster`.`fs_jidusertrue`;

DELIMITER $$
USE `xmppmaster`$$
CREATE FUNCTION `fs_jidusertrue`(jid char(255)) RETURNS char(255) CHARSET utf8
BEGIN
RETURN  substring_index(substring_index(jid, '@', 1), '.', 1);
END$$

DELIMITER ;


-- ----------------------------------------------------------------------
-- index
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`deploy`
ADD INDEX `ind_title` (`title` ASC) ;



-- ----------------------------------------------------------------------
-- mmc_delete_deploy_session_id stored procedure
-- -----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_delete_deploy_session_id`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_delete_deploy_session_id`;
;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mmc_delete_deploy_session_id`(IN IN_sessid VARCHAR(255))
BEGIN
-- cette procedure supprime les deployement dans la table log et deploysuivant la session passe.
-- delete log information
DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
END$$

DELIMITER ;
;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_delete_blocked_convergence`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mmc_delete_blocked_convergence`()
BEGIN
-- Cette procedure supprime de la table delpoy et de la table log
-- les deployements appartenant a une 1 Convergence restant bloque
-- les deployement supprimer ne sont pas relance.
-- les deployements seront relancé par la convergence planifier.

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
SELECT DISTINCT
    `xmppmaster`.`deploy`.sessionid,
	`xmppmaster`.`deploy`.title,
	fs_jidusertrue( `xmppmaster`.`deploy`.jidmachine),
	fs_jidusertrue( `xmppmaster`.`deploy`.jid_relay),
	`xmppmaster`.`logs`.text
FROM
    xmppmaster.deploy
JOIN
    logs ON logs.sessionname = deploy.sessionid
WHERE
    deploy.title  like "Convergence%"
    AND deploy.state = 'DEPLOYMENT START'
	AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
	AND sessionname = deploy.sessionid
	AND ((logs.text REGEXP '^First WOL|^Second WOL|^Third WOL|.*Trying to continue deployment|Starting deployment|^Key successfully present'
	AND logs.date < DATE_ADD(NOW(), INTERVAL - 600 SECOND))
	OR (logs.text REGEXP '^Client generated transfer command is'
	AND logs.date < DATE_ADD(NOW(), INTERVAL - 1 DAY)))
GROUP BY deploy.sessionid ;
-- declare NOT FOUND handler
DECLARE CONTINUE HANDLER
	FOR NOT FOUND SET finished = 1;
# pour chaque result appeler reload deploy
OPEN cursor_session_reload;
nextsessionid: LOOP
	FETCH cursor_session_reload INTO session_string, title_deploy,machine_name, ars_name,history_log_msg;
	IF finished = 1 THEN LEAVE nextsessionid;
	END IF;
	call `mmc_delete_deploy_session_id`(session_string);
	-- create message log
	SELECT CONCAT("Delete locked deploy   [", title_deploy, "] previous session  ", session_string, " on machine ", machine_name , " [blocked on message :", history_log_msg, " ]")
	INTO message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`) 
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
END$$

DELIMITER ;


-- ----------------------------------------------------------------------
-- mmc_restart_deploy_sessionid stored procedure
-- -----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_restart_deploy_sessionid`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_deploy_sessionid`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mmc_restart_deploy_sessionid`(IN IN_sessid VARCHAR(255), in force_redeploy integer, in rechedule_deploy integer)
BEGIN
-- parameters
-- IN_sessid session id deployement
-- force_redeploy = 1 do not consider ignored status (variable: ignorestatus)
-- rechedule_deploy = 1 Replan the deploiements betwenn not and 1 day
-- TODO: Update the list on which we forbid redeploy.
SET @ignorestatus0 = "DEPLOYMENT SUCCESS";
SET @ignorestatus1 = "WAITING MACHINE ONLINE";
set @total = 0;
 IF force_redeploy > 0 THEN
	set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid limit 1);
 else
     set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid and state not in (@ignorestatus0,@ignorestatus1) limit 1);
 END IF;
 SELECT  COUNT(*) from    xmppmaster.deploy  where sessionid like IN_sessid into @total;
if @total != 0 THEN
	set @grp = (select group_uuid from  xmppmaster.deploy where sessionid like IN_sessid limit 1);
    set @name_mach = (select FS_JIDUSERTRUE(host) as host from  xmppmaster.deploy where sessionid like IN_sessid limit 1);
    set @fk_commands_on_host = (select id from msc.commands_on_host where FS_JIDUSERTRUE(host)=@name_mach and fk_commands = @cmd limit 1);
    DELETE FROM `xmppmaster`.`logs` WHERE (`sessionname` like IN_sessid);
	DELETE FROM `xmppmaster`.`deploy` WHERE (`sessionid` like IN_sessid);
    IF rechedule_deploy > 0 THEN
	   -- sinon recreation des deployement avec meme planification.
	   -- rechedule_deploy is 1 on s assure que le deployement soit rejoue quelque soit sa planification.
	   UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` =  @cmd); -- and  NOW() > end_date;
	END IF;
    UPDATE `msc`.`phase` SET `state` = 'ready' WHERE (`msc`.`phase`.`fk_commands_on_host` = @fk_commands_on_host );
 END IF;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- mmc_restart_deploy_cmdid stored procedure
-- -----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_restart_deploy_cmdid`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_deploy_cmdid`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mmc_restart_deploy_cmdid`(in cmd_id integer, in force_redeploy integer, in rechedule_deploy integer)
BEGIN
set @total = 0;
-- TODO: Update the list on which we forbid redeploy.
SET @ignorestatus = "'DEPLOYMENT SUCCESS','WAITING MACHINE ONLINE'";

-- parameters
-- cmd_id command the msc id of the group or the individual machine.
-- force_redeploy = 1 do not consider ignored status (variable: ignorestatus)
-- rechedule_deploy = 1 Replan the deploiements betwenn not and 1 day

IF force_redeploy > 0 THEN
	 SET @s = CONCAT("CREATE TEMPORARY TABLE list_sessio_id SELECT FS_JIDUSERTRUE(host) as host, sessionid FROM xmppmaster.deploy where command = " , cmd_id);
else
   SET @s = CONCAT("CREATE TEMPORARY TABLE list_sessio_id SELECT  FS_JIDUSERTRUE(host) as host,sessionid FROM xmppmaster.deploy where command = " ,cmd_id, " and state not in (", @ignorestatus,")" );
 END IF;
PREPARE stmt FROM @s;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

 SELECT
    COUNT(*)
 FROM
   list_sessio_id into @total;
  if @total != 0 THEN
	-- temporary table list_sessio_id content session_id for restart deploiement
	-- DELETE FROM `xmppmaster`.`logs` WHERE	`sessionname` IN (SELECT sessionid FROM list_sessio_id);
	-- the deploiements does not exit anymore.
	 DELETE FROM `xmppmaster`.`deploy` WHERE `sessionid` IN (SELECT sessionid	FROM list_sessio_id);

	 IF rechedule_deploy > 0 THEN
       -- If not, we create the deploiements with the same date/hour.
       -- rechedule_deploy is 1:  we make sure that that the deploiement is replayed whenever it is planned.
	    UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` = cmd_id); -- and  NOW() > end_date;
	 END IF;

    -- we calculate all the commands_on_host id fields and we list the selected sessions.
	CREATE TEMPORARY TABLE `commands_on_host_id`  SELECT id FROM msc.commands_on_host
       JOIN list_sessio_id ON list_sessio_id.host = FS_JIDUSERTRUE(msc.commands_on_host.host)
	 WHERE msc.commands_on_host.fk_commands = cmd_id;

	 UPDATE `msc`.`phase` SET `state` = 'ready' WHERE  `msc`.`phase`.`fk_commands_on_host` IN (select id from `commands_on_host_id` );
  END IF;
drop table IF EXISTS list_sessio_id;
drop table IF EXISTS commands_on_host_id;
END$$

DELIMITER ;


-- ----------------------------------------------------------------------
-- stored procedure  mmc_restart_blocked_deployments
-- -----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_restart_blocked_deployments`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_blocked_deployments`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mmc_restart_blocked_deployments`( in nombre_reload integer)
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
-- deploy list fields :'id,title,jidmachine,jid_relay,pathpackage,state,sessionid,start,startcmd,endcmd,inventoryuuid,host,user,command,group_uuid,login,macadress,syncthing,result,subdep'
-- logs list fields :' id,date,type,module,text,fromuser,touser,action,sessionname,how,why,priority,who'

SELECT DISTINCT
    `xmppmaster`.`deploy`.sessionid,
	`xmppmaster`.`deploy`.title,
    fs_jidusertrue( `xmppmaster`.`deploy`.jidmachine),
    fs_jidusertrue( `xmppmaster`.`deploy`.jid_relay),
    `xmppmaster`.`logs`.text
FROM
    xmppmaster.deploy
JOIN
    logs ON logs.sessionname = deploy.sessionid
WHERE
    deploy.title  NOT like "Convergence%"
	AND deploy.state = 'DEPLOYMENT START'
	AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
	AND sessionname = deploy.sessionid
	AND ((logs.text REGEXP '^First WOL|^Second WOL|^Third WOL|.*Trying to continue deployment|Starting deployment|^Key successfully present'
	AND logs.date < DATE_ADD(NOW(), INTERVAL - 600 SECOND))
	OR (logs.text REGEXP '^Taking resource'
	AND logs.date < DATE_ADD(NOW(), INTERVAL - 1 DAY)))
GROUP BY deploy.sessionid limit nombre_reload;
-- declare NOT FOUND handler
DECLARE CONTINUE HANDLER
    FOR NOT FOUND SET finished = 1;
if  nombre_reload != -1 then
    set limit_deploy = nombre_reload;
end if;
# pour chaque result appeler reload deploy
OPEN cursor_session_reload;
nextsessionid: LOOP
	FETCH cursor_session_reload INTO session_string,title_deploy,machine_name,ars_name,history_log_msg;
	IF finished = 1 THEN
	LEAVE nextsessionid;
	END IF;
	-- count
	set nombreselect = nombreselect + 1;
	-- call reload deployement
	call `mmc_restart_deploy_sessionid`(session_string, 1, 0);
	-- create message log
	SELECT CONCAT("Restarting deployment [", title_deploy, "] previous session  ", session_string, " on machine ", machine_name , " via relay ", ars_name, " [blocked on message :", history_log_msg, " ]") 
	INTO  message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`)
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
select nombreselect;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- stored procedure  mmc_delete_blocked_convergence_transfer_error
-- Delete deployments blocked in states ERROR TRANSFER FAILED and ERROR TRANSFER FAILED 
-- coming from a convergence
-- -----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_delete_blocked_convergence_transfer_error`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_delete_blocked_convergence_transfer_error`;

DELIMITER $$
USE `xmppmaster`$$
CREATE  PROCEDURE `mmc_delete_blocked_convergence_transfer_error`()
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
-- deploy list fields :'id,title,jidmachine,jid_relay,pathpackage,state,sessionid,start,startcmd,endcmd,inventoryuuid,host,user,command,group_uuid,login,macadress,syncthing,result,subdep'
-- logs list fields :' id,date,type,module,text,fromuser,touser,action,sessionname,how,why,priority,who'
-- delete deployement en etat ERROR TRANSFER FAILED et ERROR TRANSFER FAILED bloquee
-- issu d une convergence
SELECT DISTINCT
	`xmppmaster`.`deploy`.sessionid,
	`xmppmaster`.`deploy`.title,
	fs_jidusertrue( `xmppmaster`.`deploy`.jidmachine),
	fs_jidusertrue( `xmppmaster`.`deploy`.jid_relay),
	newtablelog.text,
	newtablelog.date,
	newtablelog.id
FROM
    xmppmaster.deploy
        JOIN
    (SELECT
        aaa.id, aaa.text, aaa.sessionname, aaa.date
    FROM
        logs aaa
    INNER JOIN (SELECT
        *, MAX(id) AS ddddd
    FROM
        logs
    GROUP BY sessionname) AS bbb ON aaa.sessionname = bbb.sessionname
        AND aaa.id = bbb.ddddd) newtablelog ON newtablelog.sessionname = deploy.sessionid
WHERE
    deploy.state REGEXP 'TRANSFER FAILED$'
	AND deploy.title LIKE 'Convergence%'
	AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
	AND (newtablelog.text NOT REGEXP '^.*ABORT DEPLOYMENT CANCELLED BY USER.*$'
	AND newtablelog.date < DATE_ADD(NOW(), INTERVAL - 1 HOUR));
-- declare NOT FOUND handler
DECLARE CONTINUE HANDLER
    FOR NOT FOUND SET finished = 1;

OPEN cursor_session_reload;
nextsessionid: LOOP
	FETCH cursor_session_reload INTO session_string,title_deploy,machine_name,ars_name,history_log_msg, date_log, id_log  ;
	IF finished = 1 THEN LEAVE nextsessionid;
	END IF;
	-- count
	set nombreselect = nombreselect + 1;
	-- call reload deployement
    call `mmc_delete_deploy_session_id`(session_string);
	-- create message log
	SELECT CONCAT('Delete locked deploy [', title_deploy, '] previous session  ', session_string, ' on machine ', machine_name, ' via relay ', ars_name, ' [blocked on message :', history_log_msg, ' ]')
	INTO message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`)
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- stored procedure  mmc_restart_blocked_deployments_transfer_error
-- Selects deployments in states ERROR TRANSFER FAILED and ERROR TRANSFER FAILED
-- Remark: Deployments coming from convergence are ignored
-- -----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_restart_blocked_deployments_transfer_error`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_blocked_deployments_transfer_error`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mmc_restart_blocked_deployments_transfer_error`(in nombre_reload integer)
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
-- deploy list fields :'id,title,jidmachine,jid_relay,pathpackage,state,sessionid,start,startcmd,endcmd,inventoryuuid,host,user,command,group_uuid,login,macadress,syncthing,result,subdep'
-- logs list fields :' id,date,type,module,text,fromuser,touser,action,sessionname,how,why,priority,who'
-- selectionne n deploiement bloque sur les etat  ERROR TRANSFER FAILED et ERROR TRANSFER FAILED
-- remarque les deploiements issus de convergence sont ignore
     
SELECT DISTINCT
	`xmppmaster`.`deploy`.sessionid,
	`xmppmaster`.`deploy`.title,
	fs_jidusertrue( `xmppmaster`.`deploy`.jidmachine),
	fs_jidusertrue( `xmppmaster`.`deploy`.jid_relay),
	newtablelog.text,
	newtablelog.date,
	newtablelog.id
FROM
    xmppmaster.deploy
        JOIN
    (SELECT 
        aaa.id, aaa.text, aaa.sessionname, aaa.date
    FROM
        logs aaa
    INNER JOIN (SELECT 
        *, MAX(id) AS ddddd
    FROM
        logs
    GROUP BY sessionname) AS bbb ON aaa.sessionname = bbb.sessionname
        AND aaa.id = bbb.ddddd) newtablelog ON newtablelog.sessionname = deploy.sessionid
WHERE
    deploy.state REGEXP 'TRANSFER FAILED$'
	AND deploy.title NOT REGEXP '^Convergence'
	AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
	AND (newtablelog.text NOT REGEXP '^.*ABORT DEPLOYMENT CANCELLED BY USER.*$'
	AND newtablelog.date < DATE_ADD(NOW(), INTERVAL - 600 SECOND))
LIMIT nombre_reload;
-- declare NOT FOUND handler
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
	-- count
	set nombreselect = nombreselect + 1;
	-- call reload deployement
	call `mmc_restart_deploy_sessionid`(session_string, 1, 0);
	-- create message log
	SELECT CONCAT('Restarting deployment [', title_deploy, '] previous session  ', session_string, ' on machine ', machine_name, ' via relay ', ars_name, ' [blocked on message :', history_log_msg, ' ]') 
	INTO message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`)
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
SELECT nombreselect;
END$$

DELIMITER ;



-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 70;

COMMIT;
