--
--  (c) 2026 Medulla, http://www.medulla-tech.io
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

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

-- ----------------------------------------------------------------------
-- Schema 023 : dedicated ACL features for the kiosk module
--
-- The kiosk pages leave package_deployment_ro / package_deployment_rw and
-- get their own features: kiosk_ro (profile list) and kiosk_rw (add, edit,
-- delete a profile).
-- ----------------------------------------------------------------------

-- Existing grants follow the pages. Runs only while the kiosk entries are
-- still held by the deployment features, so a replay grants nothing back.
INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level, install_type)
SELECT profile_name, 'kiosk_ro', 'ro', install_type
  FROM acl_profile_features
 WHERE feature_key = 'package_deployment_ro'
   AND EXISTS (SELECT 1
                 FROM acl_feature_definitions
                WHERE feature_key = 'package_deployment_ro'
                  AND acl_entry = 'kiosk#kiosk#index');

-- Technician keeps read access only
INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level, install_type)
SELECT profile_name, 'kiosk_rw', 'rw', install_type
  FROM acl_profile_features
 WHERE feature_key = 'package_deployment_rw'
   AND access_level = 'rw'
   AND profile_name <> 'Technician'
   AND EXISTS (SELECT 1
                 FROM acl_feature_definitions
                WHERE feature_key = 'package_deployment_rw'
                  AND acl_entry IN ('kiosk#kiosk#add', 'kiosk#kiosk#edit'));

-- kiosk#kiosk#acknowledges points to a page that no longer exists
DELETE FROM acl_feature_definitions
 WHERE feature_key = 'package_deployment_ro'
   AND acl_entry = 'kiosk#kiosk#index';

DELETE FROM acl_feature_definitions
 WHERE feature_key = 'package_deployment_rw'
   AND acl_entry IN ('kiosk#kiosk#add',
                     'kiosk#kiosk#edit',
                     'kiosk#kiosk#acknowledges');

UPDATE acl_feature_definitions
   SET description = REPLACE(description, '|Kiosque', '')
 WHERE feature_key = 'package_deployment_ro'
   AND description LIKE '%|Kiosque%';

-- acl_feature_definitions has no unique constraint: purge before insert
DELETE FROM acl_feature_definitions
 WHERE feature_key IN ('kiosk_ro', 'kiosk_rw');

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('kiosk_ro', 'Kiosque - consultation', 'Liste des profils', 'deployment', 0, 'kiosk#kiosk#index', 'ro', 'onpremise,saas'),
('kiosk_rw', 'Kiosque - gestion des profils', 'Création de profils|Modification|Suppression', 'deployment', 0, 'kiosk#kiosk#add', 'rw', 'onpremise,saas'),
('kiosk_rw', 'Kiosque - gestion des profils', 'Création de profils|Modification|Suppression', 'deployment', 0, 'kiosk#kiosk#edit', 'rw', 'onpremise,saas');

UPDATE version SET Number = 23;

COMMIT;
