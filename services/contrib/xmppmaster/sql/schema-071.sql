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

ALTER TABLE `xmppmaster`.`mon_rules`
    ADD COLUMN `enable` INT NOT NULL DEFAULT 1 AFTER `id` ,
    ADD COLUMN `os` VARCHAR(45) NULL  DEFAULT NULL AFTER `comment` ,
    ADD COLUMN `type_machine` VARCHAR(45) NULL DEFAULT NULL AFTER `os` ;

ALTER TABLE `xmppmaster`.`mon_devices`
    CHANGE COLUMN `device_type` `device_type` VARCHAR(255) NOT NULL ;

ALTER TABLE `xmppmaster`.`mon_rules`
    CHANGE COLUMN `os` `os` VARCHAR(45) NULL DEFAULT NULL COMMENT 'Allow to tell on which OS the rule will be aplied. This is a regexp.' ,
    CHANGE COLUMN `type_machine` `type_machine` VARCHAR(45) NULL DEFAULT NULL COMMENT 'Allow to know if the rule is applied on a machine or a relay' ,
    CHANGE COLUMN `user` `user` VARCHAR(2048) NULL DEFAULT NULL COMMENT 'the user who defined this rule' ,
    CHANGE COLUMN `comment` `comment` VARCHAR(2048) NULL DEFAULT NULL COMMENT 'explains the contents of this rule' ,
    CHANGE COLUMN `binding` `binding` VARCHAR(2048) NOT NULL COMMENT 'code that will be executed on the information sent from the device or service for defining the actions that will be carried out' ,
    CHANGE COLUMN `succes_binding_cmd` `succes_binding_cmd` VARCHAR(225) NULL DEFAULT NULL COMMENT 'command to run if binding test result is True' ,
    CHANGE COLUMN `no_success_binding_cmd` `no_success_binding_cmd` VARCHAR(225) NULL DEFAULT NULL COMMENT 'command to run if binding test result is False' ;

ALTER TABLE `xmppmaster`.`mon_event`
    CHANGE COLUMN `parameter_other` `parameter_other` VARCHAR(2048) NULL DEFAULT NULL ;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 71;

COMMIT;
