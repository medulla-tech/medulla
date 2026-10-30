-- SPDX-FileCopyrightText: 2026 Medulla
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-116.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================

USE `xmppmaster`;

START TRANSACTION;

UPDATE qa_custom_command
SET customcmd = 'powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Select-Object HandleCount,Name,Priority,ProcessId,ThreadCount,WorkingSetSize | Format-Table -AutoSize"',
    description = 'Get list of processes with PowerShell CIM'
WHERE `user` = 'allusers'
  AND os = 'windows'
  AND namecmd = 'Show process List'
  AND customcmd = 'wmic process list brief';

UPDATE version SET Number = 116;

COMMIT;
