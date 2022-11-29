--
-- (c) 2022 Siveo, http://www.siveo.net/
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
-- Database version
-- ----------------------------------------------------------------------

START TRANSACTION;

CREATE TABLE IF NOT EXISTS acknowledgements(
    id INT NOT NULL AUTO_INCREMENT, PRIMARY KEY(id),
    id_package_has_profil INT NOT NULL,
    askuser VARCHAR(255) NOT NULL, -- user asking grants on specific package
    askdate datetime NOT NULL DEFAULT NOW(), -- when this user asked the right
    acknowledgedbyuser VARCHAR(255) NULL, -- the admin who change the rights
    startdate datetime NOT NULL DEFAULT NOW(),
    enddate datetime NULL, -- if null this acknowledge has no expiration date
    status enum("waiting", "allowed", "rejected") not null default "waiting"
);


UPDATE version SET Number = 7
COMMIT;
