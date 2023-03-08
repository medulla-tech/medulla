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
-- Database procedure stockee mmc_restart_blocked_deployments_transfer_error
-- ----------------------------------------------------------------------

START TRANSACTION;

USE `xmppmaster`;
SET FOREIGN_KEY_CHECKS=0;


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
DECLARE date_log timestamp default now();
DECLARE id_log varchar (12) default "";
DECLARE message_log varchar (1024) default "";
DECLARE limit_deploy integer default 10000000;
DECLARE nombreselect INTEGER DEFAULT 0;
DECLARE cursor_session_reload CURSOR FOR

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

	call `mmc_restart_deploy_sessionid`(session_string, 1, 0);

	SELECT CONCAT('Restarting deployment [', title_deploy, '] previous session  ', session_string, ' on machine ', machine_name, ' via relay ', ars_name, ' [blocked on message :', history_log_msg, ' ]')
	INTO message_log;
	INSERT INTO `xmppmaster`.`logs` (`type`, `module`, `text`, `fromuser`, `touser`, `action`, `sessionname`, `priority`, `who`)
	VALUES ('deploy', 'Deployment | Restart | Notify', message_log, 'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
END LOOP nextsessionid;
CLOSE cursor_session_reload;
SELECT nombreselect;
END$$

DELIMITER ;


SET FOREIGN_KEY_CHECKS=1;
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 76;

COMMIT;
