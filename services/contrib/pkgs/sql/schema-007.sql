--
-- (c) 2021 Siveo, http://siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://siveo.net
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------


START TRANSACTION;

INSERT INTO extensions VALUES(NULL, 20, "Unknown exe Rule", "", "exe", "", "", "", "", '"%s"', "Rule for unknown exes");
INSERT INTO extensions VALUES(NULL, 21, "Python Rule", "", "py", "", "python", "", "", '@@@PYTHON_PATH@@@ "%s"', "Rule for python scripts");
INSERT INTO extensions VALUES(NULL, 22, "Korn Shell Rule", "", "ksh", "", "ksh", "", "", '/bin/ksh "%s"', "Rule for ksh scripts");
INSERT INTO extensions VALUES(NULL, 23, "C Shell Rule", "", "csh", "", "csh", "", "", '/bin/csh "%s"', "Rule for csh scripts");
INSERT INTO extensions VALUES(NULL, 24, "Powershell Rule", "", "ps1", "", "", "", "", 'powershell.exe -ExecutionPolicy Bypass -File "%s"', "Rule for powershell scripts");
INSERT INTO extensions VALUES(NULL, 25, "VBS Rule", "", "vbs", "", "", "", "", 'cscript "%s"', "Rule for VB scripts");
INSERT INTO extensions VALUES(NULL, 26, "Batch Rule", "", "bat", "", "", "", "", '"%s"', "Rule for batch scripts");
UPDATE extensions SET rule_order = 100 WHERE rule_order = 3;

UPDATE version SET Number = 7;

COMMIT;

