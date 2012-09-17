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

DROP TABLE IF EXISTS SqlDatumSave;

CREATE TABLE Groups (
    id INT NOT NULL AUTO_INCREMENT,
    name TEXT,
    query TEXT,
    bool TEXT,
    display_in_menu INT NOT NULL DEFAULT 0,
    FK_user INT NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB;
CREATE INDEX dyngroup_groups_name_idx ON Groups (name(10));

CREATE TABLE Users (
    id INT NOT NULL AUTO_INCREMENT,
    login TEXT NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB;
CREATE INDEX dyngroup_users_login_idx ON Users (login(10));

CREATE TABLE ShareGroup (
    id INT NOT NULL AUTO_INCREMENT,
    FK_group INT NOT NULL,
    FK_user INT NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB;

CREATE TABLE Machines (
    id INT NOT NULL AUTO_INCREMENT,
    uuid TEXT NOT NULL,
    name TEXT,
    PRIMARY KEY(id)
) ENGINE=InnoDB;
CREATE INDEX dyngroup_machines_name_idx ON Machines (name(10));
/* ?? CREATE INDEX dyngroup_machines_uuid_idx ON Machines (uuid(10)); */

CREATE TABLE Results (
    id INT NOT NULL AUTO_INCREMENT,
    FK_group INT NOT NULL,
    FK_machine INT NOT NULL,
    PRIMARY KEY(id)
) ENGINE=InnoDB;

CREATE TABLE version (Number INT NOT NULL);
INSERT INTO version values (1);


