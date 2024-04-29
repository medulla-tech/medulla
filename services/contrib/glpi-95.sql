--
-- (c) 2022 Siveo, http://www.siveo.net/
--
-- This file is part of Medulla 2, http://medulla.mandriva.org
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC.  If not, see <http://www.gnu.org/licenses/>.

START TRANSACTION;

USE glpi;

CREATE OR REPLACE VIEW glpi_computers_medulla AS
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
        computers.autoupdatesystems_id,
        computers.locations_id,
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
        computers.is_recursive,
        ti.domains_id,
        os.operatingsystems_id,
        os.operatingsystemversions_id,
        os.operatingsystemservicepacks_id,
        os.operatingsystemarchitectures_id,
        os.license_number,
        os.licenseid,
        os.operatingsystemkernelversions_id
    FROM
        glpi_computers computers
            LEFT JOIN
        (SELECT DISTINCT
            id, items_id, domains_id
        FROM
            glpi_domains_items
        GROUP BY items_id) AS ti ON ti.items_id = computers.id
            LEFT JOIN
        (SELECT DISTINCT
            items_id,
                id,
                operatingsystems_id,
                licenseid,
                operatingsystemkernelversions_id,
                operatingsystemservicepacks_id,
                operatingsystemarchitectures_id,
                license_number,
                operatingsystemversions_id
        FROM
            glpi_items_operatingsystems
        GROUP BY (items_id)) AS os ON computers.id = os.items_id;

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
