--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/.>

START TRANSACTION;

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
        items_id_peripheral,
        items_id_asset,
        is_deleted,
        is_dynamic
    FROM
        glpi_assets_assets_peripheralassets
    WHERE
        itemtype_asset = 'Printer';

CREATE OR REPLACE VIEW glpi_view_computers_items_peripheral AS
    SELECT
        id,
        items_id_peripheral,
        items_id_asset,
        is_deleted,
        is_dynamic
    FROM
        glpi_assets_assets_peripheralassets
    WHERE
        itemtype_asset = 'Peripheral';

CREATE OR REPLACE VIEW glpi_view_peripherals_manufacturers AS
    SELECT
       *
    FROM
        glpi_manufacturers;

COMMIT;
