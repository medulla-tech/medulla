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
-- procedure stockee  mmc_restart_deploy_sessionid
- -----------------------------------------------------------------------
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
-- force_redeploy = 1 ne tient pas compte des états a ignorée (variable ignorestatus)
-- rechedule_deploy = 1 replanifie ledeployment entre maintenant et 1 jour
-- list a mettre a jour pour interdir le redoployement sur ces etats
SET @ignorestatus0 = "DEPLOYMENT SUCCESS";
SET @ignorestatus1 = "WAITING MACHINE ONLINE";
set @total = 0;
 IF force_redeploy > 0 THEN
 	set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid);
 else
     set @cmd = (select command from  xmppmaster.deploy where sessionid like IN_sessid and state not in (@ignorestatus0,@ignorestatus1));
 END IF;
 SELECT  @total:=COUNT(*) from    xmppmaster.deploy  where sessionid like IN_sessid;
if @total != 0 THEN
	set @grp = (select group_uuid from  xmppmaster.deploy where sessionid like IN_sessid );
    set @name_mach = (select FS_JIDUSERTRUE(host) as host from  xmppmaster.deploy where sessionid like IN_sessid );
    set @fk_commands_on_host = (select id from msc.commands_on_host where FS_JIDUSERTRUE(host)=@name_mach and fk_commands = @cmd);
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
-- procedure stockee  mmc_restart_deploy_cmdid
- -----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `mmc_restart_deploy_cmdid`;

USE `xmppmaster`;
DROP procedure IF EXISTS `xmppmaster`.`mmc_restart_deploy_cmdid`;

DELIMITER $$
USE `xmppmaster`$$
CREATE PROCEDURE `mmc_restart_deploy_cmdid`(in cmd_id integer, in force_redeploy integer, in rechedule_deploy integer)
BEGIN
set @total = 0;
-- list a mettre a jour pour interdir le redoployement sur ces etats
SET @ignorestatus = "'DEPLOYMENT SUCCESS','WAITING MACHINE ONLINE'";

-- parameters
-- cmd_id command id msc groupe ou machine individuel
-- force_redeploy = 1 ne tient pas compte des états a ignorée (variable ignorestatus)
-- rechedule_deploy = 1 replanifie ledeployment entre maintenant et 1 jour
IF force_redeploy > 0 THEN
	 SET @s = CONCAT("CREATE TEMPORARY TABLE list_sessio_id SELECT FS_JIDUSERTRUE(host) as host, sessionid FROM xmppmaster.deploy where command = " , cmd_id);
else
   SET @s = CONCAT("CREATE TEMPORARY TABLE list_sessio_id SELECT  FS_JIDUSERTRUE(host) as host,sessionid FROM xmppmaster.deploy where command = " ,cmd_id, " and state not in (", @ignorestatus,")" );
 END IF;
PREPARE stmt FROM @s;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

 SELECT
    @total:=COUNT(*)
 FROM
   list_sessio_id;

  if @total != 0 THEN
	-- temporary table list_sessio_id content session_id for restart deploiement
	-- DELETE FROM `xmppmaster`.`logs` WHERE	`sessionname` IN (SELECT sessionid FROM list_sessio_id);
	-- les deploy n'existent plus
	 DELETE FROM `xmppmaster`.`deploy` WHERE `sessionid` IN (SELECT sessionid	FROM list_sessio_id);

	 IF rechedule_deploy > 0 THEN
	   -- sinon recreation des deployement avec meme planification.
	   -- rechedule_deploy is 1 on s assure que le deployement soit rejoue quelque soit sa planification. call
	    UPDATE `msc`.`commands` SET `end_date` = now() + INTERVAL 1 DAY WHERE (`id` = cmd_id); -- and  NOW() > end_date;
	 END IF;

    -- on calcule tout les commands_on_host id a relancer depuis command et la liste de session selectionner.
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
-- procedure stockee  mmc_restart_blocked_deployments
- -----------------------------------------------------------------------
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
    deploy.state = 'DEPLOYMENT START'
        AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
        AND sessionname = deploy.sessionid
        AND ((logs.text REGEXP '^First WOL|^Second WOL|^Third WOL|.*Trying to continue deployment|Starting deployment$|^Key successfully present'
        AND logs.date < DATE_ADD(NOW(), INTERVAL - 600 SECOND))
        OR (logs.text REGEXP '^Client generated transfer command is'
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
		FETCH cursor_session_reload INTO session_string, title_deploy,machine_name, ars_name,history_log_msg;
		IF finished = 1 THEN
			LEAVE nextsessionid;
		END IF;
        -- count
        set nombreselect = nombreselect + 1;
		-- call reload deployement
		call `mmc_restart_deploy_sessionid`(session_string, 1, 0);
        -- create message log
        select concat("Restarting deployment [",
                       title_deploy,
                       "] previous session  ",
                       session_string,
                       " on machine ",
                       machine_name ,
                       " via relay ",
                       ars_name,
                       " [blocked on message :",
                       history_log_msg,
                       " ]"
                       ) into  message_log;
         INSERT INTO `xmppmaster`.`logs` (`type`,
										 `module`,
										 `text`,
										 `fromuser`,
										 `touser`,
										 `action`,
										 `sessionname`,
										 `priority`,
										 `who`) VALUES
										 ('deploy',
										 'Deployment | Restart | Notify',
										 message_log,
										 'mysql',
										 'admin',
										 'xmpplog',
										 'command...',
										 '-1',
										 'mysql');
	END LOOP nextsessionid;
	CLOSE cursor_session_reload;
    select nombreselect;
END$$

DELIMITER ;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 70;

COMMIT;
