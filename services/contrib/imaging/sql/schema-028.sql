--
-- (c) 2025 Siveo, http://siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://siveo.net
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

start transaction;

CREATE TABLE if not exists `Profile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fk_imagingserver` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE if not exists  `ProfileInMenu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fk_menuitem` int(11) NOT NULL,
  `fk_profile` int(11) NOT NULL,
  PRIMARY KEY (`id`)
);
CREATE TABLE if not exists  `PostInstallInProfile` (
  `fk_profile` int(11) NOT NULL,
  `fk_post_install_script` int(11) NOT NULL,
  `order` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`fk_profile`,`fk_post_install_script`)
);

CREATE TABLE if not exists  `PostInstallInMenu` (
  `fk_menuitem` int(11) NOT NULL,
  `fk_post_install_script` int(11) NOT NULL,
  PRIMARY KEY (`fk_menuitem`,`fk_post_install_script`)
);

-- these foreign keys delete PostInstallInProfile.* ProfileInMenu.* associated to the Profile <p> when the profile <p> is deleted
-- no need to handle the deletion in these tables.
ALTER TABLE ProfileInMenu
ADD FOREIGN KEY (fk_profile) REFERENCES Profile(id) on delete cascade ;

ALTER TABLE PostInstallInProfile
ADD FOREIGN KEY (fk_profile) REFERENCES Profile(id) on delete cascade ;

update version set Number=28 where Number=27;
commit;
