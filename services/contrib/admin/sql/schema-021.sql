-- (c) 2026 Medulla, http://www.medulla-tech.io
--
-- Schema 021: ACL entries for merged updates pages.
-- This migration preserves the dev schema-018 change after glpiless
-- consumed schema versions 018-020 for ITSMLocal.

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

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

INSERT INTO acl_feature_definitions
    (feature_key, label, description, category, superadmin_only,
     acl_entry, access_type, install_types)
VALUES
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#products', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#products#tabwin', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#products#tablinux', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#automation', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#automation#tabwin', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#automation#tablinux', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#linuxApprovedReleases', 'rw', 'onpremise,saas'),
('updates_rw', 'Mises a jour - actions (approuver, deployer, exclure...)',
 'Deploiement de mises a jour|Approbation|Exclusion|Listes blanche/noire/grise|Regles|Produits',
 'updates', 0, 'updates#updates#linuxAutoUpdatePolicy', 'rw', 'onpremise,saas');

UPDATE version SET Number = 21 WHERE Number < 21;

COMMIT;
