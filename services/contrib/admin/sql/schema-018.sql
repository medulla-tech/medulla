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
-- Schema 018 : pages "products" et "automation" du module updates
--
-- Quatre pages de configuration sont fusionnees deux a deux en pages a
-- onglets Windows / Linux :
--   approve_products      + linuxApprovedReleases  -> products
--   approve_rules         + linuxAutoUpdatePolicy  -> automation
--
-- Les quatre anciennes pages redirigent vers l onglet correspondant,
-- donc leurs entrees ACL restent en place.
--
-- Les onglets sont soumis a leur propre ACL : sans les entrees #tabwin
-- et #tablinux, un utilisateur non root n en voit aucun.
-- ----------------------------------------------------------------------

-- acl_feature_definitions n a pas de contrainte d unicite : on purge
-- avant d inserer pour que le script reste rejouable.
DELETE FROM acl_feature_definitions
 WHERE feature_key = 'updates_rw'
   AND acl_entry IN ('updates#updates#products',
                     'updates#updates#products#tabwin',
                     'updates#updates#products#tablinux',
                     'updates#updates#automation',
                     'updates#updates#automation#tabwin',
                     'updates#updates#automation#tablinux',
                     'updates#updates#linuxApprovedReleases',
                     'updates#updates#linuxAutoUpdatePolicy');

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#products', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#products#tabwin', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#products#tablinux', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#automation', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#automation#tabwin', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#automation#tablinux', 'rw', 'onpremise,saas');

-- Les deux anciennes pages Linux n avaient aucune entree ACL : elles
-- n etaient atteignables que par un compte root. On les couvre au passage.
INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#linuxApprovedReleases', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises à jour - actions (approuver, déployer, exclure...)', 'Déploiement de mises à jour|Approbation|Exclusion|Listes blanche/noire/grise|Règles|Produits', 'updates', 0, 'updates#updates#linuxAutoUpdatePolicy', 'rw', 'onpremise,saas');

UPDATE version SET Number = 18;

COMMIT;
