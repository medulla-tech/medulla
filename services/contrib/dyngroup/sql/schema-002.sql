--
-- (c) 2008 Mandriva, http://www.mandriva.com/
--
-- $Id$
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

CREATE TABLE ShareGroupType (
    id INT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB;
CREATE INDEX dyngroup_sharegrouptype_value_idx ON ShareGroupType (value(10));

ALTER TABLE ShareGroup ADD COLUMN FK_type INT default 0;

INSERT INTO ShareGroupType values (0, 'View');
INSERT INTO ShareGroupType values (1, 'Edit');

CREATE TABLE UsersType (
    id INT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB;
CREATE INDEX dyngroup_userstype_value_idx ON UsersType (value(10));

ALTER TABLE Users ADD COLUMN type INT default 0;
INSERT INTO UsersType values (0, 'user');
INSERT INTO UsersType values (1, 'group');

UPDATE version set Number = 2;

