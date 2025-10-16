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

CREATE TABLE IF NOT EXISTS magic_link (
  token       CHAR(36)      NOT NULL,                               -- UUID v4
  login       VARCHAR(191)  NOT NULL,                               -- uid/email
  created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at  DATETIME      NOT NULL,                               -- NOW() + INTERVAL 5 MINUTE
  used_at     DATETIME      DEFAULT NULL,                           -- single-use (NULL = not used)
  PRIMARY KEY (token),
  KEY idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Automatic cleaning every 10 min
-- Check SET GLOBAL event_scheduler=ON;
CREATE EVENT IF NOT EXISTS ev_magic_link_gc
  ON SCHEDULE EVERY 10 MINUTE
  DO
    DELETE FROM magic_link
    WHERE used_at IS NOT NULL OR expires_at < NOW();

ALTER TABLE admin.saas_organisations
  ADD COLUMN IF NOT EXISTS stripe_tag VARCHAR(255) NULL DEFAULT NULL;

UPDATE version SET Number = 5;