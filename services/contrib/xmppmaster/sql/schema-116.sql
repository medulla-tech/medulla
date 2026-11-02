-- SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-116.sql
--
-- Retry missing dependencies, including convergence deployments.
-- Convergence transfer failures remain excluded from retries and retain
-- their existing cleanup. Keep the deployment window, ten-minute delay
-- and latest-log cancellation guard.

USE `xmppmaster`;

START TRANSACTION;

DROP PROCEDURE IF EXISTS `mmc_restart_blocked_deployments_transfer_error`;

DELIMITER $$
CREATE PROCEDURE `mmc_restart_blocked_deployments_transfer_error`(IN nombre_reload INTEGER)
BEGIN
    DECLARE finished INTEGER DEFAULT 0;
    DECLARE session_string VARCHAR(100) DEFAULT "";
    DECLARE machine_name VARCHAR(50) DEFAULT "";
    DECLARE ars_name VARCHAR(50) DEFAULT "";
    DECLARE title_deploy VARCHAR(100) DEFAULT "";
    DECLARE history_log_msg VARCHAR(1024) DEFAULT "";
    DECLARE date_log TIMESTAMP DEFAULT NULL;
    DECLARE id_log VARCHAR(12) DEFAULT "";
    DECLARE message_log VARCHAR(1024) DEFAULT "";
    DECLARE limit_deploy INTEGER DEFAULT 10000000;
    DECLARE nombreselect INTEGER DEFAULT 0;
    DECLARE cursor_session_reload CURSOR FOR
        SELECT DISTINCT
            `xmppmaster`.`deploy`.sessionid,
            `xmppmaster`.`deploy`.title,
            fs_jidusertrue(`xmppmaster`.`deploy`.jidmachine),
            fs_jidusertrue(`xmppmaster`.`deploy`.jid_relay),
            newtablelog.text,
            newtablelog.date,
            newtablelog.id
        FROM xmppmaster.deploy
        JOIN (
            SELECT aaa.id, aaa.text, aaa.sessionname, aaa.date
            FROM logs aaa
            INNER JOIN (
                SELECT *, MAX(id) AS ddddd
                FROM logs
                GROUP BY sessionname
            ) AS bbb
                ON aaa.sessionname = bbb.sessionname
                AND aaa.id = bbb.ddddd
        ) newtablelog ON newtablelog.sessionname = deploy.sessionid
        WHERE
            (
                (
                    deploy.state REGEXP 'TRANSFER FAILED$'
                    AND deploy.title NOT REGEXP '^Convergence'
                )
                -- Missing dependencies are retryable even for convergence.
                OR deploy.state = 'ABORT MISSING DEPENDENCY'
            )
            AND (NOW() BETWEEN deploy.startcmd AND deploy.endcmd)
            AND (
                newtablelog.text NOT REGEXP '^.*ABORT DEPLOYMENT CANCELLED BY USER.*$'
                AND newtablelog.date < DATE_ADD(NOW(), INTERVAL - 600 SECOND)
            )
        LIMIT nombre_reload;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished = 1;

    CALL mmc_delete_blocked_convergence_transfer_error();
    IF nombre_reload != -1 THEN
        SET limit_deploy = nombre_reload;
    END IF;

    OPEN cursor_session_reload;
    nextsessionid: LOOP
        FETCH cursor_session_reload
            INTO session_string, title_deploy, machine_name,
                 ars_name, history_log_msg, date_log, id_log;
        IF finished = 1 THEN
            LEAVE nextsessionid;
        END IF;
        SET nombreselect = nombreselect + 1;
        CALL `mmc_restart_deploy_sessionid`(session_string, 1, 0);
        SELECT CONCAT(
            'Restarting deployment [', title_deploy,
            '] previous session  ', session_string,
            ' on machine ', machine_name, ' via relay ', ars_name,
            ' [blocked on message :', history_log_msg, ' ]'
        ) INTO message_log;
        INSERT INTO `xmppmaster`.`logs`
            (`type`, `module`, `text`, `fromuser`, `touser`,
             `action`, `sessionname`, `priority`, `who`)
        VALUES
            ('deploy', 'Deployment | Restart | Notify', message_log,
             'mysql', 'admin', 'xmpplog', 'command...', '-1', 'mysql');
    END LOOP nextsessionid;
    CLOSE cursor_session_reload;
    SELECT nombreselect;
END$$
DELIMITER ;

UPDATE qa_custom_command
SET customcmd = 'powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Select-Object HandleCount,Name,Priority,ProcessId,ThreadCount,WorkingSetSize | Format-Table -AutoSize"',
    description = 'Get list of processes with PowerShell CIM'
WHERE `user` = 'allusers'
  AND os = 'windows'
  AND namecmd = 'Show process List'
  AND customcmd = 'wmic process list brief';

UPDATE qa_custom_command
SET customcmd = 'powershell.exe -NoProfile -Command "Get-CimInstance Win32_Service | Select-Object ExitCode,Name,ProcessId,StartMode,State,Status | Format-Table -AutoSize"'
WHERE `user` = 'allusers'
  AND os = 'windows'
  AND namecmd = 'Show services List'
  AND customcmd = 'wmic service list brief';

UPDATE qa_custom_command
SET customcmd = 'powershell.exe -NoProfile -Command "Get-CimInstance Win32_ComputerSystem | Select-Object UserName | Format-Table -AutoSize"'
WHERE `user` = 'allusers'
  AND os = 'windows'
  AND namecmd = 'Show connected users list'
  AND customcmd = 'wmic computersystem get username';

UPDATE version SET Number = 116;

COMMIT;
