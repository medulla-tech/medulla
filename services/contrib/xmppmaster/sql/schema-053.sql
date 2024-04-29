--
-- (c) 2020 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Medulla 2, http://www.siveo.net/
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

START TRANSACTION;

USE `xmppmaster`;

insert into qa_relay_command(user, name, script, description) VALUES
('allusers', 'show relay logs', 'tail -n200 /var/log/medulla/xmpp-agent-relay.log', 'Show last 200 lines of relay logs'),
('allusers', 'list network connections', 'netstat -vapn', 'Get list of network connections and ports'),
('allusers', 'restart relay agent', 'systemctl restart medulla-agent-relay.service', 'Restart Medulla Relay service'),
('allusers', 'show system status', 'top -b -n 1 -o %MEM -c -w 512', 'Show detailed system status'),
('allusers', 'show routing table', 'netstat -rn', 'Show the IP routing table'),
('allusers', 'show disk space', 'df -h', 'Show free disk space');

UPDATE `qa_custom_command` SET `customcmd`='for /F %A in (C:\\Python27\\Lib\\site-packages\\medulla_agent\\INFOSTMP\\pidagent) do taskkill /PID %A /F' WHERE `namecmd`='Restart Medulla Agent service' AND `os`='windows';

UPDATE version SET Number = 53;

COMMIT;
