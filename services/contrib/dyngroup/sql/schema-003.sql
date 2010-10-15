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

CREATE TABLE ProfilesResults (
    FK_groups INT NOT NULL,
    FK_machines INT NOT NULL,
    PRIMARY KEY(FK_machines),
    INDEX profiles_result_ind_g (FK_groups),
    FOREIGN KEY (FK_groups) REFERENCES Groups(id),
    INDEX profiles_result_ind_m (FK_machines),
    FOREIGN KEY (FK_machines) REFERENCES Machines(id)
);

CREATE TABLE ProfilesPackages (
    FK_groups INT NOT NULL,
    package_id INT NOT NULL,
    PRIMARY KEY(FK_groups, package_id),
    INDEX profiles_packages_ind (FK_groups),
    FOREIGN KEY (FK_groups) REFERENCES Groups(id)
);

CREATE TABLE ProfilesData (
    FK_groups INT NOT NULL,
    entity_uuid TEXT default NULL,
    imaging_uuid TEXT default NULL,
    PRIMARY KEY(FK_groups),
    INDEX profiles_data_ind (FK_groups),
    FOREIGN KEY (FK_groups) REFERENCES Groups(id)
);

-- Groups.type
CREATE TABLE GroupType (
    id INT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY(id)
);
CREATE INDEX dyngroup_grouptype_value_idx ON GroupType (value(10));

INSERT INTO GroupType values (0, 'Group');
INSERT INTO GroupType values (1, 'Profile');

ALTER TABLE Groups ADD COLUMN type INT default 0;
ALTER TABLE Groups ADD FOREIGN KEY (type) REFERENCES GroupType(id);

-- modify fields name to be coherant
ALTER TABLE Groups CHANGE COLUMN FK_user FK_users INT NOT NULL;
ALTER TABLE Results CHANGE COLUMN FK_group FK_groups INT NOT NULL;
ALTER TABLE Results CHANGE COLUMN FK_machine FK_machines INT NOT NULL;
ALTER TABLE ShareGroup CHANGE COLUMN FK_user FK_users INT NOT NULL;
ALTER TABLE ShareGroup CHANGE COLUMN FK_group FK_groups INT NOT NULL;
ALTER TABLE ShareGroup CHANGE COLUMN FK_type type INT NOT NULL;

-- add missing FK
ALTER TABLE Groups ADD FOREIGN KEY (FK_users) REFERENCES Users(id);
ALTER TABLE Results ADD FOREIGN KEY (FK_groups) REFERENCES Groups(id);
ALTER TABLE Results ADD FOREIGN KEY (FK_machines) REFERENCES Machines(id);
ALTER TABLE ShareGroup ADD FOREIGN KEY (FK_users) REFERENCES Users(id);
ALTER TABLE ShareGroup ADD FOREIGN KEY (FK_groups) REFERENCES Groups(id);
ALTER TABLE ShareGroup ADD FOREIGN KEY (type) REFERENCES ShareGroupType(id);
ALTER TABLE Users ADD FOREIGN KEY (type) REFERENCES UsersTypes(id);

-- display_in_menu
ALTER TABLE ShareGroup ADD COLUMN display_in_menu INT NOT NULL Default 0;
UPDATE ShareGroup, Groups SET ShareGroup.display_in_menu = Groups.display_in_menu WHERE ShareGroup.FK_groups = Groups.id;
INSERT INTO ShareGroup (FK_groups, FK_users, display_in_menu, type) SELECT id, FK_users, display_in_menu, 1 FROM Groups;
ALTER TABLE Groups DROP COLUMN display_in_menu;

-- Some new indexes to speedup dyngroup queries
CREATE INDEX dyngroup_results_fk_machine_idx on Results (FK_machine);
CREATE INDEX dyngroup_groups_fk_user_idx on Groups (FK_user);
CREATE INDEX dyngroup_sharegroup_fk_group_idx on ShareGroup (FK_group);
CREATE INDEX dyngroup_sharegroup_fk_user_idx on ShareGroup (FK_user);

UPDATE version set Number = 3;

