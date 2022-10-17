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

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------

START TRANSACTION;

-- optimisation  search admin cluster ars
ALTER TABLE `xmppmaster`.`machines`
ADD INDEX  IF NOT EXISTS `index_group_deploy` (`groupdeploy` ASC) ;

DROP INDEX if exists ind_relay_jid on `xmppmaster`.`relayserver` ;

ALTER TABLE `xmppmaster`.`relayserver`
ADD INDEX IF NOT EXISTS `ind_mode` (`moderelayserver` ASC) ;

ALTER TABLE `xmppmaster`.`relayserver`
ADD INDEX IF NOT EXISTS `ind_presence` (`enabled` ASC) ;

ALTER TABLE `xmppmaster`.`relayserver`
ADD FULLTEXT INDEX  IF NOT EXISTS `ind_nameserver` (`nameserver`) ;

ALTER TABLE `xmppmaster`.`relayserver`
ADD FULLTEXT INDEX  IF NOT EXISTS `ind_ipserver` (`ipserver`) ;
;

ALTER TABLE `xmppmaster`.`relayserver`
ADD FULLTEXT INDEX  IF NOT EXISTS `ind_jid` (`jid`) ;

ALTER TABLE `xmppmaster`.`relayserver`
ADD FULLTEXT INDEX  IF NOT EXISTS `ind_classutil` (`classutil`) ;


ALTER TABLE `xmppmaster`.`has_cluster_ars`
ADD INDEX IF NOT EXISTS `ind_ars` (`id_ars` ASC) ,
ADD INDEX IF NOT EXISTS `ind_cluster` (`id_cluster` ASC) ;


ALTER TABLE `xmppmaster`.`cluster_ars`
ADD FULLTEXT INDEX IF NOT EXISTS `ind_name` (`name`) ,
ADD FULLTEXT INDEX IF NOT EXISTS `ind_description` (`description`) ;

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 73;

COMMIT;
