--
--  (c) 2024-2026 Medulla, http://www.medulla-tech.io
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

-- Add version-specific disclaimer columns to medulla_update_availability.
-- Populated by check_medulla_updates.sh from the remote JSON manifest
-- published at https://dl.medulla-tech.io/up/versions_disclaimer.json

START TRANSACTION;
USE admin;

ALTER TABLE medulla_update_availability
    ADD COLUMN IF NOT EXISTS disclaimer_level VARCHAR(20) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS disclaimer_json TEXT DEFAULT NULL;

UPDATE version SET Number = 12;

COMMIT;
