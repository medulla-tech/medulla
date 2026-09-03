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

SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

DELETE FROM acl_feature_definitions
 WHERE feature_key = 'config_files_rw'
    OR acl_entry IN ('store#store#deploy#tabmachines',
                     'store#store#deploy#tabgroups',
                     'store#store#unsubscribe',
                     'xmppmaster#xmppmaster#shareqa',
                     'xmppmaster#xmppmaster#xmppMonitoring',
                     'xmppmaster#xmppmaster#remoteeditorconfigurationrelay',
                     'admin#admin#websocketLogs');

DELETE FROM acl_feature_definitions
 WHERE feature_key = 'computer_management_rw'
   AND acl_entry = 'xmppmaster#xmppmaster#listfichierconf';

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection machines/groupes', 'deployment', 0, 'store#store#deploy#tabmachines', 'rw', 'onpremise,saas'),
('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection machines/groupes', 'deployment', 0, 'store#store#deploy#tabgroups', 'rw', 'onpremise,saas'),
('store_rw', 'Store - gestion (abonner, déployer)', 'Abonnement aux logiciels|Désabonnement|Déploiement depuis le Store|Sélection machines/groupes', 'deployment', 0, 'store#store#unsubscribe', 'rw', 'onpremise,saas'),
('package_deployment_rw', 'Déploiement - actions (lancer, planifier, convergence...)', 'Lancement de déploiements|Commandes avancées|Convergence|Wake-on-LAN|Console XMPP|Quick Actions', 'deployment', 0, 'xmppmaster#xmppmaster#shareqa', 'rw', 'onpremise,saas'),
('computer_management_ro', 'Postes - consultation (monitoring, CVE, sécurité...)', 'Monitoring|CVE par machine/entité/groupe|Détails logiciels|Vulnérabilités', 'security', 0, 'xmppmaster#xmppmaster#xmppMonitoring', 'ro', 'onpremise,saas'),
('admin_technician', 'Consultation infrastructure (relais, clusters...)', 'Relais|Paquets|Règles|Clusters|Entités|Téléchargement agent', 'admin', 0, 'admin#admin#websocketLogs', 'ro', 'onpremise'),
('admin_superadmin', 'Infrastructure serveur (relais, clusters, règles...)', 'Relais|Clusters|Règles de routage|Entités|Providers OIDC|Mises à jour serveur|Régénération agent', 'admin', 1, 'xmppmaster#xmppmaster#remoteeditorconfigurationrelay', 'rw', 'onpremise'),
('config_files_rw', 'Édition des fichiers de configuration sur un poste', 'Liste des fichiers de configuration|Éditeur distant|Enregistrement sur le poste', 'inventory', 0, 'xmppmaster#xmppmaster#listfichierconf', 'rw', 'onpremise,saas'),
('config_files_rw', 'Édition des fichiers de configuration sur un poste', 'Liste des fichiers de configuration|Éditeur distant|Enregistrement sur le poste', 'inventory', 0, 'xmppmaster#xmppmaster#remoteeditorconfigurationlist', 'rw', 'onpremise,saas'),
('config_files_rw', 'Édition des fichiers de configuration sur un poste', 'Liste des fichiers de configuration|Éditeur distant|Enregistrement sur le poste', 'inventory', 0, 'xmppmaster#xmppmaster#remoteeditorconfiguration', 'rw', 'onpremise,saas');

INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level) VALUES
  ('Super-Admin', 'config_files_rw', 'rw');

UPDATE version SET Number = 17;

COMMIT;
