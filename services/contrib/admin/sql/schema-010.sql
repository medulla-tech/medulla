--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- any later version.
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

-- Feature definitions: maps feature keys to their ACL entries
-- Each row in the Excel = one feature_key + access_type combination
CREATE TABLE IF NOT EXISTS acl_feature_definitions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    feature_key VARCHAR(100) NOT NULL COMMENT 'Unique feature identifier',
    label VARCHAR(200) NOT NULL COMMENT 'Short display label',
    description VARCHAR(500) NULL COMMENT 'Tooltip description',
    category VARCHAR(50) NOT NULL COMMENT 'Category for grouping in UI',
    superadmin_only TINYINT(1) NOT NULL DEFAULT 0,
    acl_entry VARCHAR(200) NOT NULL COMMENT 'Single ACL entry (module#submod#action)',
    access_type ENUM('ro', 'rw') NOT NULL COMMENT 'Whether this entry is for read or write access',
    KEY idx_feature_key (feature_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Available profiles
CREATE TABLE IF NOT EXISTS acl_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profile_name VARCHAR(64) NOT NULL UNIQUE COMMENT 'Profile name (must match GLPI profile)',
    display_order INT NOT NULL DEFAULT 0 COMMENT 'Display order in UI'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO acl_profiles (profile_name, display_order) VALUES
('Super-Admin', 1),
('Admin', 2),
('Technician', 3);

-- Categories with display order
CREATE TABLE IF NOT EXISTS acl_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_key VARCHAR(50) NOT NULL UNIQUE COMMENT 'Category identifier used in acl_feature_definitions',
    label VARCHAR(100) NOT NULL COMMENT 'Display label',
    display_order INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO acl_categories (category_key, label, display_order) VALUES
('dashboard', 'Dashboard', 1),
('inventory', 'Inventaire', 2),
('imaging', 'Imaging', 3),
('deployment', 'Déploiement', 4),
('security', 'Sécurité', 5),
('updates', 'Mises à jour', 6),
('history', 'Historique', 7),
('admin', 'Administration', 8);

-- Profile selections: which features are enabled per profile
CREATE TABLE IF NOT EXISTS acl_profile_features (
    id INT AUTO_INCREMENT PRIMARY KEY,
    profile_name VARCHAR(64) NOT NULL COMMENT 'GLPI profile name',
    feature_key VARCHAR(100) NOT NULL COMMENT 'Feature identifier',
    access_level ENUM('ro', 'rw') NOT NULL DEFAULT 'ro',
    UNIQUE KEY uk_profile_feature (profile_name, feature_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- =============================================
-- Feature definitions data (from Excel)
-- =============================================

-- 1. Dashboard - User widgets | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'dashboard#main#default', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'dashboard#main#computersOnline_dashboard', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'dashboard#main#successRate_dashboard', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'dashboard#main#agents_dashboard', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'dashboard#main#deploymentsLaunched_dashboard', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'glpi#glpi#glpi_dashboard', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'glpi#glpi#antivirus_dashboard', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'glpi#glpi#inventory_dashboard', 'ro'),
('dashboard_user_widgets', 'Widgets utilisateur (agents, déploiements, inventaire...)', 'Ordinateurs en ligne|Taux de succès|Agents|Déploiements lancés|Inventaire GLPI|Antivirus|Répartition OS', 'dashboard', 0, 'glpi#glpi#os_repartition_dashboard', 'ro');

-- 2. Dashboard - Super-Admin widgets | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('dashboard_superadmin_widgets', 'Widgets Super-Admin (espace disque, backup...)', 'Espace disque|Informations générales|Sauvegardes|Mises à jour produit', 'dashboard', 1, 'dashboard#main#default', 'ro'),
('dashboard_superadmin_widgets', 'Widgets Super-Admin (espace disque, backup...)', 'Espace disque|Informations générales|Sauvegardes|Mises à jour produit', 'dashboard', 1, 'dashboard#main#space_dashboard', 'ro'),
('dashboard_superadmin_widgets', 'Widgets Super-Admin (espace disque, backup...)', 'Espace disque|Informations générales|Sauvegardes|Mises à jour produit', 'dashboard', 1, 'dashboard#main#general_dashboard', 'ro'),
('dashboard_superadmin_widgets', 'Widgets Super-Admin (espace disque, backup...)', 'Espace disque|Informations générales|Sauvegardes|Mises à jour produit', 'dashboard', 1, 'dashboard#main#backup_dashboard', 'ro'),
('dashboard_superadmin_widgets', 'Widgets Super-Admin (espace disque, backup...)', 'Espace disque|Informations générales|Sauvegardes|Mises à jour produit', 'dashboard', 1, 'dashboard#main#product_updates_dashboard', 'ro');

-- 3. Creation of static groups from dashboard widgets | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('dashboard_create_groups', 'Groupes statiques depuis widgets', 'Création de groupes statiques depuis les widgets du tableau de bord (antivirus, OS, machines)', 'dashboard', 0, 'base#computers#createStaticGroup', 'rw'),
('dashboard_create_groups', 'Groupes statiques depuis widgets', 'Création de groupes statiques depuis les widgets du tableau de bord (antivirus, OS, machines)', 'dashboard', 0, 'base#computers#createAntivirusStaticGroup', 'rw'),
('dashboard_create_groups', 'Groupes statiques depuis widgets', 'Création de groupes statiques depuis les widgets du tableau de bord (antivirus, OS, machines)', 'dashboard', 0, 'base#computers#createOSStaticGroup', 'rw'),
('dashboard_create_groups', 'Groupes statiques depuis widgets', 'Création de groupes statiques depuis les widgets du tableau de bord (antivirus, OS, machines)', 'dashboard', 0, 'base#computers#createMachinesStaticGroup', 'rw');

-- 4. Inventory of machines | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#index', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#machinesList', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#ajaxMachinesList', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#machinesListglpi', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#ajaxMachinesListglpi', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#xmppMachinesList', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#ajaxXmppMachinesList', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab0', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab1', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab2', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab3', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab4', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab5', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab6', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab7', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab8', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'base#computers#glpitabs#tab9', 'ro'),
('inventory_machines', 'Inventaire des machines (liste, détails, onglets...)', 'Liste des machines|Détails GLPI|Onglets inventaire|Détail XMPP', 'inventory', 0, 'xmppmaster#xmppmaster#machine_xmpp_detail', 'ro');

-- 5. Groups management | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('groups_management_ro', 'Groupes - consultation (liste, favoris...)', 'Affichage des groupes|Liste des favoris|Export CSV', 'inventory', 0, 'base#computers#display', 'ro'),
('groups_management_ro', 'Groupes - consultation (liste, favoris...)', 'Affichage des groupes|Liste des favoris|Export CSV', 'inventory', 0, 'base#computers#list', 'ro'),
('groups_management_ro', 'Groupes - consultation (liste, favoris...)', 'Affichage des groupes|Liste des favoris|Export CSV', 'inventory', 0, 'base#computers#listFavourite', 'ro'),
('groups_management_ro', 'Groupes - consultation (liste, favoris...)', 'Affichage des groupes|Liste des favoris|Export CSV', 'inventory', 0, 'base#computers#csv', 'ro');

-- 6. Groups management | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreator', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubedit', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubdel', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupedit', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupsubedit', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupsubdel', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#tmpdisplay', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#edit_share', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#creator_step2', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#save', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#save_detail', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#delete_group', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#remove_machine', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreator#tabdyn', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreator#tabsta', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreator#tabfromfile', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubedit#tabdyn', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubedit#tabsta', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubedit#tabfromfile', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubdel#tabdyn', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubdel#tabsta', 'rw'),
('groups_management_rw', 'Groupes - gestion (créer, modifier, supprimer...)', 'Création de groupes dynamiques et statiques|Modification|Suppression|Import depuis fichier', 'inventory', 0, 'base#computers#computersgroupcreatesubdel#tabfromfile', 'rw');

-- 7. Packaging | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('packaging_ro', 'Paquets - consultation (liste, détails...)', 'Liste des paquets|Règles de déploiement|Paquets en attente|Désynchronisation', 'deployment', 0, 'pkgs#pkgs#rulesList', 'ro'),
('packaging_ro', 'Paquets - consultation (liste, détails...)', 'Liste des paquets|Règles de déploiement|Paquets en attente|Désynchronisation', 'deployment', 0, 'pkgs#pkgs#index', 'ro'),
('packaging_ro', 'Paquets - consultation (liste, détails...)', 'Liste des paquets|Règles de déploiement|Paquets en attente|Désynchronisation', 'deployment', 0, 'pkgs#pkgs#detail', 'ro'),
('packaging_ro', 'Paquets - consultation (liste, détails...)', 'Liste des paquets|Règles de déploiement|Paquets en attente|Désynchronisation', 'deployment', 0, 'pkgs#pkgs#pending', 'ro'),
('packaging_ro', 'Paquets - consultation (liste, détails...)', 'Liste des paquets|Règles de déploiement|Paquets en attente|Désynchronisation', 'deployment', 0, 'pkgs#pkgs#desynchronization', 'ro');

-- 8. Packaging | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('packaging_rw', 'Paquets - gestion (créer, modifier, supprimer...)', 'Création de paquets|Modification|Suppression|Règles de déploiement|Gestion des licences', 'deployment', 0, 'pkgs#pkgs#addRule', 'rw'),
('packaging_rw', 'Paquets - gestion (créer, modifier, supprimer...)', 'Création de paquets|Modification|Suppression|Règles de déploiement|Gestion des licences', 'deployment', 0, 'pkgs#pkgs#editRule', 'rw'),
('packaging_rw', 'Paquets - gestion (créer, modifier, supprimer...)', 'Création de paquets|Modification|Suppression|Règles de déploiement|Gestion des licences', 'deployment', 0, 'pkgs#pkgs#add', 'rw'),
('packaging_rw', 'Paquets - gestion (créer, modifier, supprimer...)', 'Création de paquets|Modification|Suppression|Règles de déploiement|Gestion des licences', 'deployment', 0, 'pkgs#pkgs#edit', 'rw'),
('packaging_rw', 'Paquets - gestion (créer, modifier, supprimer...)', 'Création de paquets|Modification|Suppression|Règles de déploiement|Gestion des licences', 'deployment', 0, 'pkgs#pkgs#createGroupLicence', 'rw'),
('packaging_rw', 'Paquets - gestion (créer, modifier, supprimer...)', 'Création de paquets|Modification|Suppression|Règles de déploiement|Gestion des licences', 'deployment', 0, 'pkgs#pkgs#delete', 'rw');

-- 9. Package deployment | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#groupmsctabs', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#msctabs', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#start_command', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#start_adv_command', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#convergence', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#convergenceuninstall', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#packages', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'kiosk#kiosk#add', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'kiosk#kiosk#edit', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'kiosk#kiosk#acknowledges', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#wakeonlan', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#packageslist', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#popupReloadDeploy', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#rescheduleconvergence', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#reloaddeploy', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#groupmsctabs#grouptablaunch', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'base#computers#msctabs#tablaunch', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#consolexmpp', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#customQA', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#editqa', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#deleteqa', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#consolecomputerxmpp', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#ActionQuickconsole', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#ActionQuickGroup', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#QAcustommachgrp', 'rw'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#deployquick', 'rw');

-- 10. Package deployment | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'base#computers#statuscsv', 'ro'),
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'kiosk#kiosk#index', 'ro'),
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'xmppmaster#xmppmaster#index', 'ro'),
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'xmppmaster#xmppmaster#auditmypastdeploys', 'ro'),
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'xmppmaster#xmppmaster#auditmypastdeploysteam', 'ro'),
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'xmppmaster#xmppmaster#auditteam', 'ro'),
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'xmppmaster#xmppmaster#convergence', 'ro'),
('package_deployment_ro', 'Déploiement - consultation (audits, historique...)', 'Audits personnels|Audits équipe|Convergences|Kiosque|Export CSV', 'deployment', 0, 'xmppmaster#xmppmaster#auditteamconvergence', 'ro');

-- 11. Package deployment - Admin | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('package_deployment_admin', 'Déploiement - audit admin (tous les déploiements)', 'Audit global des déploiements|Historique complet|Convergences globales', 'deployment', 0, 'xmppmaster#xmppmaster#auditdeploy', 'ro'),
('package_deployment_admin', 'Déploiement - audit admin (tous les déploiements)', 'Audit global des déploiements|Historique complet|Convergences globales', 'deployment', 0, 'xmppmaster#xmppmaster#auditpastdeploys', 'ro'),
('package_deployment_admin', 'Déploiement - audit admin (tous les déploiements)', 'Audit global des déploiements|Historique complet|Convergences globales', 'deployment', 0, 'xmppmaster#xmppmaster#auditconvergence', 'ro');

-- 12. Imaging | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#systemImageManager', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#sysprepView', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#profilescript', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#editProfilescript', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#addProfilescript', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#index', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#master', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#master_remove', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#master_delete', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#master_edit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#master_clone', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#synchromaster', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#master_add', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#service', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#service_edit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#service_del', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#service_add', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#service_remove', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#service_show_used', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#bootmenu', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#bootmenu_up', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#bootmenu_down', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#bootmenu_edit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#postinstall', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#postinstall_edit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#postinstall_duplicate', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#postinstall_create_boot_service', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#postinstall_redirect_to_boot_service', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#postinstall_delete', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#configuration', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#save_configuration', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreator', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubedit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubdel', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofileedit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilesubedit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilesubdel', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#list_profiles', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupregister_target', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupimgtabs', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupbootmenu_remove', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#display', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#delete_group', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersgroupedit', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#edit_share', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupmsctabs', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#systemImageManager#unattended', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#systemImageManager#sysprepList', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreator#tabdyn', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreator#tabsta', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreator#tabfromfile', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubedit#tabdyn', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubedit#tabsta', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubedit#tabfromfile', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubdel#tabdyn', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubdel#tabsta', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#computersprofilecreatesubdel#tabfromfile', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupimgtabs#grouptabbootmenu', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupimgtabs#grouptabimages', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupimgtabs#grouptabservices', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupimgtabs#grouptabimlogs', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupimgtabs#grouptabconfigure', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupmsctabs#grouptablaunch', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupmsctabs#grouptabbundle', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupmsctabs#grouptablogs', 'rw'),
('imaging_rw', 'Imaging complet (toutes les fonctions)', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Sysprep|Unattended', 'imaging', 0, 'imaging#manage#groupmsctabs#grouptabhistory', 'rw');

-- 13. Updates | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#deployAllUpdates', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#deploySpecificUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#detailsSpecificUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#enableUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#disableUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#whitelistUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#blacklistUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#greylistUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#deleteRule', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#grayEnable', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#grayDisable', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#grayApprove', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#banUpdate', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#whiteUnlist', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#blackUnban', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#pendingUpdateByMachine', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#auditUpdateByMachine', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#approve_rules', 'rw'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#approve_products', 'rw');

-- 14. Updates | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#index', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#detailsByMachines', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#detailsByUpdates', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#hardwareConstraintsForMajorUpdates', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#MajorEntitiesList', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#ajaxMajorEntitiesList', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#ajaxMajorEntitiesListServ', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#updatesListWin', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#updatesListMajorWin', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#majorDetailsByMachines', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#groupUpdateMajorEntity', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#auditByEntity', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#auditByUpdate', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#MajorEntitiesList#tabwin', 'ro'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#MajorEntitiesList#tabwinserv', 'ro');

-- 15. Admin - Super-Admin | RW (superadmin_only)
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#switchrelay', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#conffile', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'xmppmaster#xmppmaster#listconffile', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#detailactions', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#qalaunched', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#qaresult', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#rules_tabs', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#moveRule', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#editCluster', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#newCluster', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#deleteRelayRule', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#editRelayRule', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#moveRelayRule', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#ban', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#unban', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#editEntity', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#deleteEntity', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#manageproviders', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#editProvider', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#deleteProvider', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'medulla_server#update#viewProductUpdates', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'medulla_server#update#installProductUpdates', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'medulla_server#update#ajaxInstallProductUpdates', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'medulla_server#update#restartAllMedullaServices', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'medulla_server#update#regenerateAgent', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#rules_tabs#relayRules', 'rw'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'admin#admin#rules_tabs#newRelayRule', 'rw');

-- 16. Admin - Admin | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('admin_admin', 'Gestion des utilisateurs (créer, modifier, supprimer...)', 'Création de comptes|Modification|Suppression|Désactivation|Reconfiguration machines', 'admin', 0, 'admin#admin#reconfiguremachines', 'rw'),
('admin_admin', 'Gestion des utilisateurs (créer, modifier, supprimer...)', 'Création de comptes|Modification|Suppression|Désactivation|Reconfiguration machines', 'admin', 0, 'admin#admin#listUsersofEntity', 'rw'),
('admin_admin', 'Gestion des utilisateurs (créer, modifier, supprimer...)', 'Création de comptes|Modification|Suppression|Désactivation|Reconfiguration machines', 'admin', 0, 'admin#admin#editUser', 'rw'),
('admin_admin', 'Gestion des utilisateurs (créer, modifier, supprimer...)', 'Création de comptes|Modification|Suppression|Désactivation|Reconfiguration machines', 'admin', 0, 'admin#admin#deleteUser', 'rw'),
('admin_admin', 'Gestion des utilisateurs (créer, modifier, supprimer...)', 'Création de comptes|Modification|Suppression|Désactivation|Reconfiguration machines', 'admin', 0, 'admin#admin#desactivateUser', 'rw');

-- 17. Admin - Technician | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#relaysList', 'ro'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#packageslist', 'ro'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#rules', 'ro'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#rulesDetail', 'ro'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#clustersList', 'ro'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#entitiesManagement', 'ro'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#downloadAgent', 'ro'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#downloadAgentFile', 'ro');

-- 18. History | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#index', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logsinventory', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logsbackup', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logsdeployment', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logsquickaction', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logsdownload', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logskiosk', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logspackaging', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logsremotedesktop', 'ro'),
('history', 'Historique (inventaire, déploiement, imaging...)', 'Inventaire|Sauvegardes|Déploiements|Quick Actions|Téléchargements|Kiosque|Paquets|Bureau à distance|Imaging', 'history', 0, 'base#logview#logsimaging', 'ro');

-- 19. Imaging - On premise | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#index', 'ro'),
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#master', 'ro'),
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#service', 'ro'),
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#bootmenu', 'ro'),
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#postinstall', 'ro'),
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#profilescript', 'ro'),
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#list_profiles', 'ro'),
('imaging_onpremise_ro', 'Imaging On-premise - consultation', 'Masters|Services|Bootmenu|Post-install|Profils de scripts', 'imaging', 0, 'imaging#manage#display', 'ro');

-- 20. Imaging - On premise | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#groupimgtabs', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#configuration', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#master_add', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#master_edit', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#master_clone', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#master_delete', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#service_del', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#service_add', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#bootmenu_up', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#bootmenu_down', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#bootmenu_edit', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#postinstall_create_boot_service', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#postinstall_duplicate', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#addProfilescript', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#systemImageManager', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#computersprofilecreator', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#groupregister_target', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#computersgroupedit', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#edit_share', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#groupmsctabs', 'rw'),
('imaging_onpremise_rw', 'Imaging On-premise - gestion', 'Masters|Services|Bootmenu|Post-install|Profils|Groupes imaging|Déploiement', 'imaging', 0, 'imaging#manage#delete_group', 'rw');

-- 21. Computer management | RO
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'xmppmaster#xmppmaster#monitoringview', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#index', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#softwareDetail', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#machines', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#machineDetail', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#entities', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#groups', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#groupDetail', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#allcves', 'ro'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'security#security#cveDetail', 'ro');

-- 22. Computer management | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'base#computers#vnc_client', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'base#computers#delete', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'xmppmaster#xmppmaster#listfichierconf', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#ajaxAddExclusion', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#ajaxScanMachine', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#ajaxStartScanEntity', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#ajaxStartScanGroup', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#settings', 'rw'),
('computer_management_rw', 'Postes - gestion (VNC, suppression, scans...)', 'VNC|Suppression de machines|Configuration|Scans de sécurité|Exclusions CVE|Paramètres sécurité', 'security', 0, 'security#security#ajaxResetDisplayFilters', 'rw');

-- 23. Creation of static groups from deployment results | RW
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('deploy_groups_from_results', 'Groupes statiques depuis résultats de déploiement', 'Création de groupes depuis les résultats graphiques de déploiement', 'deployment', 0, 'base#computers#createMachinesStaticGroupdeploy', 'rw');

-- 24. ACL Management | RW (superadmin_only)
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type) VALUES
('acl_management', 'Gestion des ACL', 'Gestion des droits par fonctionnalité et par profil', 'admin', 1, 'admin#admin#aclFeatures', 'rw');

UPDATE version SET Number = 10;

COMMIT;
