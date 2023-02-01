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
-- insert item params_json  parameters deployement general

START TRANSACTION;
--
-- Table machines creation index
--

ALTER TABLE `xmppmaster`.`machines` 
ADD INDEX IF NOT EXISTS `ind_jid_machine` (jid(12) ASC),
ADD INDEX IF NOT EXISTS `ind_uuid_machine` (`uuid_inventorymachine` ASC);

--
-- Table deploy creation index
--

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX IF NOT EXISTS `ind_deploy_uuid` (`inventoryuuid` ASC),
ADD INDEX IF NOT EXISTS `ind_deploy_jidM` (`jidmachine` ASC),
ADD INDEX IF NOT EXISTS `ind_deploy_start` (`startcmd` ASC),
ADD INDEX IF NOT EXISTS `ind_deploy_end` (`endcmd` ASC),
ADD INDEX IF NOT EXISTS `ind_deploy_cmd` (`command` ASC),
ADD INDEX IF NOT EXISTS `ind_deploy_grp` (`group_uuid` ASC);

--
-- Table log creation index
--

ALTER TABLE `xmppmaster`.`logs` 
ADD INDEX IF NOT EXISTS `ind_log_sessionid` (`sessionname` ASC),
ADD INDEX IF NOT EXISTS `ind_log_type` (`type` ASC);

--
-- Table relayserver creation index
--

ALTER TABLE `xmppmaster`.`relayserver` 
ADD INDEX IF NOT EXISTS `ind_relay_jid` (`jid` ASC),
ADD INDEX IF NOT EXISTS `ind_relay_grpdeploy` (`groupdeploy` ASC);

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX IF NOT EXISTS `ind_start_cmd` (`startcmd` ASC),
ADD INDEX IF NOT EXISTS `ind_end_cmd` (`endcmd` ASC);


UPDATE version SET Number = 26;

COMMIT;
