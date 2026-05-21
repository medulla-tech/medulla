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

-- Fix: the Security > Settings page uses TabbedPageGenerator tabs, each guarded
-- by hasCorrectTabAcl() which requires a 4-segment ACL (module#submod#action#tab).
-- Only the 3-segment page ACL 'security#security#settings' existed, so non-root
-- profiles saw the Settings page with no visible tabs. Add the 6 tab ACLs to the
-- existing 'computer_management_rw' feature (parent page ACL already present there).

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#settings#tabfilters', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#settings#tabcves', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#settings#tabsoftware', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#settings#tabvendors', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#settings#tabmachines', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#settings#tabgroups', 'rw');

UPDATE version SET Number = 14;

COMMIT;
