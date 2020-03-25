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

LOCK TABLES `def_remote_deploy_status` WRITE;
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Transfer error : curl download.*$', 'ABORT TRANSFER FAILED', 'errortransferfailed');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Package delayed execution error.*$', 'ABORT PACKAGE EXECUTION ERROR', 'abortpackageexecutionerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Package delayed execution cancelled.*$', 'ABORT PACKAGE EXECUTION CANCELLED', 'abortpackageexecutioncancelled');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Deployment error : missing dependency.*$', 'ABORT MISSING DEPENDENCY', 'abortmissingdependency');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Package execution error.*$', 'ABORT PACKAGE EXECUTION ERROR', 'abortpackageexecutionerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Package error: descriptor for OS .* missing.*$', 'ABORT PACKAGE WORKFLOW ERROR', 'abortpackageworkflowerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Transfer error: Package Server does not have this package.*$', 'ABORT TRANSFER FAILED', 'errortransferfailed');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Deployment error in fifo : timed out.*$', 'ABORT ON TIMEOUT', 'abortontimeout');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Spooling the deployment in queue.*$', 'DEPLOYMENT SPOOLED', 'deploymentspooled');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Descriptor inconsistency error.*$', 'ABORT PACKAGE WORKFLOW ERROR', 'abortpackageworkflowerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Error initializing grafcet.*$', 'ABORT PACKAGE WORKFLOW ERROR', 'abortpackageworkflowerror');
INSERT INTO `xmppmaster`.`def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES ('.*Deployment aborted: inventory error.*$', 'ABORT PACKAGE EXECUTION ERROR', 'abortpackageexecutionerror');
UNLOCK TABLES;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 37;

COMMIT;
