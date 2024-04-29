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

UPDATE `qa_custom_command` SET `customcmd`='plugin_downloadfile@_@/var/log/medulla/xmpp-agent-machine.log' WHERE `namecmd`='Download agent log to file-transfer folder' AND `os`='linux';
UPDATE `qa_custom_command` SET `customcmd`='plugin_downloadfile@_@/Library/Application Support/Medulla/var/log/xmpp-agent-machine.log' WHERE `namecmd`='Download agent log to file-transfer folder' AND `os`='macos';
UPDATE `qa_custom_command` SET `customcmd`='plugin_downloadfile@_@C:\\Program Files\\Medulla\\var\\log\\xmpp-agent-machine.log' WHERE `namecmd`='Download agent log to file-transfer folder' AND `os`='windows';

UPDATE `qa_custom_command` SET `customcmd`='tail -n100 /var/log/medulla/xmpp-agent-machine.log' WHERE `namecmd`='Show last 100 lines of agent logs' AND `os`='linux';
UPDATE `qa_custom_command` SET `customcmd`='tail -n100 \'/Library/Application Support/Medulla/var/log/xmpp-agent-machine.log\'' WHERE `namecmd`='Show last 100 lines of agent logs' AND `os`='macos';
UPDATE `qa_custom_command` SET `customcmd`='powershell.exe Get-Content  \'C:\\Program Files\\Medulla\\var\\log\\xmpp-agent-machine.log\' -Tail 100' WHERE `namecmd`='Show last 100 lines of agent logs' AND `os`='windows';

ALTER TABLE `xmppmaster`.`has_relayserverrules`
ADD INDEX `idx_uniq_rules` (`rules_id`,`order`,`subject`,`relayserver_id`) ;

UPDATE version SET Number = 52;

COMMIT;
