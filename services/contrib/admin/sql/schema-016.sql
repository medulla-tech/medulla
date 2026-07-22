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

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

-- Authentication provider management feature
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#authConfig', 'rw', 'onpremise,saas');

-- Missing on-premise only ACLs
UPDATE acl_feature_definitions set install_types = 'onpremise' WHERE feature_key = 'package_deployment_ro' and acl_entry IN ('xmppmaster#xmppmaster#auditmypastdeploysteam', 'xmppmaster#xmppmaster#auditteam', 'xmppmaster#xmppmaster#auditteamconvergence');
UPDATE acl_feature_definitions set install_types = 'onpremise' WHERE feature_key = 'acl_management';

-- Move remote desktop acl to a separate section
UPDATE acl_feature_definitions set label = 'Postes - gestion (suppression, scans...)', description = 'Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité' WHERE feature_key = 'computer_management_rw';
DELETE from acl_feature_definitions where feature_key = 'computer_management_rw' and acl_entry = 'base#computers#vnc_client';
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
  ('remote_desktop_rw', 'Postes - PMAD', 'VNC|RDP|SSH', 'security', 0, 'base#computers#vnc_client', 'rw', 'onpremise,saas');
INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level) VALUES
  ('Super-Admin', 'remote_desktop_rw', 'rw'),
  ('Admin', 'remote_desktop_rw', 'rw'),
  ('Technician', 'remote_desktop_rw', 'rw');

-- Missing ACL for package deployment audit details
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'xmppmaster#xmppmaster#viewlogs', 'ro', 'onpremise,saas');

UPDATE version SET Number = 16;

COMMIT;
