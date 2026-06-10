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

-- Imaging | RW > Missing ACLs for imaging action in computers list
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#imgtabs', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#imgtabs#tabbootmenu', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#imgtabs#tabimages', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#imgtabs#tabservices', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#imgtabs#tabimlogs', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#imgtabs#tabconfigure', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#bootmenu_remove', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#addimage', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#addservice', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'base#computers#showtarget', 'rw');

-- Imaging - On premise | RW > Missing ACLs for imaging action in computers list
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#imgtabs', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#imgtabs#tabbootmenu', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#imgtabs#tabimages', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#imgtabs#tabservices', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#imgtabs#tabimlogs', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#imgtabs#tabconfigure', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#bootmenu_remove', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#addimage', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#addservice', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'base#computers#showtarget', 'rw');

UPDATE version SET Number = 14;

COMMIT;
