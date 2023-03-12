--
-- (c) 2022 Siveo, http://www.siveo.net/
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

USE glpi;

CREATE OR REPLACE VIEW glpi_computers_pulse AS
    SELECT 
        computers.id,
        computers.entities_id,
        computers.name,
        computers.serial,
        computers.otherserial,
        computers.contact,
        computers.contact_num,
        computers.users_id_tech,
        computers.groups_id_tech,
        computers.comment,
        computers.date_mod,
        os.operatingsystems_id,
        os.operatingsystemversions_id,
        os.operatingsystemservicepacks_id,
        os.operatingsystemarchitectures_id,
        os.license_number,
        os.licenseid,
        os.operatingsystemkernelversions_id,
        computers.autoupdatesystems_id,
        computers.locations_id,
        glpi_domains_items.domains_id,
        computers.networks_id,
        computers.computermodels_id,
        computers.computertypes_id,
        computers.is_template,
        computers.template_name,
        computers.manufacturers_id,
        computers.is_deleted,
        computers.is_dynamic,
        computers.users_id,
        computers.groups_id,
        computers.states_id,
        computers.ticket_tco,
        computers.uuid,
        computers.date_creation,
        computers.is_recursive 
    FROM
        glpi_computers computers 
    INNER JOIN
        glpi_items_operatingsystems os ON computers.id = os.items_id
    LEFT JOIN
        glpi_domains_items ON glpi_domains_items.items_id = computers.id;

CREATE OR REPLACE VIEW glpi_view_computers_items_printer AS
    SELECT
        id,
        items_id,
        computers_id,
        is_deleted,
        is_dynamic
    FROM
        glpi.glpi_computers_items
    WHERE
        itemtype = 'Printer';

CREATE OR REPLACE VIEW glpi_view_computers_items_peripheral AS
    SELECT
        id,
        items_id,
        computers_id,
        is_deleted,
        is_dynamic
    FROM
        glpi.glpi_computers_items
    WHERE
        itemtype = 'Peripheral';

CREATE OR REPLACE VIEW glpi_view_peripherals_manufacturers AS
    SELECT
       *
    FROM
        glpi.glpi_manufacturers;

COMMIT;
