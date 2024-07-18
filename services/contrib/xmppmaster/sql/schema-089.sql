-- -*- coding: utf-8; -*-
-- SPDX-FileCopyrightText: 2022-2024 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

START TRANSACTION;

USE `xmppmaster`;

-- ----------------------------------------------------------------------
-- Quick actions to add or remove pulseuser to Administrators group
-- ----------------------------------------------------------------------
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Add SSH user to admins group','PowerShell Add-LocalGroupMember -SID S-1-5-32-544 -Member pulseuser -Verbose','Add pulseuser account to Administrators group');
INSERT INTO `qa_custom_command` VALUES ('allusers','windows','Remove SSH user from admins group','PowerShell Remove-LocalGroupMember -SID S-1-5-32-544 -Member pulseuser -Verbose','Remove pulseuser account from Administrators group');

UPDATE version SET Number = 89;

COMMIT;
