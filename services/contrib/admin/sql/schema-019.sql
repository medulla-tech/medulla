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
-- Schema 019 : droits du module reflex (supervision par sondes)
--
-- Sept fonctionnalites, separees selon ce qu elles engagent :
-- consulter, acquitter, gerer ses propres sondes, les poser sur des
-- machines, configurer les notifications, regler la conservation des
-- donnees, administrer le module.
--
-- La configuration des notifications est distinguee du reste : elle envoie
-- des messages hors du produit.
-- ----------------------------------------------------------------------

-- Nouvelle categorie : la supervision n est ni de la securite ni de
-- l inventaire, et le module a vocation a s etoffer.
INSERT IGNORE INTO acl_categories (category_key, label, display_order) VALUES
('monitoring', 'Supervision', 6);

-- Recaler l ordre d affichage des categories suivantes
UPDATE acl_categories SET display_order = 7 WHERE category_key = 'updates';
UPDATE acl_categories SET display_order = 8 WHERE category_key = 'history';
UPDATE acl_categories SET display_order = 9 WHERE category_key = 'admin';

DELETE FROM acl_feature_definitions WHERE feature_key LIKE 'reflex_%';

INSERT INTO acl_feature_definitions (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types) VALUES
-- Consultation
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#index', 'ro', 'onpremise,saas'),
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#probes', 'ro', 'onpremise,saas'),
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#probeDetail', 'ro', 'onpremise,saas'),
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#alerts', 'ro', 'onpremise,saas'),
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#alertsHistory', 'ro', 'onpremise,saas'),
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#machines', 'ro', 'onpremise,saas'),
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#machineDetail', 'ro', 'onpremise,saas'),
('reflex_ro', 'Supervision - consultation', 'Tableau de bord|Sondes|Alertes|Historique|État des postes', 'monitoring', 0, 'reflex#reflex#ajaxAlertDetail', 'ro', 'onpremise,saas'),

-- Acquittement des alertes
('reflex_ack', 'Supervision - acquittement des alertes', 'Acquitter une alerte|Acquittement en masse', 'monitoring', 0, 'reflex#reflex#ajaxAckAlert', 'rw', 'onpremise,saas'),
('reflex_ack', 'Supervision - acquittement des alertes', 'Acquitter une alerte|Acquittement en masse', 'monitoring', 0, 'reflex#reflex#ajaxAckAlertsBulk', 'rw', 'onpremise,saas'),

-- Sondes personnelles : creer, modifier, partager les siennes.
-- La portee globale est reservee aux sondes livrees : le partage s arrete a
-- l entite.
('reflex_probes_rw', 'Supervision - mes sondes', 'Création de sondes|Modification|Duplication|Suppression|Portée privée ou partagée', 'monitoring', 0, 'reflex#reflex#probeEdit', 'rw', 'onpremise,saas'),
('reflex_probes_rw', 'Supervision - mes sondes', 'Création de sondes|Modification|Duplication|Suppression|Portée privée ou partagée', 'monitoring', 0, 'reflex#reflex#ajaxDuplicateProbe', 'rw', 'onpremise,saas'),
('reflex_probes_rw', 'Supervision - mes sondes', 'Création de sondes|Modification|Duplication|Suppression|Portée privée ou partagée', 'monitoring', 0, 'reflex#reflex#ajaxDeleteProbe', 'rw', 'onpremise,saas'),
('reflex_probes_rw', 'Supervision - mes sondes', 'Création de sondes|Modification|Duplication|Suppression|Portée privée ou partagée', 'monitoring', 0, 'reflex#reflex#ajaxSetVisibility', 'rw', 'onpremise,saas'),

-- Pose des sondes sur le parc
('reflex_assign_rw', 'Supervision - pose des sondes sur les postes', 'Assignation à une machine, un groupe ou une entité|Choix de la cadence|Exception sur une machine', 'monitoring', 0, 'reflex#reflex#ajaxAssignProbe', 'rw', 'onpremise,saas'),
('reflex_assign_rw', 'Supervision - pose des sondes sur les postes', 'Assignation à une machine, un groupe ou une entité|Choix de la cadence|Exception sur une machine', 'monitoring', 0, 'reflex#reflex#ajaxUnassignProbe', 'rw', 'onpremise,saas'),
('reflex_assign_rw', 'Supervision - pose des sondes sur les postes', 'Assignation à une machine, un groupe ou une entité|Choix de la cadence|Exception sur une machine', 'monitoring', 0, 'reflex#reflex#ajaxUnassignProbesBulk', 'rw', 'onpremise,saas'),
('reflex_assign_rw', 'Supervision - pose des sondes sur les postes', 'Assignation à une machine, un groupe ou une entité|Choix de la cadence|Exception sur une machine', 'monitoring', 0, 'reflex#reflex#ajaxEditAssignmentInterval', 'rw', 'onpremise,saas'),
('reflex_assign_rw', 'Supervision - pose des sondes sur les postes', 'Assignation à une machine, un groupe ou une entité|Choix de la cadence|Exception sur une machine', 'monitoring', 0, 'reflex#reflex#ajaxSearchMachines', 'rw', 'onpremise,saas'),
('reflex_assign_rw', 'Supervision - pose des sondes sur les postes', 'Assignation à une machine, un groupe ou une entité|Choix de la cadence|Exception sur une machine', 'monitoring', 0, 'reflex#reflex#ajaxExcludeProbe', 'rw', 'onpremise,saas'),
('reflex_assign_rw', 'Supervision - pose des sondes sur les postes', 'Assignation à une machine, un groupe ou une entité|Choix de la cadence|Exception sur une machine', 'monitoring', 0, 'reflex#reflex#ajaxIncludeProbe', 'rw', 'onpremise,saas'),

-- Notifications : envoie des messages hors du produit
-- L acces a la page Parametres suit le droit des onglets : sans lui, un
-- profil qui gere les notifications sans administrer le module ne pourrait
-- pas ouvrir la page qui les contient. Une entree par onglet, en plus de la
-- page : sans reflex#reflex#settings#tabchannels et #tabrules, la page
-- s ouvre et les onglets restent vides. L onglet #tabretention n est pas
-- repris : il reste a reflex_retention_rw.
--
-- Ouverte aux administrateurs d entite. Le cloisonnement est tenu par le
-- serveur : un canal porte une entite, une regle celle de son canal, et
-- chacun ne lit et ne gere que ceux des entites qu il atteint.
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#settings', 'rw', 'onpremise,saas'),
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#settings#tabchannels', 'rw', 'onpremise,saas'),
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#settings#tabrules', 'rw', 'onpremise,saas'),
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#channelEdit', 'rw', 'onpremise,saas'),
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#ajaxDeleteChannel', 'rw', 'onpremise,saas'),
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#ajaxTestChannel', 'rw', 'onpremise,saas'),
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#ruleEdit', 'rw', 'onpremise,saas'),
('reflex_notify_rw', 'Supervision - canaux et règles de notification', 'Canaux d envoi|Règles de notification|Test d envoi', 'monitoring', 0, 'reflex#reflex#ajaxDeleteRule', 'rw', 'onpremise,saas'),

-- Conservation des donnees : les durees de retention valent pour toute
-- l instance, et un raccourcissement efface a la purge suivante l historique
-- de tous les clients. Reservee au Super-Admin, et distincte des
-- notifications parce qu elle engage autre chose : ce qui est detruit, pas ce
-- qui est envoye. La page Parametres est reprise ici pour qu un profil qui ne
-- tient que ce droit puisse l ouvrir.
('reflex_retention_rw', 'Supervision - conservation des données', 'Conservation des mesures|Conservation des alertes résolues|Conservation de l historique des envois', 'monitoring', 1, 'reflex#reflex#settings', 'rw', 'onpremise,saas'),
('reflex_retention_rw', 'Supervision - conservation des données', 'Conservation des mesures|Conservation des alertes résolues|Conservation de l historique des envois', 'monitoring', 1, 'reflex#reflex#settings#tabretention', 'rw', 'onpremise,saas'),

-- Administration du module
-- L interrupteur d une sonde et l adaptation d une condition livree portent
-- sur le catalogue commun : eteindre 'cpu_load' l eteint pour l instance
-- entiere, et un seuil adapte vaut pour tout le monde. Le backend ne peut pas
-- juger de ce droit, une sonde livree n appartenant a personne : c est cette
-- entree qui le porte.
--
-- Pas de reflex#reflex#settings ici : les deux actions se declenchent depuis
-- la fiche d une sonde, jamais depuis la page Parametres.
('reflex_admin_rw', 'Supervision - administration du module', 'Adapter une condition livrée', 'monitoring', 0, 'reflex#reflex#ajaxEditCondition', 'rw', 'onpremise,saas');

-- Attribution aux profils existants
INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level) VALUES
('Super-Admin', 'reflex_ro',         'ro'),
('Super-Admin', 'reflex_ack',        'rw'),
('Super-Admin', 'reflex_probes_rw',  'rw'),
('Super-Admin', 'reflex_assign_rw',  'rw'),
('Super-Admin', 'reflex_notify_rw',  'rw'),
('Super-Admin', 'reflex_retention_rw', 'rw'),
('Super-Admin', 'reflex_admin_rw',   'rw'),
('Admin',       'reflex_ro',         'ro'),
('Admin',       'reflex_ack',        'rw'),
('Admin',       'reflex_probes_rw',  'rw'),
('Admin',       'reflex_assign_rw',  'rw'),
('Admin',       'reflex_notify_rw',  'rw'),
('Admin',       'reflex_admin_rw',   'rw'),
-- Un technicien consulte et acquitte, et gere ses propres sondes.
-- Il ne configure pas les envois.
('Technician',  'reflex_ro',         'ro'),
('Technician',  'reflex_ack',        'rw'),
('Technician',  'reflex_probes_rw',  'rw');

UPDATE version SET Number = 19;

COMMIT;
