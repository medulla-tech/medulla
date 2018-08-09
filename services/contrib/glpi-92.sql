--
-- (c) 2018 Siveo, http://www.siveo.net/
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
-- along with MMC.  If not, see <http://www.gnu.org/licenses/>.

START TRANSACTION;

use glpi;

Create or replace view glpi_computers_pulse as select computers.id, computers.entities_id, computers.name, computers.serial, computers.otherserial, computers.contact, computers.contact_num, computers.users_id_tech, computers.groups_id_tech, computers.comment, computers.date_mod, os.operatingsystems_id, os.operatingsystemversions_id, os.operatingsystemservicepacks_id, os.operatingsystemarchitectures_id, os.license_number, os.license_id, os.operatingsystemkernelversions_id, computers.autoupdatesystems_id, computers.locations_id, computers.domains_id, computers.networks_id, computers.computermodels_id, computers.computertypes_id, computers.is_template, computers.template_name, computers.manufacturers_id, computers.is_deleted, computers.is_dynamic, computers.users_id, computers.groups_id, computers.states_id, computers.ticket_tco, computers.uuid, computers.date_creation, computers.is_recursive from glpi_computers computers inner join glpi_items_operatingsystems os on computers.id = os.items_id;


COMMIT;
