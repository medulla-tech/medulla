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

-- =============================================
-- Medulla Store Module - Schema local minimal
--
-- Note: Ce module se connecte à une base store DISTANTE (centralisee).
-- Les tables software, subscriptions, etc. sont sur le serveur Store.
-- Ce schema sert uniquement à la verification de version locale.
-- =============================================
START TRANSACTION;

USE store;

-- Table de versioning (requise par le module pour le check de version)
CREATE TABLE IF NOT EXISTS version (
    Number TINYINT UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO version (Number)
SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM version);

COMMIT;
