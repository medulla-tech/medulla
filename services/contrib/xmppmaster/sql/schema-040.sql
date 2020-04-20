--
-- (c) 2018 Siveo, http://www.siveo.net/
--
-- $Id$
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

DELETE FROM `xmppmaster`.`def_remote_deploy_status`;

INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Transfer error: Package Server does not have this package.*', 'ERROR TRANSFER FAILED', 'errortransferfailed');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Transfer error.*', 'ABORT TRANSFER FAILED', 'aborttransferfailed');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*execution error.*', 'ABORT PACKAGE EXECUTION ERROR', 'abortpackageexecutionerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*execution cancelled.*', 'ABORT PACKAGE EXECUTION CANCELLED', 'abortpackageexecutioncancelled');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*missing dependency.*', 'ABORT MISSING DEPENDENCY', 'abortmissingdependency');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Descriptor error.*', 'ABORT PACKAGE WORKFLOW ERROR', 'abortpackageworkflowerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Error initializing grafcet.*', 'ABORT PACKAGE WORKFLOW ERROR', 'abortpackageworkflowerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Deployment error in fifo : timed out.*', 'ABORT ON TIMEOUT', 'abortontimeout');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Spooling the deployment in queue.*', 'DEPLOYMENT SPOOLED', 'deploymentspooled');

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 40;

COMMIT;
