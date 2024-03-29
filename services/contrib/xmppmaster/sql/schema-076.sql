--
-- (c) 2021 Siveo, http://www.siveo.net/
--
--
-- This file is part of Pulse 2, http://www.siveo.net/
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
START TRANSACTION;


USE `xmppmaster`;
DROP procedure IF EXISTS `afterinsertmachine`;


INSERT IGNORE INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*ABORT DEPLOYMENT SHUTDOWN.*', 'ABORT RESUMPTION ERROR', 'abortontimeout');
INSERT IGNORE INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Resumption deploy session.*', 'DEPLOYMENT START', 'restartdeploy');

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 76;

COMMIT;
