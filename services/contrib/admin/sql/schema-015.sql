--
--  (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
-- along with MMC; If not, see <http://www.gnu.org/licenses/>.
--

-- Introduce the notion of "installation type" (onpremise vs saas) in the ACL
-- schema. Two distinct concerns are addressed:
--
--   1. Feature visibility per install type
--      (acl_feature_definitions.install_types): some features only exist on
--      one type (e.g. imaging is not available on multi-tenant SaaS).
--
--   2. Per-profile default assignments per install type
--      (acl_profile_features.install_type): the same feature can exist on
--      both install types but ship with different default rights (e.g. Admin
--      gets RW on onpremise but only RO on saas).
--
-- install_type values:
--   * 'onpremise' covers both on-premise infrastructure and dedicated
--     single-tenant SaaS installations.
--   * 'saas' covers mutualised multi-tenant SaaS only.
--
-- Existing rows are preserved with safe defaults so installations behave
-- exactly as before the upgrade. The migration also cleans up the imaging
-- feature_keys: imaging_rw was a superset of imaging_onpremise_*, so the
-- latter are merged into imaging_rw and dropped, and imaging_rw is tagged
-- 'onpremise' (imaging is not available on multi-tenant SaaS).
--
-- WARNING: any UI customisation pointing at imaging_onpremise_ro will be
-- silently dropped (no RO counterpart in imaging_rw). imaging_onpremise_rw
-- customisations are migrated to imaging_rw, but if a profile already had
-- imaging_rw with a different access_level for the same install_type, the
-- INSERT IGNORE keeps the existing row and the imaging_onpremise_rw level
-- is lost. Document this in the release notes.
--
-- Idempotency: this migration uses MariaDB's IF [NOT] EXISTS clauses on
-- ALTER TABLE so it can be re-run after a partial apply without erroring.
-- It is NOT compatible with stock MySQL (which does not support those
-- extensions on ADD COLUMN / DROP INDEX). Medulla ships against MariaDB.

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

-- 1. Reference table listing available installation types
CREATE TABLE IF NOT EXISTS acl_install_types (
    install_type VARCHAR(32) NOT NULL PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    display_order INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO acl_install_types (install_type, label, display_order) VALUES
    ('onpremise', 'On-premise', 1),
    ('saas',      'SaaS',       2)
ON DUPLICATE KEY UPDATE label = VALUES(label), display_order = VALUES(display_order);

-- 2. Tag each feature with the install types it is relevant for.
--    Default 'onpremise,saas' = visible everywhere (no behaviour change).
ALTER TABLE acl_feature_definitions
    ADD COLUMN IF NOT EXISTS install_types SET('onpremise','saas') NOT NULL DEFAULT 'onpremise,saas'
    AFTER access_type;

-- 3. Tag each profile pre-assignment with the install type it applies to.
--    'both' = applied on every install type (preserves current behaviour).
ALTER TABLE acl_profile_features
    ADD COLUMN IF NOT EXISTS install_type ENUM('onpremise','saas','both') NOT NULL DEFAULT 'both'
    AFTER access_level;

-- 4. Allow the same (profile, feature) pair to coexist with different
--    install_type values, so we can express "Admin: RW on onpremise, RO on saas".
ALTER TABLE acl_profile_features DROP INDEX IF EXISTS uk_profile_feature;
ALTER TABLE acl_profile_features
    ADD UNIQUE KEY IF NOT EXISTS uk_profile_feature (profile_name, feature_key, install_type);

-- 5. Imaging cleanup: restrict imaging_rw to onpremise (imaging is not
--    available on multi-tenant SaaS), merge imaging_onpremise_rw into
--    imaging_rw (schema-014 had already made it a subset by adding the
--    base#computers#imgtabs* entries to imaging_rw), and drop the now
--    redundant imaging_onpremise_* feature_keys.
--    See the WARNING block at the top of this file regarding lost
--    customisations on imaging_onpremise_ro and on conflicting
--    imaging_onpremise_rw rows.
UPDATE acl_feature_definitions
   SET install_types = 'onpremise'
 WHERE feature_key = 'imaging_rw';

INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level, install_type)
  SELECT profile_name, 'imaging_rw', 'rw', install_type
    FROM acl_profile_features
   WHERE feature_key = 'imaging_onpremise_rw';

DELETE FROM acl_profile_features WHERE feature_key LIKE 'imaging_onpremise_%';
DELETE FROM acl_feature_definitions WHERE feature_key LIKE 'imaging_onpremise_%';

UPDATE version SET Number = 15;

COMMIT;
