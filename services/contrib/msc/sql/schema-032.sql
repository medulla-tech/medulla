--
-- (c) 2023 Siveo, http://www.siveo.net/
--
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


-- check exist index before creation




START TRANSACTION;

SET FOREIGN_KEY_CHECKS=0;

-------------------------------------------
-- Save msc tables
-------------------------------------------

CREATE TABLE IF NOT EXISTS save_phase SELECT * FROM phase;
CREATE TABLE IF NOT EXISTS save_commands_on_host SELECT * FROM commands_on_host;
CREATE TABLE IF NOT EXISTS save_commands SELECT * FROM commands;
CREATE TABLE IF NOT EXISTS save_target SELECT * FROM target;

-------------------------------------------
-- Clean msc tables
-------------------------------------------

delete FROM phase;
delete FROM commands_on_host;
delete FROM commands;
delete FROM target;

-- ----------------------------------------------------------------------
-- Add foreign key on tables
-- ----------------------------------------------------------------------
ALTER TABLE `msc`.`commands_on_host` 
  DROP FOREIGN KEY IF EXISTS `fk_commands_on_host_commands`;
ALTER TABLE `msc`.`commands_on_host` 
ADD CONSTRAINT `fk_commands_on_host_commands`
  FOREIGN KEY IF NOT EXISTS (`fk_commands`)
  REFERENCES `msc`.`commands` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

ALTER TABLE `msc`.`phase` 
  DROP FOREIGN KEY IF EXISTS `fk_phase_command_on_host`;
ALTER TABLE `msc`.`phase` 
ADD CONSTRAINT `fk_phase_command_on_host`
  FOREIGN KEY IF NOT EXISTS (`fk_commands_on_host`)
  REFERENCES `msc`.`commands_on_host` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

ALTER TABLE `msc`.`commands_on_host` 
  DROP FOREIGN KEY IF EXISTS `fk_commands_on_host_target`;
ALTER TABLE `msc`.`commands_on_host`
ADD CONSTRAINT `fk_commands_on_host_target` 
  FOREIGN KEY IF NOT EXISTS (`fk_target`) 
  REFERENCES `target` (`id`) 
  ON DELETE NO ACTION 
  ON UPDATE NO ACTION;


-------------------------------------------
-- Copy data back
-------------------------------------------
INSERT IGNORE INTO commands (SELECT * FROM save_commands);
INSERT IGNORE INTO target (SELECT * FROM save_target);
INSERT IGNORE INTO commands_on_host (SELECT * FROM save_commands_on_host);
INSERT IGNORE INTO phase (SELECT * FROM save_phase);

-------------------------------------------
-- Clean msc tables
-------------------------------------------

DROP TABLE IF EXISTS save_commands;
DROP TABLE IF EXISTS save_target;
DROP TABLE IF EXISTS save_commands_on_host;
DROP TABLE IF EXISTS save_phase;

SET FOREIGN_KEY_CHECKS=1;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 32;

COMMIT;

