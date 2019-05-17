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

CREATE OR REPLACE INDEX ind_jid_machine on machines (jid(12) ASC);

ALTER TABLE `xmppmaster`.`machines` 
ADD INDEX `ind_uuid_machine` (`uuid_inventorymachine` ASC);

--
-- Table deploy creation index
--

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_deploy_uuid` (`inventoryuuid` ASC);

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_deploy_jidM` (`jidmachine` ASC);

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_deploy_start` (`startcmd` ASC);

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_deploy_end` (`endcmd` ASC);

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_deploy_cmd` (`command` ASC);

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_deploy_grp` (`group_uuid` ASC);

--
-- Table log creation index
--

ALTER TABLE `xmppmaster`.`logs` 
ADD INDEX `ind_log_sessionid` (`sessionname` ASC);

ALTER TABLE `xmppmaster`.`logs` 
ADD INDEX `ind_log_type` (`type` ASC);

--
-- Table relayserver creation index
--

ALTER TABLE `xmppmaster`.`relayserver` 
ADD INDEX `ind_relay_jid` (`jid` ASC);


ALTER TABLE `xmppmaster`.`relayserver` 
ADD INDEX `ind_relay_grpdeploy` (`groupdeploy` ASC);

-- base kiosk

ALTER TABLE `kiosk`.`profile_has_ous` 
ADD INDEX `ind_pr_ous_ou` (`ou` ASC);

ALTER TABLE `kiosk`.`profile_has_ous` 
ADD INDEX `ind_profile` (`profile_id` ASC);


ALTER TABLE `kiosk`.`package_has_profil` 
ADD INDEX `ind_packid` (`package_id` ASC);

ALTER TABLE `kiosk`.`package_has_profil` 
ADD INDEX `ind_profil` (`profil_id` ASC);

ALTER TABLE `xmppmaster`.`deploy` 
ADD INDEX `ind_start_cmd` (`startcmd` ASC),
ADD INDEX `ind_end_cmd` (`endcmd` ASC);


UPDATE version SET Number = 26;

COMMIT;
