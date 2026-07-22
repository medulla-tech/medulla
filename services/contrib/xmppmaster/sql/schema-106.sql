--
-- (c) 2026, http://www.medulla-tech.io/
--
-- FILE contrib/xmppmaster/sql/schema-106.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- Renommage du Label LaunchDaemon macOS
--

START TRANSACTION;

USE `xmppmaster`;

-- Restart Mac via /usr/local/bin/medulla-restart (et pas un bare launchctl kickstart)
-- car kickstart ne tue pas les enfants agentxmpp.py du launcher : ils survivent en
-- orphelins et se battent pour la session XMPP -> loop / "Agent installed is different".
-- medulla-restart fait killall -9 Python avant kickstart pour eviter ce cas.
UPDATE qa_custom_command
SET customcmd = '/usr/local/bin/medulla-restart',
    namecmd = 'Restart Medulla Agent service',
    description = 'Restart Medulla Agent macos service'
WHERE os = 'macos'
  AND namecmd = 'Restart Pulse Agent service';

-- Migration des chemins de log macOS : ancien chemin Pulse vers le nouveau /var/log/medulla/
-- Touche "Download agent log to file-transfer folder" + "Show last 100 lines of agent logs".
UPDATE qa_custom_command
SET customcmd = REPLACE(customcmd,
                        '/Library/Application Support/Pulse/var/log/xmpp-agent-machine.log',
                        '/var/log/medulla/medulla-agent.log')
WHERE os = 'macos'
  AND customcmd LIKE '%/Library/Application Support/Pulse/var/log/xmpp-agent-machine.log%';

UPDATE version SET Number = 106;

commit;