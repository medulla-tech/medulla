-- -*- coding: utf-8; -*-
-- SPDX-FileCopyrightText: 2022-2023 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

START TRANSACTION;

USE `xmppmaster`;

UPDATE `qa_custom_command` SET `customcmd`='start cmd /c "sc stop medullaagent && timeout /t 5 && sc start medullaagent"', `namecmd`='Restart Medulla Agent service' WHERE `namecmd`='Restart Pulse Agent service' AND `os`='windows';

UPDATE `qa_custom_command` SET `customcmd`="powershell.exe Get-Content  'C:\Program Files\Medulla\var\log\xmpp-agent-machine.log' -Tail 100" WHERE `namecmd`="Show last 100 lines of agent logs" AND `os`="windows";

UPDATE version SET Number = 87;

COMMIT;
