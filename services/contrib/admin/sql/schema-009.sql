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

-- Table to track Medulla update availability (populated by nightly cron)

START TRANSACTION;
USE admin;

CREATE TABLE IF NOT EXISTS medulla_update_availability (
    id INT PRIMARY KEY DEFAULT 1,
    update_available TINYINT(1) DEFAULT 0,
    current_version VARCHAR(20),
    available_version VARCHAR(20),
    last_check DATETIME,
    last_check_status VARCHAR(20) DEFAULT 'pending'
);

UPDATE version SET Number = 9;

COMMIT;
