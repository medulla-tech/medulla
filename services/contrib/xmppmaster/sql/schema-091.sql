-- -*- coding: utf-8; -*-
-- SPDX-FileCopyrightText: 2022-2024 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

START TRANSACTION;

USE `xmppmaster`;

UPDATE `qa_custom_command` SET `customcmd`='\"c:\\Progra~1\\TightVNC\\tvnserver.exe\" -controlservice -sharedisplay 2' WHERE `namecmd`='VNC view secondary screen';

UPDATE `qa_custom_command` SET `customcmd`='\"c:\\Progra~1\\TightVNC\\tvnserver.exe\" -controlservice -sharedisplay 3' WHERE `namecmd`='VNC view third screen';

UPDATE version SET Number = 91;

COMMIT;