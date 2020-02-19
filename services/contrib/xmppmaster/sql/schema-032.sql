--
-- (c) 2019 Siveo, http://www.siveo.net/
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

--
-- Table substituteconf
--

CREATE TABLE IF NOT EXISTS `xmppmaster`.`substituteconf` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `type` VARCHAR(45) NOT NULL DEFAULT 'master',
  `jidsubtitute` VARCHAR(255) NOT NULL,
  `countsub` INT(11) NOT NULL DEFAULT '0',
  `relayserver_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_substituteconf_relayserver_idx` (`relayserver_id` ASC),
  CONSTRAINT `fk_substituteconf_relayserver_idx`
    FOREIGN KEY (`relayserver_id`)
    REFERENCES `xmppmaster`.`relayserver` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

CREATE TABLE IF NOT EXISTS `xmppmaster`.`agent_subscription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`))
ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT 'Lists subscription agents';

CREATE TABLE IF NOT EXISTS `xmppmaster`.`subscription` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `macadress` varchar(15) NOT NULL,
  `idagentsubscription` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `macadress_UNIQUE` (`macadress`),
  KEY `fk_subscription_agent_subscription_idx` (`idagentsubscription`),
  CONSTRAINT `fk_subscription_agent_subscription_idx`
    FOREIGN KEY (`idagentsubscription`)
    REFERENCES `xmppmaster`.`agent_subscription` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE=InnoDB
DEFAULT CHARACTER SET = utf8
COMMENT='This table defines which subscription agent is used';

LOCK TABLES `substituteconf` WRITE;
INSERT INTO `xmppmaster`.`substituteconf` (`type`, `jidsubtitute`, `relayserver_id`) VALUES ('registration', 'master@pulse', 1);
INSERT INTO `xmppmaster`.`substituteconf` (`type`, `jidsubtitute`, `relayserver_id`) VALUES ('subscription', 'master@pulse', 1);
INSERT INTO `xmppmaster`.`substituteconf` (`type`, `jidsubtitute`, `relayserver_id`) VALUES ('inventory', 'master@pulse', 1);
INSERT INTO `xmppmaster`.`substituteconf` (`type`, `jidsubtitute`, `relayserver_id`) VALUES ('assessor', 'master@pulse', 1);
UNLOCK TABLES;

LOCK TABLES `agent_subscription` WRITE;
INSERT INTO `xmppmaster`.`agent_subscription` (`name`) VALUES ('master@pulse');
UNLOCK TABLES;

UPDATE version SET Number = 32;

COMMIT;
