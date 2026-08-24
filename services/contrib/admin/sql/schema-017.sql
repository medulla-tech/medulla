--
-- (c) 2022 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://www.siveo.net/
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

--
-- Schema v017 : Support du moteur de synchronisation ITSM → GLPI Medulla
-- Ajoute 3 nouvelles tables pour la synchronisation des entités ITSM
--
-- Historique :
--  - v004 : saas_application, saas_organisations
--  - v017 : itsm_entity_mapping, sync_logs, sync_metrics
--

-- =====================================================================
-- Table 1 : saas_itsm_entity_mapping
-- =====================================================================
-- Rôle : Réconciliation / Mapping source (ITSM) → cible (Medulla/GLPI)
-- Objectif : Enregistrer la correspondance entre les entités source et cibles,
--            garantir la stabilité des IDs Medulla, tracer l'historique
-- Rejouabilité : CREATE TABLE IF NOT EXISTS (safe)
--
CREATE TABLE IF NOT EXISTS `admin`.`saas_itsm_entity_mapping` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL COMMENT 'Identifiant client ITSM (ex: c001)',
  `source_path` VARCHAR(500) NOT NULL COMMENT 'Chemin complet source ITSM (ex: Organisation/Finance/Comptabilité)',
  `source_id` VARCHAR(100) NOT NULL COMMENT 'ID unique source ITSM (ex: glpi_entity_1)',
  `target_path` VARCHAR(500) COMMENT 'Chemin Medulla après normalisation (ex: c001/Finance/Comptabilité)',
  `target_glpi_id` INT COMMENT 'ID entité Medulla/GLPI créée/modifiée',
  `config_version` VARCHAR(50) COMMENT 'Version config utilisée pour ce mapping',
  `last_modifier` VARCHAR(100) COMMENT 'Qui a modifié (user ou system_sync)',
  `modification_origin` VARCHAR(20) COMMENT 'Origine: sync (auto), mmc (manuel), bootstrap (initial)',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Création du mapping',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Dernière modification',
  
  -- Constraints et indexes
  UNIQUE KEY `uk_client_source_id` (`client_id`, `source_id`),
  INDEX `idx_client_target_glpi_id` (`client_id`, `target_glpi_id`),
  INDEX `idx_updated_at` (`updated_at`),
  INDEX `idx_modification_origin` (`modification_origin`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci 
COMMENT='[SaaS] Mapping source → cible pour synchronisation ITSM';

-- =====================================================================
-- Table 2 : saas_itsm_sync_logs
-- =====================================================================
-- Rôle : Historique et audit des exécutions de synchronisation
-- Objectif : Tracer chaque sync (résultats, erreurs, stats),
--            permettre diagnostique et audit complet
-- Rejouabilité : CREATE TABLE IF NOT EXISTS (safe)
--
CREATE TABLE IF NOT EXISTS `admin`.`saas_itsm_sync_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL COMMENT 'Identifiant client synchro',
  `sync_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Quand la sync a exécuté',
  `config_version` VARCHAR(50) COMMENT 'Version config utilisée pour cette sync',
  `status` VARCHAR(20) COMMENT 'Résultat: success, partial, failed',
  `objects_created` INT DEFAULT 0 COMMENT 'Nombre entités créées en Medulla',
  `objects_updated` INT DEFAULT 0 COMMENT 'Nombre entités modifiées en Medulla',
  `objects_ignored` INT DEFAULT 0 COMMENT 'Nombre entités skippées (erreur, mapping absent)',
  `errors` LONGTEXT COMMENT 'Messages erreurs détaillés si status != success',
  `debug_mode` BOOLEAN DEFAULT FALSE COMMENT 'Mode debug activé lors de la sync',
  
  -- Indexes pour requêtes courantes
  INDEX `idx_client_sync_timestamp` (`client_id`, `sync_timestamp`),
  INDEX `idx_status` (`status`),
  INDEX `idx_sync_timestamp` (`sync_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci 
COMMENT='[SaaS] Historique et audit des synchronisations ITSM';

-- =====================================================================
-- Table 3 : saas_itsm_sync_metrics
-- =====================================================================
-- Rôle : Métriques de performance de chaque synchronisation
-- Objectif : Monitoring perf, tendances, alertes, dimensionnement ressources
-- Rejouabilité : CREATE TABLE IF NOT EXISTS (safe)
--
CREATE TABLE IF NOT EXISTS `admin`.`saas_itsm_sync_metrics` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `client_id` VARCHAR(50) NOT NULL COMMENT 'Identifiant client synchro',
  `sync_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Quand exécuté',
  `duration_seconds` INT COMMENT 'Durée totale de la sync (secondes)',
  `objects_count` INT COMMENT 'Nombre total entités traitées',
  `errors_count` INT COMMENT 'Nombre entités en erreur',
  `performance_notes` TEXT COMMENT 'Notes optionnelles (ex: Slow DB query)',
  
  -- Indexes pour requêtes courantes
  INDEX `idx_client_sync_timestamp` (`client_id`, `sync_timestamp`),
  INDEX `idx_duration_seconds` (`duration_seconds`),
  INDEX `idx_sync_timestamp` (`sync_timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci 
COMMENT='[SaaS] Métriques de performance des synchronisations ITSM';

-- =====================================================================
-- Vérification : tables créées
-- =====================================================================
-- Requêtes de vérification (à exécuter manuellement si nécessaire) :
--
-- SELECT TABLE_NAME FROM information_schema.TABLES 
-- WHERE TABLE_SCHEMA='admin' 
-- AND TABLE_NAME IN ('saas_itsm_entity_mapping', 'saas_itsm_sync_logs', 'saas_itsm_sync_metrics');
--
-- SELECT * FROM admin.saas_application;
-- SELECT * FROM admin.saas_organisations;
-- SELECT COUNT(*) FROM admin.saas_itsm_entity_mapping;
-- SELECT COUNT(*) FROM admin.saas_itsm_sync_logs;
-- SELECT COUNT(*) FROM admin.saas_itsm_sync_metrics;
--

--
-- Update version du schema
--
UPDATE version SET Number = 17;

COMMIT;
