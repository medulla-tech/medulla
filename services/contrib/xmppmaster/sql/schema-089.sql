-- -*- coding: utf-8; -*-
-- SPDX-FileCopyrightText: 2022-2023 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

START TRANSACTION;

USE `xmppmaster`;

UPDATE `qa_custom_command` SET `customcmd`='\"c:\\Progra~1\\TightVNC\\tvnserver.exe\" -controlservice -shareprimary' WHERE `namecmd`='VNC view primary screen';
UPDATE `qa_custom_command` SET `customcmd`='\"c:\\Progra~1\\TightVNC\\tvnserver.exe\" -controlservice -sharedisplay 1' WHERE `namecmd`='VNC view secondary screen';
UPDATE `qa_custom_command` SET `customcmd`='\"c:\\Progra~1\\TightVNC\\tvnserver.exe\" -controlservice -sharefull' WHERE `namecmd`='VNC view all screen';
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','VNC view third screen','\"c:\\Progra~1\\TightVNC\\tvnserver.exe\" -controlservice -sharedisplay 2','Display third screen');

UPDATE version SET Number = 89;

COMMIT;
