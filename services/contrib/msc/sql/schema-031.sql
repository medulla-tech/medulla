--
-- (c) 2013 Mandriva, http://www.mandriva.com/
--
-- This file is part of Pulse 2, http://pulse2.mandriva.org
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

-- ----------------------------------------------------------------------
-- Database converti to Innodb Myisam table
-- ----------------------------------------------------------------------
ALTER TABLE commands_history ENGINE=InnoDB;
ALTER TABLE  bundle  ENGINE=InnoDB;
ALTER TABLE  commands  ENGINE=InnoDB;
ALTER TABLE  commands_history ENGINE=InnoDB;
ALTER TABLE  commands_on_host ENGINE=InnoDB;
ALTER TABLE  phase            ENGINE=InnoDB;
ALTER TABLE  pull_targets     ENGINE=InnoDB;
ALTER TABLE  target          ENGINE=InnoDB;


ALTER TABLE `msc`.`phase`
DROP FOREIGN KEY `fk_phase_1`;
ALTER TABLE `msc`.`phase`
ADD CONSTRAINT `fk_phase_1`
  FOREIGN KEY (`fk_commands_on_host`)
  REFERENCES `msc`.`commands_on_host` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

ALTER TABLE `msc`.`commands_on_host`
ADD CONSTRAINT `fkcommand`
  FOREIGN KEY (`id`)
  REFERENCES `msc`.`commands` (`id`)
  ON DELETE CASCADE
  ON UPDATE NO ACTION;

SET FOREIGN_KEY_CHECKS=1;



-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 31;

COMMIT;

