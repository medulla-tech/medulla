-- SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-119.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Alignement des actions rapides de l'agent entre Windows, Linux et macOS.

USE `xmppmaster`;

START TRANSACTION;

UPDATE `qa_custom_command`
   SET `description` = 'Restart Medulla Agent windows service'
 WHERE `os` = 'windows'
   AND `namecmd` = 'Restart Medulla Agent service';

UPDATE `qa_custom_command`
   SET `customcmd` = 'plugin_downloadfile@_@C:\\Program Files\\Medulla\\var\\log\\xmpp-agent-machine.log'
 WHERE `os` = 'windows'
   AND `namecmd` = 'Download agent log to file-transfer folder'
   AND `customcmd` = 'plugin_downloadfile@_@C:\\Program Files\\Pulse\\var\\log\\xmpp-agent-machine.log';

UPDATE `qa_custom_command`
   SET `namecmd` = 'Restart Medulla Agent service',
       `description` = 'Restart Medulla Agent linux service'
 WHERE `os` = 'linux'
   AND `namecmd` = 'Restart Pulse Agent service';

UPDATE `qa_custom_command`
   SET `customcmd` = REPLACE(`customcmd`,
                             '/var/log/medulla/medulla-agent.log',
                             '/var/log/medulla/xmpp-agent-machine.log')
 WHERE `os` = 'macos'
   AND `customcmd` LIKE '%/var/log/medulla/medulla-agent.log%';

UPDATE version SET Number = 119;

COMMIT;
