--
-- (c) 2023 Siveo, http://www.siveo.net/
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

START TRANSACTION;
USE `xmppmaster`;
-- ----------------------------------------------------------------------
-- Crée la table `up_history` s'il n'existe pas déjà.
-- Cette table permet de garder une trace des updates effectuées sur les machines
-- ----------------------------------------------------------------------

create table if not exists up_history(
    id int not null auto_increment, primary key(id),
    update_id varchar(255) not null,
    id_machine int not null,
    jid varchar(255),
    update_list enum("white", "gray"),
    required_date datetime,
    curent_date datetime,
    deploy_date datetime,
    delete_date datetime,
    command int null,
    id_deploy int,
    deploy_title varchar(255)
);
-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 84;

COMMIT;
