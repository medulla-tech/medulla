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
-- Schema 020 : ACL du module updates
--
-- updates#updates#index redirige vers EntityComplianceos, qui n avait
-- aucune entree ACL.
--
-- Les entrees designant des pages ou des onglets retires du module sont
-- supprimees : ancien moteur Windows, ancien Linux. products, automation et
-- EntityComplianceos ont un onglet Windows et un onglet Linux. Les pages
-- products et automation sont reposees.
-- ----------------------------------------------------------------------

DELETE FROM acl_feature_definitions
 WHERE feature_key IN ('updates_ro', 'updates_rw')
   AND acl_entry IN ('updates#updates#deployAllUpdates',
                     'updates#updates#enableUpdate',
                     'updates#updates#disableUpdate',
                     'updates#updates#whitelistUpdate',
                     'updates#updates#blacklistUpdate',
                     'updates#updates#greylistUpdate',
                     'updates#updates#deleteRule',
                     'updates#updates#updatesListMajorWin',
                     'updates#updates#groupUpdateMajorEntity',
                     'updates#updates#ajaxMajorEntitiesList',
                     'updates#updates#ajaxMajorEntitiesListServ',
                     'updates#updates#hardwareConstraintsForMajorUpdates',
                     'updates#updates#majorDetailsByMachines',
                     'updates#updates#ajaxMajorDetailsByMachines',
                     'updates#updates#View_detail_machine_kernel_linux_entity',
                     'updates#updates#ajaxApproveProduct',
                     'updates#updates#ajaxApproveRules',
                     'updates#updates#ajaxAuditByEntity',
                     'updates#updates#ajaxAuditByUpdate',
                     'updates#updates#ajaxDeploySpecificUpdate',
                     'updates#updates#ajaxDetailsByMachines',
                     'updates#updates#ajaxDetailsByUpdates',
                     'updates#updates#ajaxDetailsSpecificUpdate',
                     'updates#updates#ajaxDetailsSpecificUpdateWithout',
                     'updates#updates#ajaxEntitiesList',
                     'updates#updates#ajaxEntitiesListlinux',
                     'updates#updates#ajaxEntitiesListlinuxfilter',
                     'updates#updates#ajaxEntitiesListwindows',
                     'updates#updates#ajaxEntitiesListwindowsfilter',
                     'updates#updates#ajaxLinuxApprovedReleases',
                     'updates#updates#ajaxLinuxAutoUpdatePolicy',
                     'updates#updates#ajaxMajorDeploymentHistoryLinux',
                     'updates#updates#ajaxPendingUpdateByMachine',
                     'updates#updates#ajaxUpdatesListWin',
                     'updates#updates#ajaxUpdatesListWinBlack',
                     'updates#updates#ajaxUpdatesListWinGray',
                     'updates#updates#ajaxUpdatesListWinWhite',
                     'updates#updates#ajaxView_compliance_distri_linux_entity',
                     'updates#updates#ajaxView_detail_machine_kernel_linux_entity',
                     'updates#updates#approve_products',
                     'updates#updates#approve_rules',
                     'updates#updates#auditByEntity',
                     'updates#updates#auditByUpdate',
                     'updates#updates#blackUnban',
                     'updates#updates#cancelUpdate',
                     'updates#updates#deploySpecificUpdate',
                     'updates#updates#deployUpdate',
                     'updates#updates#deployUpdateLinuxType',
                     'updates#updates#detailsByMachines',
                     'updates#updates#detailsByUpdates',
                     'updates#updates#detailsSpecificUpdate',
                     'updates#updates#grayDisable',
                     'updates#updates#grayEnable',
                     'updates#updates#grpDeployUpdateLinuxMajor',
                     'updates#updates#linuxApprovedReleases',
                     'updates#updates#linuxAutoUpdatePolicy',
                     'updates#updates#majorDeploymentHistoryLinux',
                     'updates#updates#majorDeploymentHistoryWin',
                     'updates#updates#auditUpdateByMachine',
                     'updates#updates#osLinux',
                     'updates#updates#pendingUpdateByMachine',
                     'updates#updates#View_compliance_distri_linux_entity',
                     'updates#updates#EntityComplianceos#tablinux',
                     'updates#updates#products#tabwin',
                     'updates#updates#products#tablinux',
                     'updates#updates#automation#tabwin',
                     'updates#updates#automation#tablinux',
                     'updates#updates#MajorEntitiesList#tabalma',
                     'updates#updates#MajorEntitiesList#tabcentosos',
                     'updates#updates#MajorEntitiesList#tabdebian',
                     'updates#updates#MajorEntitiesList#tabfedora',
                     'updates#updates#MajorEntitiesList#tabmint',
                     'updates#updates#MajorEntitiesList#tabrhel',
                     'updates#updates#MajorEntitiesList#tabsuse',
                     'updates#updates#MajorEntitiesList#tabubuntu',
                     'updates#updates#MajorEntitiesList#tabwinserv',
                     'updates#updates#MajorEntitiesList#tabzorin');

-- acl_feature_definitions n a pas de contrainte d unicite : on purge
-- avant d inserer pour que le script reste rejouable.
DELETE FROM acl_feature_definitions
 WHERE feature_key = 'updates_ro'
   AND acl_entry IN ('updates#updates#EntityComplianceos',
                     'updates#updates#EntityComplianceos#tabwin',
                     'updates#updates#EntityComplianceos#tablinux',
                     'updates#updates#MajorEntitiesList#tablinux',
                     'updates#updates#detailsMachineWin');

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#EntityComplianceos', 'ro', 'onpremise,saas'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#EntityComplianceos#tabwin', 'ro', 'onpremise,saas'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#EntityComplianceos#tablinux', 'ro', 'onpremise,saas'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#MajorEntitiesList#tablinux', 'ro', 'onpremise,saas'),
('updates_ro', 'Mises à jour - consultation (conformité, audit...)', 'Conformité par entité|Détails par machines|Mises à jour majeures OS', 'updates', 0, 'updates#updates#detailsMachineWin', 'ro', 'onpremise,saas');

DELETE FROM acl_feature_definitions
 WHERE feature_key = 'updates_rw'
   AND acl_entry IN ('updates#updates#settingsWin',
                     'updates#updates#products',
                     'updates#updates#products#tabwin',
                     'updates#updates#products#tablinux',
                     'updates#updates#automation',
                     'updates#updates#automation#tabwin',
                     'updates#updates#automation#tablinux',
                     'updates#updates#deployWinGroup',
                     'updates#updates#uninstallWinUpdate',
                     'updates#updates#upgradeWinGroup');

-- La description d une fonctionnalite est lue sur sa premiere ligne
UPDATE acl_feature_definitions
   SET description = 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits'
 WHERE feature_key = 'updates_rw';

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#settingsWin', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#products', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#products#tabwin', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#products#tablinux', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#automation', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#automation#tabwin', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#automation#tablinux', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#deployWinGroup', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#uninstallWinUpdate', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Règles|Produits', 'updates', 0, 'updates#updates#upgradeWinGroup', 'rw', 'onpremise,saas');

UPDATE version SET Number = 20;

COMMIT;
