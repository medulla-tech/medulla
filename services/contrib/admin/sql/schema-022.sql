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
-- Schema 022 : deploiement d une mise a jour du Store depuis le module
-- securite (roue dentee de la liste des logiciels vulnerables).
--
-- La page security#security#deployStoreUpdate n avait aucune entree ACL :
-- la roue dentee restait grisee pour tout compte non root.
-- ----------------------------------------------------------------------

DELETE FROM acl_feature_definitions
 WHERE feature_key = 'store_rw'
   AND acl_entry = 'security#security#deployStoreUpdate';

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection
  machines/groupes', 'deployment', 0, 'security#security#deployStoreUpdate', 'rw', 'onpremise,saas');

-- ----------------------------------------------------------------------
-- La page security#security#softwares (liste des logiciels vulnerables,
-- qui porte la roue dentee) n avait pas d entree ACL non plus. Elle suit
-- la consultation du module, comme security#security#index.
-- ----------------------------------------------------------------------

DELETE FROM acl_feature_definitions
 WHERE feature_key = 'computer_management_ro'
   AND acl_entry = 'security#security#softwares';

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types)
SELECT feature_key, label, description, category, superadmin_only, 'security#security#softwares', access_type, install_types
  FROM acl_feature_definitions
 WHERE feature_key = 'computer_management_ro'
   AND acl_entry = 'security#security#index';

UPDATE version SET Number = 22;

COMMIT;
