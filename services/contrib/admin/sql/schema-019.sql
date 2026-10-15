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

-- Add ACL features for the Medulla Store module (catalog, subscriptions, deployment).
-- Pre-assigns store features to existing profiles:
--   Super-Admin: RO + RW
--   Admin:       RO + RW
--   Technician:  RO only (consultation)

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

-- gives access to the multicast init configuration popup
INSERT INTO acl_feature_definitions(`feature_key`, `label`, `description`,`category`, `superadmin_only`,`acl_entry`, `access_type`, `install_types`) VALUES ("imaging_rw", "Imaging complet (toutes les fonctions)", "Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended", "imaging", 0, "base#computers#multicast", "rw", "onpremise,saas");

UPDATE version SET Number = 19;

COMMIT;
