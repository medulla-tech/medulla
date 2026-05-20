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

  -- 1. Store | RO (consultation catalogue + liste abonnements)
  INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
  ('store_ro', 'Store - consultation (catalogue, abonnements)', 'Catalogue Medulla Store|Liste des abonnements', 'deployment', 0,
  'store#store#index', 'ro'),
  ('store_ro', 'Store - consultation (catalogue, abonnements)', 'Catalogue Medulla Store|Liste des abonnements', 'deployment', 0,
  'store#store#ajaxCatalogList', 'ro'),
  ('store_ro', 'Store - consultation (catalogue, abonnements)', 'Catalogue Medulla Store|Liste des abonnements', 'deployment', 0,
  'store#store#ajaxSubscribeList', 'ro');

  -- 2. Store | RW (abonnement + déploiement depuis le Store)
  INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#subscribe', 'rw'),
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#deploy', 'rw'),
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#tabmachines', 'rw'),
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#tabgroups', 'rw'),
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#ajaxMachinesListForDeploy', 'rw'),
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#ajaxGroupsListForDeploy', 'rw'),
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#ajaxSearchMachines', 'rw'),
  ('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'store#store#startDeploy', 'rw');

  -- Pre-assign Store features to existing profiles
  INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level) VALUES
  ('Super-Admin', 'dashboard_user_widgets', 'ro'),
  ('Super-Admin', 'dashboard_superadmin_widgets', 'ro'),
  ('Super-Admin', 'dashboard_create_groups', 'rw'),
  ('Admin',       'dashboard_user_widgets', 'ro'),
  ('Admin',       'dashboard_create_groups', 'rw'),
  ('Technician',  'dashboard_user_widgets', 'ro'),
  ('Technician',  'dashboard_create_groups', 'rw'),
  ('Super-Admin', 'inventory_machines', 'ro'),
  ('Super-Admin', 'groups_management_ro', 'ro'),
  ('Super-Admin', 'groups_management_rw', 'rw'),
  ('Admin',       'inventory_machines', 'ro'),
  ('Admin',       'groups_management_ro', 'ro'),
  ('Admin',       'groups_management_rw', 'rw'),
  ('Technician',  'inventory_machines', 'ro'),
  ('Technician',  'groups_management_ro', 'ro'),
  ('Technician',  'groups_management_rw', 'rw'),
  ('Super-Admin', 'packaging_ro', 'ro'),
  ('Super-Admin', 'packaging_rw', 'rw'),
  ('Super-Admin', 'package_deployment_ro', 'ro'),
  ('Super-Admin', 'package_deployment_rw', 'rw'),
  ('Super-Admin', 'package_deployment_admin', 'ro'),
  ('Super-Admin', 'deploy_groups_from_results', 'rw'),
  ('Super-Admin', 'store_ro', 'ro'),
  ('Super-Admin', 'store_rw', 'rw'),
  ('Admin',       'packaging_ro', 'ro'),
  ('Admin',       'packaging_rw', 'rw'),
  ('Admin',       'package_deployment_ro', 'ro'),
  ('Admin',       'package_deployment_rw', 'rw'),
  ('Admin',       'package_deployment_admin', 'ro'),
  ('Admin',       'deploy_groups_from_results', 'rw'),
  ('Admin',       'store_ro', 'ro'),
  ('Admin',       'store_rw', 'rw'),
  ('Technician',  'packaging_ro', 'ro'),
  ('Technician',  'packaging_rw', 'rw'),
  ('Technician',  'package_deployment_ro', 'ro'),
  ('Technician',  'package_deployment_rw', 'rw'),
  ('Technician',  'deploy_groups_from_results', 'rw'),
  ('Technician',  'store_ro', 'ro'),
  ('Super-Admin', 'imaging_rw', 'rw'),
  ('Super-Admin', 'imaging_onpremise_ro', 'ro'),
  ('Super-Admin', 'imaging_onpremise_rw', 'rw'),
  ('Admin',       'imaging_rw', 'rw'),
  ('Admin',       'imaging_onpremise_ro', 'ro'),
  ('Admin',       'imaging_onpremise_rw', 'rw'),
  ('Technician',  'imaging_rw', 'rw'),
  ('Technician',  'imaging_onpremise_ro', 'ro'),
  ('Technician',  'imaging_onpremise_rw', 'rw'),
  ('Super-Admin', 'updates_ro', 'ro'),
  ('Super-Admin', 'updates_rw', 'rw'),
  ('Admin',       'updates_ro', 'ro'),
  ('Admin',       'updates_rw', 'rw'),
  ('Technician',  'updates_ro', 'ro'),
  ('Technician',  'updates_rw', 'rw'),
  ('Super-Admin', 'admin_superadmin', 'rw'),
  ('Super-Admin', 'admin_admin', 'rw'),
  ('Super-Admin', 'admin_technician', 'ro'),
  ('Admin',       'admin_admin', 'rw'),
  ('Admin',       'admin_technician', 'ro'),
  ('Technician',  'admin_technician', 'ro'),
  ('Super-Admin', 'history', 'ro'),
  ('Admin',       'history', 'ro'),
  ('Technician',  'history', 'ro'),
  ('Super-Admin', 'computer_management_ro', 'ro'),
  ('Super-Admin', 'computer_management_rw', 'rw'),
  ('Admin',       'computer_management_ro', 'ro'),
  ('Admin',       'computer_management_rw', 'rw'),
  ('Technician',  'computer_management_ro', 'ro'),
  ('Technician',  'computer_management_rw', 'rw'),
  ('Super-Admin', 'acl_management', 'rw');

  UPDATE version SET Number = 13;

  COMMIT;
