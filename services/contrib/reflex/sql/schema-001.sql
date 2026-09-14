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

-- ----------------------------------------------------------------------
-- Reflex Module - Schema 001
-- Supervision par sondes (module reflex) : catalogue, conditions, assignations,
-- mesures, alertes et notifications.
--
-- L'agent mesure, le serveur evalue et notifie. Aucune condition n'est
-- evaluee sur le poste, aucun code utilisateur n'est execute sur le serveur.
--
-- Lien avec le parc : machines_id (xmppmaster.machines.id) et
-- uuid_inventorymachine (format UUID<glpi_id>), sans cle etrangere
-- inter-bases, comme le module security.
-- ----------------------------------------------------------------------


-- ----------------------------------------------------------------------
-- Table: probes
-- Definition d'une sonde. Une sonde dit QUOI mesurer ; les conditions
-- disent QUAND alerter ; les assignations disent OU et A QUELLE CADENCE.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probes` (
    `id` int NOT NULL AUTO_INCREMENT,
    `probe_key` varchar(128) NOT NULL COMMENT 'Identifiant technique stable, ex: cpu_load',
    `label` varchar(255) NOT NULL,
    `description` text NULL,
    `category` varchar(64) NOT NULL DEFAULT 'system' COMMENT 'system, security, network, storage, service, application',
    `probe_type` enum('builtin','script') NOT NULL DEFAULT 'builtin' COMMENT 'builtin = collecteurs natifs de l agent (sondes livrees et leurs copies) ; script = sonde personnelle, une commande par systeme dans probe_collectors',
    `metric_key` varchar(128) NOT NULL COMMENT 'Mesure produite, ex: cpu.percent_global',
    `unit` varchar(32) NULL DEFAULT NULL,
    `value_type` enum('numeric','text','boolean') NOT NULL DEFAULT 'numeric',

    -- Toutes les sondes numeriques et booleennes ne meritent pas une courbe
    -- sur la fiche machine. Le nombre d'administrateurs locaux d'un poste ne
    -- bouge pas : sa courbe est une ligne plate, qui prend la place d'une
    -- courbe utile sans rien apprendre.
    --
    -- C'est une propriete de la sonde, pas une decision d'affichage. Elle ne
    -- se deduit ni de l'absence de condition d'alerte -- pending_updates et
    -- process_count n'en ont aucune et meritent leur courbe -- ni de la
    -- variation constatee, la periode consultee etant un choix du lecteur
    -- recharge en ajax.
    --
    -- Defaut a 1 : une sonde personnelle creee depuis la console est tracable
    -- sans que personne ait rien a regler.
    `plottable` tinyint(1) NOT NULL DEFAULT 1 COMMENT '1 = la fiche machine trace la courbe des mesures de cette sonde ; 0 = la valeur s affiche sans courbe. Propriete de la sonde, pas de la periode consultee',
    `os_support` set('windows','linux','darwin') NOT NULL DEFAULT 'windows,linux' COMMENT 'Doit refleter les lignes de probe_collectors : un OS liste ici sans collecteur ne sera jamais mesure',
    `min_interval_seconds` int NOT NULL DEFAULT 300 COMMENT 'Cadence minimale admise pour cette sonde',
    `default_interval_seconds` int NOT NULL DEFAULT 300,
    `is_builtin` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 = livree avec le produit, non modifiable, non supprimable',
    `visibility` enum('private','entity','global') NOT NULL DEFAULT 'entity' COMMENT 'private = le proprietaire seul ; entity = tous ceux qui ont acces a l entite portee par entity_id, c est le defaut a la creation ; global = RESERVE aux sondes livrees (is_builtin = 1), ce n est pas un choix offert a l utilisateur mais la consequence d etre livre avec le produit',
    `entity_id` varchar(255) NULL DEFAULT NULL COMMENT 'Entite portee par la sonde quand visibility = entity, NULL sinon. Id d entite GLPI, meme type et meme convention que probe_assignments.target_id : deux representations differentes de la meme chose dans la meme base seraient un piege. L entite est stockee sur la sonde et non deduite du proprietaire : si celui-ci change d entite, sa sonde ne doit pas changer de public sans que personne l ait decide',
    `owner_login` varchar(255) NULL DEFAULT NULL COMMENT 'NULL pour les sondes livrees',
    `enabled` tinyint(1) NOT NULL DEFAULT 1,
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_probe_key` (`probe_key`),
    KEY `idx_visibility_owner` (`visibility`, `owner_login`) COMMENT 'Sondes globales et sondes privees d un utilisateur',
    KEY `idx_visibility_entity` (`visibility`, `entity_id`) COMMENT 'Sondes visibles par une entite. Index separe et non colonne ajoutee au precedent : dans (visibility, owner_login, entity_id), owner_login s intercale et coupe l acces a entity_id pour une recherche qui ne porte pas sur le proprietaire',
    KEY `idx_category` (`category`),
    KEY `idx_enabled` (`enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_shipped_labels
-- Nom de chaque sonde livree dans chaque langue de la console. Le nom d une
-- sonde est unique, et une sonde livree occupe son nom dans toutes les langues
-- ou la console l affiche : sans cette table, un utilisateur francophone
-- pouvait creer une sonde nommee Charge processeur, et voir ensuite deux
-- sondes de ce nom dans sa liste. Le controle d unicite lit cette table, en
-- base, et non les catalogues de traduction : la couche base ne va pas
-- chercher des fichiers sur le disque du serveur web.
--
-- PIEGE. C est une COPIE des libelles portes par les catalogues gettext de la
-- console, pas leur source. Une traduction corrigee dans un .po ne se propage
-- pas ici toute seule : elle doit etre reprise par un schema ulterieur, sinon
-- le nom traduit cesse d etre reserve et redevient creable par un utilisateur.
--
-- Une seule langue par ligne, et le couple (probe_key, language) pour cle :
-- une sonde livree a exactement un nom par langue.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_shipped_labels` (
    `probe_key` varchar(128) NOT NULL COMMENT 'Sonde livree, meme cle et meme longueur que probes.probe_key',
    `language` varchar(16) NOT NULL COMMENT 'en, fr_FR, es_ES : la langue dans laquelle la console affiche ce libelle',
    `label` varchar(255) NOT NULL,
    PRIMARY KEY (`probe_key`, `language`),
    KEY `idx_label` (`label`) COMMENT 'Le controle d unicite part du nom saisi, jamais de la sonde'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_conditions
-- Condition d'alerte attachee a une sonde. Plusieurs conditions permettent
-- de graduer : avertissement a 80, critique a 95.
-- Declaratif uniquement : aucun code n'est stocke ni execute.
--
-- Meme motif que la table settings : default_* porte ce que livre le produit,
-- la colonne nue porte ce que l exploitant a choisi, et NULL signifie qu il
-- n a rien change et suit donc le produit. Toute lecture effective se fait en
-- COALESCE(surcharge, defaut). Un seuil livre a 90 reste corrigeable chez tous
-- les clients par un schema ulterieur sans ecraser celui qui l a deja regle.
--
-- NULL comme suit le produit ne perd rien : un champ hors sujet pour une
-- condition, par exemple threshold_value sur une comparaison de texte, est
-- NULL des deux cotes et COALESCE(NULL, NULL) vaut NULL.
--
-- operator et display_order n ont deliberement pas de surcharge : changer
-- l operateur change la nature de la condition, pas son reglage. Qui veut
-- comparer autrement duplique la sonde.
--
-- Pour une sonde personnelle (is_builtin = 0), la definition du proprietaire
-- s ecrit dans les colonnes default_* et les surcharges restent NULL : il n y
-- a pas de produit a suivre, il est son propre produit.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_conditions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `probe_id` int NOT NULL,
    `operator` enum('gt','gte','lt','lte','eq','ne','between','outside','changed') NOT NULL COMMENT 'Non surchargeable : il definit la nature de la condition',

    -- Valeurs livrees par le produit, ou definition du proprietaire pour une
    -- sonde personnelle. Un schema ulterieur peut les corriger.
    `default_threshold_value` double NULL DEFAULT NULL,
    `default_threshold_value2` double NULL DEFAULT NULL COMMENT 'Borne haute pour between et outside',
    `default_threshold_text` varchar(255) NULL DEFAULT NULL COMMENT 'Comparaison sur valeur non numerique',
    `default_duration_seconds` int NOT NULL DEFAULT 0 COMMENT 'Condition vraie en continu pendant N secondes avant de lever ; 0 = immediat',
    `default_severity` enum('info','medium','high','critical') NOT NULL DEFAULT 'medium',
    `default_message_template` varchar(512) NULL DEFAULT NULL COMMENT 'Libelle de l alerte, variables @@machine@@ @@value@@ @@threshold@@ @@instance@@. @@instance@@ nomme la mesure quand la sonde en remonte plusieurs par machine, ex: le point de montage ; vide sur une sonde qui ne remonte qu une valeur',
    `default_enabled` tinyint(1) NOT NULL DEFAULT 1,

    -- Surcharges de l exploitant. NULL tant qu il n a rien change : la valeur
    -- livree s applique alors, et le suit a chaque mise a jour.
    `threshold_value` double NULL DEFAULT NULL,
    `threshold_value2` double NULL DEFAULT NULL,
    `threshold_text` varchar(255) NULL DEFAULT NULL,
    `duration_seconds` int NULL DEFAULT NULL,
    `severity` enum('info','medium','high','critical') NULL DEFAULT NULL,
    `message_template` varchar(512) NULL DEFAULT NULL,
    `enabled` tinyint(1) NULL DEFAULT NULL,

    `customized_by` varchar(255) NULL DEFAULT NULL COMMENT 'Qui a regle, pour que le support sache qu un seuil n est plus celui du produit',
    `customized_at` timestamp NULL DEFAULT NULL,
    `display_order` int NOT NULL DEFAULT 0 COMMENT 'Non surchargeable : il porte l unicite qui rend le seed idempotent',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_probe_order` (`probe_id`, `display_order`) COMMENT 'Rend le seed idempotent et fixe l ordre',
    KEY `idx_probe` (`probe_id`) COMMENT 'Sans enabled : l activation effective est un COALESCE, un index ne peut pas la filtrer',
    CONSTRAINT `fk_condition_probe` FOREIGN KEY (`probe_id`)
        REFERENCES `probes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_condition_overrides
-- Reglage d une condition pour UNE entite. Le catalogue est commun a
-- l instance, mais une instance porte plusieurs clients separes par entite :
-- sans cette table, un seuil regle vaut pour tout le monde a la fois.
--
-- Trois niveaux, du plus precis au plus general :
--   1. probe_condition_overrides, le reglage de l entite ;
--   2. probe_conditions, colonnes nues, le reglage de l exploitant pour
--      l instance entiere ;
--   3. probe_conditions, colonnes default_*, la valeur livree.
-- Toute lecture effective se fait en
-- COALESCE(override, surcharge instance, defaut), colonne par colonne : une
-- entite qui ne regle que le seuil garde la gravite du niveau au-dessus.
-- Rien d existant ne change de sens, le niveau 1 s intercale seulement devant.
--
-- Meme decoupage que probe_conditions : les colonnes surchargeables sont
-- celles du reglage, jamais operator ni display_order, qui definissent la
-- nature de la condition.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_condition_overrides` (
    `id` int NOT NULL AUTO_INCREMENT,
    `condition_id` int NOT NULL,
    `entity_id` varchar(255) NOT NULL COMMENT 'Id d entite GLPI, meme type et meme convention que probe_assignments.target_id. 0 est l entite racine, une entite valide et non une absence',

    `threshold_value` double NULL DEFAULT NULL,
    `threshold_value2` double NULL DEFAULT NULL,
    `threshold_text` varchar(255) NULL DEFAULT NULL,
    `duration_seconds` int NULL DEFAULT NULL,
    `severity` enum('info','medium','high','critical') NULL DEFAULT NULL,
    `message_template` varchar(512) NULL DEFAULT NULL,
    `enabled` tinyint(1) NULL DEFAULT NULL,

    `customized_by` varchar(255) NOT NULL,
    `customized_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_condition_entity` (`condition_id`, `entity_id`) COMMENT 'Un reglage au plus par condition et par entite. Sert aussi la lecture, qui porte toujours sur ce couple : un index supplementaire ferait doublon',
    CONSTRAINT `fk_override_condition` FOREIGN KEY (`condition_id`)
        REFERENCES `probe_conditions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_collectors
-- COMMENT une sonde est mesuree, par systeme d exploitation.
--
-- `collector` est l identifiant d un collecteur IMPLEMENTE DANS L AGENT,
-- qui refuse tout identifiant qu il ne connait pas. Une sonde livree nomme
-- un collecteur natif. Une sonde personnelle (probe_type = script) porte
-- sa commande dans params_json, {"command": "..."} : script.sh pour linux et
-- darwin, script.powershell pour windows ; la premiere ligne affichee est
-- la mesure.
--
-- `implementation_note` est PUREMENT DOCUMENTAIRE : elle sert a l interface
-- et au support pour expliquer d ou vient la valeur. Elle n est jamais
-- executee ni interpretee.
--
-- Une sonde sans ligne pour un OS donne n y est pas mesurable : l agent
-- remonte le statut unavailable plutot que rien, pour que l absence soit
-- visible au lieu d etre silencieuse.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_collectors` (
    `id` int NOT NULL AUTO_INCREMENT,
    `probe_id` int NOT NULL,
    `os` enum('windows','linux','darwin') NOT NULL,
    `collector` varchar(128) NOT NULL COMMENT 'Identifiant du collecteur natif implemente dans l agent',
    `params_json` text NULL COMMENT 'Parametres du collecteur, ex: {"window_minutes": 15}, ou {"command": "..."} pour script.sh / script.powershell',
    `implementation_note` varchar(512) NULL COMMENT 'DOCUMENTAIRE uniquement, jamais execute',
    `requires` varchar(255) NULL COMMENT 'Dependance necessaire sur le poste, ex: smartmontools',
    `enabled` tinyint(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_probe_os` (`probe_id`, `os`),
    KEY `idx_collector` (`collector`),
    CONSTRAINT `fk_collector_probe` FOREIGN KEY (`probe_id`)
        REFERENCES `probes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_assignments
-- Ou une sonde est posee et a quelle cadence. Poser une sonde et creer une
-- sonde sont deux gestes distincts.
--
-- Aucune colonne enabled ici : une assignation existe ou n existe pas, on
-- pose une sonde ou on la retire. L interrupteur d exploitation est
-- probes.enabled, actionnable sur toutes les sondes ; un second interrupteur
-- par assignation n aurait fait que multiplier les endroits ou chercher
-- pourquoi une sonde ne remonte rien.
--
-- Une pose appartient a une seule entite. Il n existe pas de pose sur tout
-- le parc : le geste existe toujours dans la console, mais le serveur l etend
-- en une pose par entite atteinte. Une ligne unique appartenant a plusieurs
-- clients a la fois n avait pas de proprietaire : le client qui la retirait
-- arretait la mesure chez les autres, et sa cadence debordait chez eux.
-- Chaque client tient desormais la ligne qui vise son entite, la modifie et
-- la retire sans toucher aux autres ; l exploitant peut la reposer.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_assignments` (
    `id` int NOT NULL AUTO_INCREMENT,
    `probe_id` int NOT NULL,
    `target_type` enum('machine','group','entity') NOT NULL COMMENT 'Aucune valeur pour tout le parc : ce geste s etend en une pose par entite',
    `target_id` varchar(255) NOT NULL COMMENT 'machines_id, id de groupe dyngroup ou id d entite GLPI selon target_type. Jamais NULL : MySQL tient deux NULL pour distincts et uk_probe_target ne verrait pas une seconde pose. Pas de valeur par defaut : l appelant nomme toujours sa cible',
    `interval_seconds` int NOT NULL DEFAULT 300 COMMENT 'Borne a la creation par probes.min_interval_seconds. Aucun plancher global : la console propose une liste fermee de cadences',
    `created_by` varchar(255) NOT NULL COMMENT 'Qui a pose la sonde en dernier. Trace : la pose appartient a l entite visee et non a son auteur, et se lit, se modifie et se retire par qui atteint cette entite',
    `language` varchar(5) NULL DEFAULT NULL COMMENT 'Langue de celui qui a pose la sonde, ex: fr_FR, es_ES, en_US. Elle decide de la langue des notifications nees de cette pose : un exploitant espagnol travaille avec des collegues espagnols, sa langue est donc celle de ses destinataires. NULL = anglais, la langue du contenu livre en base, sans traduction. Stockee ici et nulle part ailleurs : une seconde source pour la meme information se contredirait',
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_probe_target` (`probe_id`, `target_type`, `target_id`),
    KEY `idx_target` (`target_type`, `target_id`),
    CONSTRAINT `fk_assignment_probe` FOREIGN KEY (`probe_id`)
        REFERENCES `probes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: settings
-- Reglages d exploitation du module. Le fichier .ini ne garde que ce qui est
-- lu avant toute connexion : la base elle-meme, la cle de chiffrement, le
-- niveau de log et l activation du plugin. Tout le reste vit ici, editable
-- depuis la console, sans intervention sur le serveur.
--
-- Aucun libelle en base : la console est traduite, donc l intitule et l aide
-- se deduisent de setting_key dans les catalogues. Une phrase stockee ici
-- serait figee dans la langue de celui qui l a ecrite.
--
-- exposed distingue le reglage d exploitation, montre dans Parametres, de la
-- caracteristique de fonctionnement qu un exploitant n a pas a toucher : mal
-- reglee, elle fait disparaitre des machines de l ecran ou bloque les
-- insertions. Elle reste modifiable en base par qui sait ce qu il fait.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `settings` (
    `setting_key` varchar(128) NOT NULL,
    `default_value` varchar(512) NOT NULL COMMENT 'Valeur livree par le produit. Un schema ulterieur la met a jour chez tous les clients',
    `value` varchar(512) NULL DEFAULT NULL COMMENT 'Valeur choisie par l exploitant. NULL tant qu il n a rien change : la valeur livree s applique alors, et le suit a chaque mise a jour',
    `value_type` enum('int','bool','string') NOT NULL DEFAULT 'string',
    `exposed` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Presente dans l onglet Parametres',
    `updated_by` varchar(255) NULL DEFAULT NULL,
    `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Valeurs livrees. ON DUPLICATE KEY UPDATE ne touche que default_value :
-- un schema ulterieur peut donc corriger un defaut chez tous les clients,
-- sans jamais ecraser ce qu un exploitant a regle (value reste intact).
INSERT INTO `settings` (`setting_key`, `default_value`, `value_type`, `exposed`) VALUES
-- Cinq reglages produit, aucun expose : ce sont des decisions corrigeables
-- chez tous les clients par un schema ulterieur. Le sixieme, l adresse de la
-- console, est le seul expose : aucun schema ne peut la livrer, l exploitant
-- est seul a la connaitre, et elle bouge (renommage, reverse proxy, https).
-- Mal reglee elle ne produit aucun lien, jamais une panne de supervision.
--
-- Ce qui n y figure pas, deliberement. Aucun garde-fou de cadence : la
-- console propose une liste fermee de cadences, elle borne deja ce qu on
-- peut poser, et un refus au moment de poser une sonde fait conclure que le
-- produit est casse. Aucun interrupteur global de notification : couper se
-- fait en desactivant un canal ou une regle, la ou on les configure. Aucun
-- defaut de gravite ni d anti-repetition : les formulaires demandent
-- toujours ces valeurs, un defaut ne se serait jamais applique.
('retention.measures_days',               '30',   'int',    0),
('retention.alerts_resolved_days',        '365',  'int',    0),
('retention.notification_history_days',   '90',   'int',    0),
('evaluation.batch_size',                 '500',  'int',    0),
('evaluation.max_lookback_seconds',       '3600', 'int',    0),
-- Vide par defaut : le courriel d alerte n y met aucun lien tant que
-- personne n a renseigne l adresse. Un lien mort vaut moins que pas de lien.
('console.base_url',                      '',     'string', 1)
ON DUPLICATE KEY UPDATE
    `default_value` = VALUES(`default_value`),
    `value_type`    = VALUES(`value_type`),
    `exposed`       = VALUES(`exposed`);


-- ----------------------------------------------------------------------
-- Table: probe_exclusions
-- Exceptions a une sonde posee largement. Une assignation 'all', 'group' ou
-- 'entity' ne stocke aucun lien machine par machine : ce lien est calcule au
-- moment ou la configuration d un agent est fabriquee. Retirer une sonde d une
-- seule machine n a donc rien a supprimer, d ou cette seconde liste, celle des
-- exceptions.
--
-- Le hostname est duplique ici, comme dans probe_measures : afficher une
-- exclusion ne doit pas dependre d une jointure vers xmppmaster.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_exclusions` (
    `id` int NOT NULL AUTO_INCREMENT,
    `probe_id` int NOT NULL,
    `machines_id` int NOT NULL COMMENT 'xmppmaster.machines.id, pas de FK inter-bases',
    `hostname` varchar(255) NOT NULL COMMENT 'Nom au moment de l exclusion, pour l affichage',
    `reason` varchar(255) NULL DEFAULT NULL,
    `created_by` varchar(255) NOT NULL,
    `created_at` datetime NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_probe_machine` (`probe_id`, `machines_id`) COMMENT 'Une machine n est exclue qu une fois d une sonde',
    KEY `idx_machine` (`machines_id`) COMMENT 'Exclusions d une machine, pour sa fiche',
    CONSTRAINT `fk_exclusion_probe` FOREIGN KEY (`probe_id`)
        REFERENCES `probes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_agent_config
-- Suivi de la configuration de sondes distribuee a chaque agent.
--
-- Distribution en pull et push : l agent reclame sa configuration au
-- demarrage et periodiquement, le serveur en pousse une quand elle change.
-- Le push seul raterait tout agent hors ligne au mauvais moment, le pull
-- seul ajouterait de la latence a chaque modification.
--
-- config_version est calcule par le serveur a partir des assignations
-- applicables a la machine. L agent renvoie la version qu il applique
-- reellement : l ecart entre sent_version et acked_version rend visible un
-- agent qui n a pas pris sa configuration, au lieu de le laisser silencieux.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_agent_config` (
    `id` int NOT NULL AUTO_INCREMENT,
    `machines_id` int NOT NULL,
    `hostname` varchar(255) NOT NULL,
    `sent_version` varchar(64) NULL DEFAULT NULL COMMENT 'Empreinte de la configuration envoyee',
    `sent_at` datetime NULL DEFAULT NULL,
    `acked_version` varchar(64) NULL DEFAULT NULL COMMENT 'Empreinte que l agent declare appliquer',
    `acked_at` datetime NULL DEFAULT NULL,
    `probe_count` int NOT NULL DEFAULT 0 COMMENT 'Nombre de sondes actives sur ce poste',
    `last_error` varchar(512) NULL DEFAULT NULL COMMENT 'Erreur remontee par l agent, ex: collecteur inconnu',
    `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_machine` (`machines_id`),
    KEY `idx_hostname` (`hostname`),
    KEY `idx_drift` (`sent_version`, `acked_version`) COMMENT 'Reperage des agents en ecart de configuration'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_config_changes
-- File d attente des changements de configuration : une ligne par geste qui
-- change ce qu une machine doit mesurer. Ecrite par le plugin mmc, lue et
-- videe par le substitut, qui pousse la configuration aux machines touchees.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_config_changes` (
    `id` bigint unsigned NOT NULL AUTO_INCREMENT,
    `scope_type` enum('machine','group','entity','all','probe') NOT NULL,
    `scope_id` int NULL DEFAULT NULL COMMENT 'xmppmaster.machines.id, id de groupe dyngroup, id d entite GLPI ou probes.id selon scope_type. NULL quand scope_type = all',
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: probe_measures
-- Mesures remontees par les agents. Table volumineuse : c'est elle qui
-- dimensionne la base et la politique de purge.
--
-- collected_at (horodatage du poste) et received_at (horodatage serveur)
-- sont distincts volontairement : l ecart revele un poste deconnecte qui
-- rejoue son retard.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `probe_measures` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `machines_id` int NOT NULL COMMENT 'xmppmaster.machines.id, pas de FK inter-bases',
    `uuid_inventorymachine` varchar(45) NULL DEFAULT NULL COMMENT 'Format UUID<glpi_id>, jointure GLPI et security',
    `hostname` varchar(255) NOT NULL,
    `probe_id` int NOT NULL,
    `metric_key` varchar(128) NOT NULL,
    `value_num` double NULL DEFAULT NULL,
    `value_text` varchar(512) NULL DEFAULT NULL,
    `unit` varchar(32) NULL DEFAULT NULL,
    `status` enum('ok','warning','error','unavailable') NOT NULL DEFAULT 'ok' COMMENT 'Etat de la mesure elle-meme, pas de la condition',

    -- 512 caracteres et non 255 : une liste de comptes serialisee en JSON
    -- depasse 255 des la dizaine de comptes, et une troncature silencieuse
    -- rendrait le JSON illisible plutot que raccourci. 512, comme value_text
    -- de la meme table.
    `detail` varchar(512) NULL DEFAULT NULL COMMENT 'Contenu qui explique la mesure, conserve quel que soit son statut : soit un texte libre, en anglais, donne par l agent -- le motif d une mesure non mesurable --, soit un objet JSON {"items": [...]} quand la mesure porte un contenu structure, comme la liste des comptes de la sonde des administrateurs locaux. NULL quand il n y a rien a dire',
    `collected_at` datetime(3) NOT NULL COMMENT 'Horodatage pose par le poste : soumis a la derive d horloge, ne jamais comparer a NOW()',
    `received_at` timestamp(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT 'Horodatage pose par le serveur : seule reference pour la fraicheur, les durees et la purge. Milliseconde exigee : une duree de condition se juge sur des ecarts, et une troncature a la seconde y introduit une erreur qui decide de l alerte',
    PRIMARY KEY (`id`),
    KEY `idx_machine_probe_time` (`machines_id`, `probe_id`, `received_at`) COMMENT 'Series temporelles et derniere mesure par sonde : sur received_at, la seule horloge fiable',
    KEY `idx_probe_time` (`probe_id`, `collected_at`),
    KEY `idx_received` (`received_at`) COMMENT 'Purge par anciennete, sur l horloge du serveur',
    KEY `idx_recent_activity` (`received_at`, `machines_id`, `probe_id`) COMMENT 'Agregats bornes des pages Machines et tableau de bord : sans lui, connaitre l activite recente impose de parcourir tout l historique',
    KEY `idx_hostname` (`hostname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: alerts
-- Alerte levee par une condition. Une condition qui reste vraie ne cree pas
-- une alerte par cycle : elle met a jour last_seen_at et occurrence_count
-- de l alerte ouverte. C'est la difference entre une alerte et un evenement.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `alerts` (
    `id` int NOT NULL AUTO_INCREMENT,
    `probe_id` int NOT NULL,
    `condition_id` int NULL DEFAULT NULL COMMENT 'NULL si la condition a ete supprimee depuis',
    `machines_id` int NOT NULL,
    `uuid_inventorymachine` varchar(45) NULL DEFAULT NULL,
    `hostname` varchar(255) NOT NULL,
    `severity` enum('info','medium','high','critical') NOT NULL,
    `status` enum('open','ack','resolved') NOT NULL DEFAULT 'open',
    `value_at_trigger` double NULL DEFAULT NULL,
    `value_text_at_trigger` varchar(512) NULL DEFAULT NULL,

    -- L'alerte afficherait une valeur sans dire ce qu'elle recouvre. Un arret
    -- de service inattendu se lit "Valeur : 1", et il faudrait retourner sur
    -- la fiche machine pour apprendre que le service en cause est
    -- cron.service.
    --
    -- Meme convention que les colonnes _at_trigger ci-dessous : le contenu est
    -- COPIE a l'ouverture de l'alerte et ne bouge plus. La mesure qui a
    -- declenche est une ligne de probe_measures parmi d'autres, effacee par la
    -- purge ou remplacee par la mesure suivante ; ce qui est fige ici est ce
    -- qui a REELLEMENT declenche. Relire le detail courant de la sonde ferait
    -- lire, sur une alerte ouverte sur cron.service, le nom d'un autre service
    -- arrete depuis.
    --
    -- Nullable et sans valeur par defaut : NULL quand la mesure qui a
    -- declenche ne portait pas de detail.
    --
    -- Aucun index, comme les autres _at_trigger : on la lit sur une alerte
    -- qu'on a deja en main, jamais pour en chercher une.
    --
    -- varchar(512) et non 255 : meme forme et meme largeur que
    -- probe_measures.detail, la colonne recoit sa copie caractere pour
    -- caractere. Toute autre largeur tronquerait, et une troncature rendrait
    -- un objet JSON illisible plutot que raccourci.
    `detail_at_trigger` varchar(512) NULL DEFAULT NULL COMMENT 'Contenu de la mesure qui a declenche, copie a l ouverture de l alerte et jamais remis a jour ensuite. Meme forme que probe_measures.detail : soit un texte libre, en anglais, soit un objet JSON {"items": [...]} quand la mesure porte un contenu structure. NULL quand la mesure n en portait pas',

    -- Condition figee au declenchement. condition_id ne designe que la ligne
    -- d aujourd hui : elle a pu etre reglee, ou supprimee, depuis que l alerte
    -- s est levee. Ce qui est copie ici est ce qui a REELLEMENT declenche, et
    -- ce que la fiche d alerte doit afficher. Sans cela un seuil abaisse puis
    -- retabli fait lire, sur une alerte ouverte a 24%, une condition
    -- superieure a 85% : l ecran se contredit et passe pour un bug.
    --
    -- Ce n est pas une denormalisation a nettoyer : ces colonnes ne sont
    -- jamais relues depuis probe_conditions, elles sont ecrites une fois a
    -- l ouverture de l alerte et ne bougent plus. Les types sont ceux de
    -- probe_conditions, pour qu une comparaison entre les deux n impose
    -- aucune conversion implicite.
    --
    -- Toutes nullables, sans valeur par defaut : une alerte ouverte avant
    -- l ajout de ces colonnes n a jamais porte ces valeurs et rien ne peut les
    -- reconstruire. Elle reste lisible avec des colonnes vides, que la console
    -- interprete comme condition inconnue ; un defaut y inventerait un seuil
    -- qui n a jamais existe.
    --
    -- Aucun index : on les lit sur une alerte qu on a deja en main, jamais
    -- pour en chercher une.
    `operator_at_trigger` enum('gt','gte','lt','lte','eq','ne','between','outside','changed') NULL DEFAULT NULL COMMENT 'Operateur de la condition au moment du declenchement',
    `threshold_value_at_trigger` double NULL DEFAULT NULL COMMENT 'Seuil effectif au moment du declenchement',
    `threshold_value2_at_trigger` double NULL DEFAULT NULL COMMENT 'Borne haute effective pour between et outside',
    `threshold_text_at_trigger` varchar(255) NULL DEFAULT NULL COMMENT 'Seuil texte effectif pour une comparaison non numerique',
    `duration_seconds_at_trigger` int NULL DEFAULT NULL COMMENT 'Duree exigee en continu, effective au moment du declenchement',

    `message` varchar(512) NOT NULL,
    `opened_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_seen_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Derniere confirmation de la condition',
    `occurrence_count` int NOT NULL DEFAULT 1,
    `ack_user` varchar(255) NULL DEFAULT NULL,
    `ack_at` datetime NULL DEFAULT NULL,
    `ack_comment` varchar(512) NULL DEFAULT NULL,
    `resolved_at` datetime NULL DEFAULT NULL,
    `resolved_reason` varchar(255) NULL DEFAULT NULL COMMENT 'Renseigne quand la resolution ne vient pas d un retour a la normale, ex: sonde retiree de la machine, ou superseded quand une alerte plus grave s ouvre sur la meme machine, sonde et instance',
    PRIMARY KEY (`id`),
    KEY `idx_status_severity` (`status`, `severity`),
    KEY `idx_machine_status` (`machines_id`, `status`),
    KEY `idx_probe_status` (`probe_id`, `status`),
    KEY `idx_opened` (`opened_at`),
    KEY `idx_open_dedup` (`probe_id`, `condition_id`, `machines_id`, `status`) COMMENT 'Recherche de l alerte ouverte a mettre a jour',
    KEY `idx_resolved` (`status`, `resolved_at`) COMMENT 'Purge par lots des alertes resolues : idx_status_severity filtre le statut mais laisse le tri par date en filesort',
    CONSTRAINT `fk_alert_probe` FOREIGN KEY (`probe_id`)
        REFERENCES `probes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: notification_channels
-- Canal d envoi configure dans l interface. La v1 n implemente que le
-- courriel ; l enumeration est complete pour que l ajout d un canal soit
-- l ajout d un connecteur, sans migration.
--
-- Le secret du canal (mot de passe SMTP, jeton) est stocke ici CHIFFRE, avec
-- la cle keyAES32 de reflex.ini. Deux canaux du meme type ayant chacun leurs
-- identifiants, un renvoi vers un fichier de configuration ne suffirait pas.
--
-- Le secret n'est jamais renvoye au web : l'API expose seulement s'il est
-- renseigne ou non. Meme mecanisme que le module security.
--
-- Aucune langue ici : elle vit sur probe_assignments.language, celle de qui a
-- pose la sonde. Un canal est un moyen d envoi, pas un public.
--
-- CLOISONNEMENT. Une instance porte plusieurs clients, separes par entite. Un
-- canal contient les adresses des destinataires d un client et la
-- configuration de son serveur d envoi : il appartient TOUJOURS a une entite,
-- sans exception, et ne recoit que les alertes des machines de cette entite.
-- Une alerte de l entite B ne part jamais par un canal de l entite A. C est
-- entity_id qui porte cette appartenance ; le filtrage se fait dans le
-- backend, jamais dans l interface.
--
-- L entite racine GLPI porte l identifiant 0. C est une entite comme une
-- autre, soumise a la meme regle : elle porte les canaux de l exploitant, et
-- comme aucun client n y est rattache, ces canaux restent invisibles des
-- clients sans qu aucun cas particulier soit ecrit nulle part.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `notification_channels` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(255) NOT NULL,
    `entity_id` varchar(255) NOT NULL COMMENT 'Entite proprietaire du canal. Id d entite GLPI, meme type et meme convention que probes.entity_id et probe_assignments.target_id : deux representations differentes de la meme chose dans la meme base seraient un piege. Toujours renseignee, sans exception : un canal appartient a une entite et ne recoit que les alertes des machines de cette entite. Aucune valeur par defaut, volontairement : l appelant doit dire a qui appartient le canal, un defaut le rattacherait en silence a une entite qui n est pas la sienne. L entite racine GLPI porte l identifiant 0 ; c est une entite comme une autre, celle des canaux de l exploitant, a laquelle aucun client n est rattache',
    `channel_type` enum('email','telegram','webhook','slack','teams','sms','whatsapp') NOT NULL DEFAULT 'email',
    `config_json` text NULL COMMENT 'Parametres NON sensibles du canal',
    `secret_encrypted` text NULL DEFAULT NULL COMMENT 'Secret chiffre AES-256-CBC, IV prefixe, base64. Jamais en clair, jamais renvoye au web.',
    `enabled` tinyint(1) NOT NULL DEFAULT 1,
    `created_by` varchar(255) NOT NULL,
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_entity_name` (`entity_id`, `name`) COMMENT 'Un nom de canal est unique DANS une entite, pas dans l instance. Deux clients peuvent nommer leur canal de la meme facon, c est l entite qui les distingue : en SaaS le cas normal est un relais d envoi unique et un destinataire par client, donc des canaux qui ne different que par l entite et l adresse, et l unicite globale obligeait a inventer des noms qui n ont de sens pour personne. entity_id en tete et non name : l entite est le seul critere de recherche, toute lecture part de c.entity_id IN (...) et trie ensuite par nom, que cet ordre de colonnes sert directement ; un index mene par name ne serait jamais attaque par sa tete. Il remplace aussi idx_entity_enabled (entity_id, enabled), qui repondait au meme filtre sans servir le tri : enabled se verifie sur la poignee de canaux d une entite',
    KEY `idx_type_enabled` (`channel_type`, `enabled`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: notification_rules
-- Qui recoit quoi. Une alerte ouverte declenche l evaluation de ces regles.
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `notification_rules` (
    `id` int NOT NULL AUTO_INCREMENT,
    `channel_id` int NOT NULL,
    `probe_id` int NULL DEFAULT NULL COMMENT 'NULL = toutes les sondes',
    `min_severity` enum('info','medium','high','critical') NOT NULL DEFAULT 'high',
    `recipients` text NULL COMMENT 'Destinataires du canal, ex: liste d adresses',
    `target_filter` varchar(255) NULL DEFAULT NULL COMMENT 'Restriction par groupe ou entite',
    `cooldown_minutes` int NOT NULL DEFAULT 60 COMMENT 'Anti-repetition',
    `escalation_minutes` int NULL DEFAULT NULL COMMENT 'Second envoi si alerte critique non acquittee ; NULL = pas d escalade',
    `enabled` tinyint(1) NOT NULL DEFAULT 1,
    `created_by` varchar(255) NOT NULL,
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_channel` (`channel_id`, `enabled`),
    KEY `idx_probe` (`probe_id`),
    CONSTRAINT `fk_rule_channel` FOREIGN KEY (`channel_id`)
        REFERENCES `notification_channels` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_rule_probe` FOREIGN KEY (`probe_id`)
        REFERENCES `probes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Table: notification_history
-- Trace des envois. Sert au diagnostic et porte l anti-repetition.
-- ----------------------------------------------------------------------
-- Un envoi accepte par le serveur de messagerie ne prouve pas la remise ni la
-- lecture. accepted_at et provider_message_id tracent ce qui est reellement
-- verifiable : l acceptation par le relais et son identifiant.
--
-- La trace d un envoi ne se lit que depuis la fiche de l alerte qui l a
-- declenche : elle suit donc l alerte en cascade, comme l alerte suit sa
-- sonde. Sans cette cascade les lignes survivaient a l alerte supprimee et
-- restaient en base sans aucun ecran pour les atteindre.
CREATE TABLE IF NOT EXISTS `notification_history` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `alert_id` int NULL DEFAULT NULL,
    `channel_id` int NULL DEFAULT NULL,
    `rule_id` int NULL DEFAULT NULL,
    `recipients` text NULL,
    `status` enum('pending','sent','failed','skipped') NOT NULL DEFAULT 'pending',
    `skip_reason` varchar(255) NULL DEFAULT NULL COMMENT 'cooldown, severite insuffisante, canal desactive',
    `error_message` varchar(512) NULL DEFAULT NULL,
    `attempt_count` int NOT NULL DEFAULT 0,
    `next_retry_at` datetime NULL DEFAULT NULL COMMENT 'NULL = pas de reessai prevu',
    `accepted_at` datetime NULL DEFAULT NULL COMMENT 'Horodatage d acceptation par le serveur distant',
    `provider_message_id` varchar(255) NULL DEFAULT NULL COMMENT 'Identifiant retourne par le serveur, pour correlation',
    `is_escalation` tinyint(1) NOT NULL DEFAULT 0,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `sent_at` datetime NULL DEFAULT NULL COMMENT 'Renseigne uniquement quand status = sent',
    PRIMARY KEY (`id`),
    KEY `idx_alert` (`alert_id`) COMMENT 'Porte aussi fk_notification_alert : InnoDB exige un index de tete sur la colonne referencante',
    KEY `idx_created` (`created_at`),
    KEY `idx_retry` (`status`, `next_retry_at`) COMMENT 'File des envois a reessayer',
    KEY `idx_cooldown` (`channel_id`, `status`, `created_at`) COMMENT 'Verification anti-repetition. Sur le canal et non sur l alerte : une alerte n est notifiee qu a son ouverture, donc chercher un envoi anterieur portant son identifiant ne trouvait jamais rien. La fenetre se lit sur le couple machine + sonde a travers des alertes successives, donc sur le canal puis par jointure vers alerts',
    CONSTRAINT `fk_notification_alert` FOREIGN KEY (`alert_id`)
        REFERENCES `alerts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ----------------------------------------------------------------------
-- Catalogue initial de sondes livrees
-- is_builtin = 1, visibility = global : visibles par tous, modifiables par
-- personne. Un utilisateur qui veut une variante duplique la sonde ; la copie
-- nait en visibility = entity, portee par son entite.
--
-- LANGUE DU CONTENU LIVRE : anglais, ici et dans toutes les autres valeurs
-- que le produit ecrit (libelles, descriptions, gabarits de message, notes
-- d implementation). La base n en garde qu une seule version, et c'est elle
-- qui sert de clef de traduction a un catalogue gettext. Ce qu un exploitant
-- saisit lui-meme -- sa sonde personnelle, son message adapte dans les
-- colonnes de surcharge -- reste tel qu il l a ecrit et ne se traduit jamais.
-- Ecrire une valeur livree en francais ici, c'est la rendre intraduisible
-- pour tous les autres.
--
-- global est reserve a ce catalogue : c'est la consequence d etre livre avec
-- le produit, pas un choix offert dans la console. `visibility` figure donc
-- dans l ON DUPLICATE KEY UPDATE, avec les autres colonnes qui appartiennent
-- au produit. `entity_id` n est pas alimente et reste NULL : une sonde livree
-- n appartient a aucune entite.
--
-- ON DUPLICATE KEY UPDATE sur probe_key : un libelle, une description ou une
-- cadence corriges dans une livraison ulterieure descendent chez les clients
-- qui ont deja joue ce schema. Rien de tout cela n est modifiable par
-- l exploitant, ces colonnes appartiennent au produit.
--
-- Deux colonnes en sont exclues, et ce n est pas un oubli. `enabled` est
-- l interrupteur d exploitation : le reecrire rallumerait chez le client une
-- sonde qu il a volontairement eteinte. `probe_key` est la cle qui reconnait
-- la sonde d une livraison a l autre : la changer ne corrige pas une sonde,
-- elle en cree une seconde.
--
-- Corriger un metric_key est possible ici mais ne suffit pas : probe_measures
-- en garde une copie sur chaque mesure deja remontee. Une telle correction
-- demande un UPDATE d accompagnement dans le schema qui la porte.
-- ----------------------------------------------------------------------
INSERT INTO `probes`
    (`probe_key`, `label`, `description`, `category`, `metric_key`, `unit`, `value_type`, `plottable`,
     `os_support`, `min_interval_seconds`, `default_interval_seconds`, `is_builtin`, `visibility`)
VALUES
    ('cpu_load', 'CPU load', 'Overall processor usage of the machine, as a percentage.',
     'system', 'cpu.percent_global', '%', 'numeric', 1, 'windows,linux,darwin', 300, 300, 1, 'global'),

    ('memory_usage', 'Memory used', 'Share of physical memory in use, as a percentage.',
     'system', 'memory.ram_percent', '%', 'numeric', 1, 'windows,linux,darwin', 300, 300, 1, 'global'),

    ('swap_usage', 'Swap used', 'Share of swap space in use, as a percentage.',
     'system', 'memory.swap_percent', '%', 'numeric', 1, 'windows,linux,darwin', 300, 900, 1, 'global'),

    ('disk_usage', 'Disk space', 'Space used on each partition or volume, as a percentage.',
     'storage', 'disk.percent', '%', 'numeric', 1, 'windows,linux,darwin', 300, 900, 1, 'global'),

    ('disk_smart', 'Disk SMART status', 'Health status reported by the disk itself.',
     'storage', 'disk.smart_status', NULL, 'text', 1, 'windows,linux,darwin', 3600, 21600, 1, 'global'),

    ('service_failed', 'Failed services', 'Number of system services in a failed state.',
     'service', 'service.failed_count', 'count', 'numeric', 1, 'windows,linux,darwin', 300, 900, 1, 'global'),

    ('antivirus_status', 'Antivirus active', 'Whether an antivirus protection is present and running.',
     'security', 'security.antivirus_active', NULL, 'boolean', 1, 'windows,linux', 900, 3600, 1, 'global'),

    ('antivirus_signatures_age', 'Antivirus signature age', 'Age of the antivirus signatures, in days.',
     'security', 'security.av_signatures_age_days', 'd', 'numeric', 1, 'windows,linux', 3600, 21600, 1, 'global'),

    ('firewall_status', 'Firewall active', 'State of the local firewall.',
     'security', 'security.firewall_enabled', NULL, 'boolean', 1, 'windows,linux,darwin', 900, 3600, 1, 'global'),

    ('disk_encryption', 'Disk encryption', 'Encryption state of the system volume.',
     'security', 'security.disk_encrypted', NULL, 'boolean', 1, 'windows,linux,darwin', 3600, 21600, 1, 'global'),

    ('failed_logins', 'Failed logons', 'Number of failed authentications over the last 15 minutes. The window is part of the measure: a threshold with no period behind it means nothing.',
     'security', 'security.failed_logins_15m', 'count', 'numeric', 1, 'windows,linux,darwin', 300, 900, 1, 'global'),

    ('pending_updates', 'Pending updates', 'Number of system updates available.',
     'application', 'system.pending_updates', 'count', 'numeric', 1, 'windows,linux,darwin', 3600, 86400, 1, 'global'),

    ('reboot_required', 'Reboot required', 'The machine is waiting for a reboot to finish applying an update.',
     'application', 'system.reboot_required', NULL, 'boolean', 1, 'windows,linux', 3600, 21600, 1, 'global'),

-- Sonde load_average
--
-- Mesure la charge moyenne du systeme sur 5 minutes, rapportee au nombre de
-- coeurs et exprimee en pourcentage : rapportee aux coeurs, elle se lit de la
-- meme facon sur une machine a 2 coeurs et sur une machine a 32.
--
-- Elle ne remplace pas cpu_load et ne fait pas double emploi avec elle :
-- cpu_load donne l'occupation instantanee du processeur, la charge moyenne
-- compte aussi les taches qui attendent leur tour. Une machine peut etre a
-- 100 % de charge moyenne sans que le processeur soit sature.
--
-- Linux et macOS seulement : Windows n'expose pas de charge moyenne. Aucune
-- ligne windows dans probe_collectors, et os_support le reflete -- un OS
-- liste sans collecteur ne serait jamais mesure.
    ('load_average', 'Load average', 'System load average over the last 5 minutes, relative to the number of cores, as a percentage.',
     'system', 'system.load_average_percent', '%', 'numeric', 1, 'linux,darwin', 300, 300, 1, 'global'),

-- Sonde process_count
--
-- Compte les processus en cours d'execution sur la machine. Elle se regarde,
-- elle n'alerte pas : voir plus bas.
--
-- unit vaut 'count' et non NULL. C'est la convention de pending_updates et de
-- failed_logins plus haut : un decompte n'a pas de grandeur derriere lui, et
-- la console resout 'count' a vide (ReflexHelper::unitLabel). NULL
-- afficherait la meme chose, mais ne dirait pas que c'est un decompte.
    ('process_count', 'Process count', 'Number of processes running on the machine.',
     'system', 'system.process_count', 'count', 'numeric', 1, 'windows,linux,darwin', 300, 300, 1, 'global'),

-- Sonde cpu_temperature
--
-- Releve la temperature la plus elevee rapportee par les capteurs de la
-- machine. Le maximum et non une moyenne : c'est le point chaud qui fait
-- s'arreter un processeur, une moyenne le noierait.
--
-- Linux seulement : psutil.sensors_temperatures() n'existe ni sur macOS ni
-- sur Windows. Une seule ligne dans probe_collectors, et os_support le
-- reflete.
--
-- L'unite porte le signe degre. Le fichier est en UTF-8 -- il ecrit deja
-- Mémoire utilisée plus haut --, SET NAMES utf8mb4 l'annonce en tete et la
-- colonne est en utf8mb4 : le caractere traverse la chaine intact.
    ('cpu_temperature', 'Temperature', 'Highest temperature reported by the sensors of the machine.',
     'system', 'system.temperature_celsius', '°C', 'numeric', 1, 'linux', 300, 300, 1, 'global'),

-- Sonde local_admins
--
-- Compte les comptes membres du groupe d'administration locale de la
-- machine. Sa condition livree est un changement du decompte, sans seuil :
-- voir plus bas.
--
-- unit vaut 'count', comme process_count et pending_updates plus haut : un
-- decompte n'a pas de grandeur derriere lui, et la console resout 'count' a
-- vide (ReflexHelper::unitLabel).
--
-- Cadences plus lentes que les sondes systeme : la composition d'un groupe
-- d'administration ne change pas d'une minute a l'autre. min_interval a 300
-- secondes interdit de la relever plus souvent que toutes les cinq minutes,
-- defaut a 3600.
--
-- Seule sonde du catalogue a porter plottable = 0 : pour la meme raison, sa
-- courbe serait une ligne plate. La fiche machine affiche sa valeur et son
-- evolution, pas un graphique.
    ('local_admins', 'Local administrators', 'Number of accounts that are members of the local administration group of the machine.',
     'security', 'security.local_admins_count', 'count', 'numeric', 0, 'windows,linux,darwin', 300, 3600, 1, 'global'),

-- Sonde dns_resolution
--
-- La machine resout-elle le nom de son serveur Medulla. Booleenne : le
-- collecteur rend 1 ou 0, et unit reste NULL, comme antivirus_status,
-- firewall_status et disk_encryption plus haut. Un booleen n'a pas d'unite,
-- et la console l'affiche en oui/non.
--
-- Premiere sonde livree de categorie 'network'. La categorie existait deja --
-- la colonne la cite dans son commentaire et la console sait l'afficher --
-- mais aucune sonde ne la portait : rien a declarer en plus, category est un
-- varchar et non une enumeration.
    ('dns_resolution', 'Name resolution', 'Whether the machine can resolve the name of its Medulla server.',
     'network', 'network.dns_resolution_ok', NULL, 'boolean', 1, 'windows,linux,darwin', 300, 300, 1, 'global'),

-- L'axe Journaux du catalogue livre
--
-- Les cinq sondes qui suivent -- evenements systeme critiques, arrets
-- inattendus de service, redemarrages inattendus, erreurs materielles et
-- erreurs de systeme de fichiers -- sont baties sur le modele de
-- failed_logins, livree plus haut : la valeur n'est pas un etat instantane
-- mais un COMPTEUR D'OCCURRENCES sur une fenetre glissante. Trois
-- consequences, qui tiennent ensemble et ne se separent pas :
--
--   - la fenetre est portee par params_json du collecteur, et non par la
--     cadence de la sonde. Les deux sont independantes : une sonde relevee
--     toutes les 15 minutes sur une fenetre de 24 heures recompte le meme
--     intervalle glissant a chaque passage, c'est voulu ;
--   - elle est rappelee dans metric_key (_15m, _24h) et dans la description,
--     parce qu'un decompte sans periode derriere lui ne veut rien dire ;
--   - la condition porte une duree NULLE. Un evenement compte sur une fenetre
--     ne dure pas : exiger qu'il se maintienne n secondes n'aurait pas de
--     sens, la fenetre joue deja ce role. C'est exactement le reglage de la
--     condition de failed_logins.

-- Sonde critical_log_events
--
-- Compte les evenements de niveau critique enregistres dans le journal
-- systeme sur les 15 dernieres minutes. Elle ne dit pas ce qui s'est passe --
-- c'est le journal de la machine qui le dit -- elle dit qu'il s'est passe
-- quelque chose, et combien de fois.
--
-- Les trois systemes. Le journal ne porte pas le meme nom ni le meme format
-- partout, c'est le collecteur qui le sait ; la sonde, elle, mesure la meme
-- chose : un decompte d'evenements critiques.
--
-- unit vaut 'count', convention de failed_logins et de pending_updates : un
-- decompte n'a pas de grandeur derriere lui, et la console resout 'count' a
-- vide (ReflexHelper::unitLabel).
--
-- min_interval a 300 secondes : la lecture d'un journal sur une fenetre de 15
-- minutes est une operation couteuse, elle n'a pas a etre relancee toutes les
-- minutes. Defaut a 900, soit la fenetre elle-meme.
    ('critical_log_events', 'Critical system events', 'Number of critical events recorded in the system log over the last 15 minutes. The window is part of the measure: a threshold with no period behind it means nothing.',
     'system', 'system.critical_log_events_15m', 'count', 'numeric', 1, 'windows,linux,darwin', 300, 900, 1, 'global'),

-- Sonde service_crashes
--
-- Compte les services qui se sont arretes sans qu'on le leur demande sur les
-- 15 dernieres minutes.
--
-- Elle ne fait pas double emploi avec service_failed, livree plus haut :
-- service_failed donne l'ETAT courant, le nombre de services actuellement en
-- echec. Un service qui tombe et que le systeme relance aussitot n'y apparait
-- jamais, alors qu'il est exactement ce que cette sonde compte. L'une voit ce
-- qui est casse maintenant, l'autre ce qui a lache pendant la fenetre.
--
-- Pas de ligne darwin : launchd relance ses services et ne journalise pas
-- l'arret inattendu de facon exploitable. os_support le reflete -- un OS
-- liste sans collecteur ne serait jamais mesure.
    ('service_crashes', 'Unexpected service stops', 'Number of services that stopped unexpectedly over the last 15 minutes. Unlike the failed services probe, which reports the current state, this one counts services that went down during the window even when they were restarted right after.',
     'service', 'service.unexpected_stops_15m', 'count', 'numeric', 1, 'windows,linux', 300, 900, 1, 'global'),

-- Sonde unexpected_reboot
--
-- Compte les redemarrages non precedes d'un arret propre sur les 24 dernieres
-- heures : coupure de courant, plantage du noyau, arret brutal.
--
-- La fenetre est de 24 heures et non de 15 minutes. Un redemarrage inattendu
-- est rare et couteux a constater : une fenetre courte n'en verrait presque
-- jamais, et l'information resterait invisible entre deux releves. Sur 24
-- heures, le compteur raconte la journee de la machine.
--
-- Cadences plus lentes en consequence : min_interval a 900 secondes, defaut a
-- 3600. Relever toutes les minutes un decompte qui porte sur 24 heures
-- n'apporterait rien et relirait le journal de boot a chaque passage.
    ('unexpected_reboot', 'Unexpected reboots', 'Number of reboots over the last 24 hours that were not preceded by a clean shutdown: power loss, kernel panic or forced power off.',
     'system', 'system.unexpected_reboots_24h', 'count', 'numeric', 1, 'windows,linux', 900, 3600, 1, 'global'),

-- Sonde hardware_errors
--
-- Compte les erreurs materielles rapportees par le systeme sur les 24
-- dernieres heures : memoire, bus, processeur, peripheriques.
--
-- Categorie system et non storage : le materiel en cause n'est pas
-- necessairement un disque. Les erreurs de disque ont deja leur sonde,
-- disk_smart, livree plus haut.
--
-- Meme fenetre et memes cadences que unexpected_reboot, pour la meme raison :
-- l'evenement est rare, une fenetre courte ne le verrait pas.
    ('hardware_errors', 'Hardware errors', 'Number of hardware errors reported by the system over the last 24 hours: memory, bus, processor or device faults.',
     'system', 'system.hardware_errors_24h', 'count', 'numeric', 1, 'windows,linux', 900, 3600, 1, 'global'),

-- Sonde filesystem_errors
--
-- Compte les erreurs de systeme de fichiers rapportees par le systeme sur les
-- 24 dernieres heures : corruption, incoherence, remontage en lecture seule.
--
-- Categorie storage, celle de disk_usage et de disk_smart : ce qui est en
-- cause est le stockage. Elle ne fait pas double emploi avec disk_smart, qui
-- interroge l'etat du disque lui-meme : un systeme de fichiers peut se
-- corrompre sur un disque en parfaite sante.
    ('filesystem_errors', 'Filesystem errors', 'Number of filesystem errors reported by the system over the last 24 hours: corruption, inconsistency or a volume remounted read only.',
     'storage', 'storage.filesystem_errors_24h', 'count', 'numeric', 1, 'windows,linux', 900, 3600, 1, 'global'),

-- Sonde system_files_modified
--
-- Compte les fichiers appartenant a un paquet dont le contenu ne correspond
-- plus a ce que le paquet a installe. La reference est celle du gestionnaire
-- de paquets, qui conserve l'empreinte de chaque fichier livre : il n'y a
-- aucune base de reference a construire sur la machine, ni a tenir a jour, et
-- une mise a jour de paquet ne cree pas d'ecart puisqu'elle reinstalle le
-- fichier et son empreinte ensemble.
--
-- Linux seulement, et c'est une decision, pas une lacune a combler plus tard.
-- L'equivalent Windows, sfc /verifyonly, relit l'integralite des fichiers
-- proteges du disque et prend plusieurs minutes pendant lesquelles il occupe
-- la machine de l'utilisateur : ce prix est acceptable pour un diagnostic
-- ponctuel, il ne l'est pas pour une sonde qui repasse toute seule sur tout un
-- parc. macOS ne pose pas la question : depuis Big Sur ses fichiers systeme
-- vivent sur un volume scelle et monte en lecture seule.
--
-- Aucune ligne windows ni darwin dans probe_collectors, et os_support le
-- reflete -- un OS liste sans collecteur ne serait jamais mesure.
--
-- unit vaut 'count', convention de local_admins et de pending_updates : un
-- decompte n'a pas de grandeur derriere lui, et la console resout 'count' a
-- vide (ReflexHelper::unitLabel).
--
-- Cadences longues, et c'est une decision egalement. La commande lit et hache
-- chaque fichier installe par un paquet, soit des dizaines de milliers de
-- fichiers : elle coute du disque et du processeur pendant plusieurs minutes.
-- min_interval a 3600 secondes borne la liste des cadences que la console
-- propose, et c'est la le garde-fou : un exploitant ne peut pas poser cette
-- sonde a la minute, quelle que soit son envie de voir vite. Defaut a 86400,
-- une fois par jour -- un fichier systeme modifie le reste, le constater plus
-- souvent n'apprend rien de plus.
    ('system_files_modified', 'Modified system files', 'Number of files owned by a package whose content differs from what the package installed. The reference is the one kept by the package manager, so there is nothing to build and nothing to maintain on the machine.',
     'security', 'security.system_files_modified', 'count', 'numeric', 1, 'linux', 3600, 86400, 1, 'global')
ON DUPLICATE KEY UPDATE
    `label`                    = VALUES(`label`),
    `description`              = VALUES(`description`),
    `category`                 = VALUES(`category`),
    `metric_key`               = VALUES(`metric_key`),
    `unit`                     = VALUES(`unit`),
    `value_type`               = VALUES(`value_type`),
    `plottable`                = VALUES(`plottable`),
    `os_support`               = VALUES(`os_support`),
    `min_interval_seconds`     = VALUES(`min_interval_seconds`),
    `default_interval_seconds` = VALUES(`default_interval_seconds`),
    `is_builtin`               = VALUES(`is_builtin`),
    `visibility`               = VALUES(`visibility`);


-- ----------------------------------------------------------------------
-- Noms des sondes livrees, langue par langue
--
-- Place ici, contre le catalogue : ces libelles en sont la copie, et les deux
-- se relisent ensemble. Ce qui est ecrit a droite est le libelle EXACT que la
-- console affiche, caractere pour caractere, celui des catalogues gettext du
-- module web. Un libelle approche ne reserve rien : il ne sera jamais egal a
-- ce qu un utilisateur voit a l ecran et recopie.
--
-- L anglais n est pas saisi une seconde fois : il est deja dans probes.label,
-- il en est recopie. Deux ecritures du meme texte finissent par diverger, et
-- c est alors le nom anglais qui cesse d etre reserve.
--
-- ON DUPLICATE KEY UPDATE, comme le catalogue : une traduction corrigee dans
-- une livraison ulterieure descend chez les clients qui ont deja joue ce
-- schema. Rien ici n appartient a l exploitant, tout appartient au produit.
-- ----------------------------------------------------------------------
INSERT INTO `probe_shipped_labels` (`probe_key`, `language`, `label`)
SELECT `probe_key`, 'en', `label` FROM `probes` WHERE `is_builtin` = 1
ON DUPLICATE KEY UPDATE `label` = VALUES(`label`);

INSERT INTO `probe_shipped_labels` (`probe_key`, `language`, `label`) VALUES
    ('cpu_load',                 'fr_FR', 'Charge processeur'),
    ('memory_usage',             'fr_FR', 'Mémoire utilisée'),
    ('swap_usage',               'fr_FR', 'Swap utilisé'),
    ('disk_usage',               'fr_FR', 'Espace disque'),
    ('disk_smart',               'fr_FR', 'État SMART du disque'),
    ('service_failed',           'fr_FR', 'Services en échec'),
    ('antivirus_status',         'fr_FR', 'Antivirus actif'),
    ('antivirus_signatures_age', 'fr_FR', 'Ancienneté des signatures antivirus'),
    ('firewall_status',          'fr_FR', 'Pare-feu actif'),
    ('disk_encryption',          'fr_FR', 'Chiffrement du disque'),
    ('failed_logins',            'fr_FR', 'Connexions en échec'),
    ('pending_updates',          'fr_FR', 'Mises à jour en attente'),
    ('reboot_required',          'fr_FR', 'Redémarrage requis'),
    ('load_average',             'fr_FR', 'Charge moyenne'),
    ('process_count',            'fr_FR', 'Nombre de processus'),
    ('cpu_temperature',          'fr_FR', 'Température'),
    ('local_admins',             'fr_FR', 'Administrateurs locaux'),
    ('dns_resolution',           'fr_FR', 'Résolution de noms'),
    ('critical_log_events',      'fr_FR', 'Événements système critiques'),
    ('service_crashes',          'fr_FR', 'Arrêts de service inattendus'),
    ('unexpected_reboot',        'fr_FR', 'Redémarrages inattendus'),
    ('hardware_errors',          'fr_FR', 'Erreurs matérielles'),
    ('filesystem_errors',        'fr_FR', 'Erreurs de système de fichiers'),
    ('system_files_modified',    'fr_FR', 'Fichiers système modifiés'),

    ('cpu_load',                 'es_ES', 'Carga de CPU'),
    ('memory_usage',             'es_ES', 'Memoria utilizada'),
    ('swap_usage',               'es_ES', 'Swap utilizado'),
    ('disk_usage',               'es_ES', 'Espacio en disco'),
    ('disk_smart',               'es_ES', 'Estado SMART del disco'),
    ('service_failed',           'es_ES', 'Servicios en fallo'),
    ('antivirus_status',         'es_ES', 'Antivirus activo'),
    ('antivirus_signatures_age', 'es_ES', 'Antigüedad de las firmas del antivirus'),
    ('firewall_status',          'es_ES', 'Cortafuegos activo'),
    ('disk_encryption',          'es_ES', 'Cifrado del disco'),
    ('failed_logins',            'es_ES', 'Inicios de sesión fallidos'),
    ('pending_updates',          'es_ES', 'Actualizaciones pendientes'),
    ('reboot_required',          'es_ES', 'Reinicio necesario'),
    ('load_average',             'es_ES', 'Carga media'),
    ('process_count',            'es_ES', 'Número de procesos'),
    ('cpu_temperature',          'es_ES', 'Temperatura'),
    ('local_admins',             'es_ES', 'Administradores locales'),
    ('dns_resolution',           'es_ES', 'Resolución de nombres'),
    ('critical_log_events',      'es_ES', 'Eventos críticos del sistema'),
    ('service_crashes',          'es_ES', 'Paradas inesperadas de servicios'),
    ('unexpected_reboot',        'es_ES', 'Reinicios inesperados'),
    ('hardware_errors',          'es_ES', 'Errores de hardware'),
    ('filesystem_errors',        'es_ES', 'Errores del sistema de archivos'),
    ('system_files_modified',    'es_ES', 'Archivos del sistema modificados')
ON DUPLICATE KEY UPDATE
    `label` = VALUES(`label`);


-- ----------------------------------------------------------------------
-- Conditions livrees avec les sondes du catalogue
--
-- Seules les colonnes default_* sont alimentees : les surcharges restent
-- NULL, donc chaque condition suit le produit tant que l exploitant n a rien
-- regle.
--
-- ON DUPLICATE KEY UPDATE, comme pour la table settings, et pour la meme
-- raison : un INSERT IGNORE serait rejouable mais inerte. Une livraison
-- ulterieure qui corrigerait un seuil livre serait purement ignoree chez tout
-- client ayant deja joue ce schema, et la correction ne descendrait jamais.
-- Ici elle descend, et elle ne touche que la definition produit : operator et
-- les sept colonnes default_*. Les surcharges, customized_by et customized_at
-- ne sont jamais reecrites, c'est ce qui protege le reglage du client.
--
-- INVARIANT A NE PAS CASSER : c'est uk_probe_order (probe_id, display_order)
-- qui fait qu une condition se reconnait d une livraison a l autre. Changer
-- le display_order d une condition livree la rend meconnaissable : la
-- correction s inserera comme une condition neuve a cote de l ancienne, et le
-- client se retrouvera avec les deux. Un display_order attribue est definitif.
-- Les valeurs sont ecrites en entier, NULL compris, pour que ce que le
-- produit livre soit lisible ligne a ligne et qu une valeur retiree d une
-- livraison a l autre soit reellement effacee.
--
-- Gabarits de message. Quatre variables : @@machine@@, @@value@@,
-- @@threshold@@ et @@instance@@. @@instance@@ nomme la mesure quand une sonde
-- en remonte plusieurs par machine : c'est le cas de disk_usage, seule sonde
-- livree dont les collecteurs declarent leur demultiplication par une clef
-- per_ dans params_json (per_mountpoint sur les trois OS). Sans elle, Disk
-- space at 44 % on ath-w10-1 ne dit pas quel volume est plein. Elle est
-- placee avant la valeur et sans mot de liaison : sur une sonde qui ne remonte
-- qu une mesure elle se resout a vide, et la phrase n y perd qu une espace, la
-- ou entre parentheses ou derriere un of elle laisserait un fragment vide.
--
-- L espace devant le signe pourcent est une espace ORDINAIRE, pas une
-- insecable. Ce texte sort par courriel et par les autres canaux de
-- notification : une insecable mal transcodee s affiche en Â devant le signe,
-- et dans ce fichier elle serait un caractere invisible qu un diff ne montre
-- pas et qu un editeur peut normaliser sans prevenir. Le gain typographique ne
-- vaut pas ce risque.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       90, NULL, NULL,
       600, 'high', 'CPU load at @@value@@ % on @@machine@@ (threshold @@threshold@@ %)',
       1, 10
    FROM `probes` WHERE `probe_key` = 'cpu_load'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       90, NULL, NULL,
       600, 'high', 'Memory used at @@value@@ % on @@machine@@ (threshold @@threshold@@ %)',
       1, 10
    FROM `probes` WHERE `probe_key` = 'memory_usage'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       80, NULL, NULL,
       900, 'medium', 'Swap used at @@value@@ % on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'swap_usage'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       85, NULL, NULL,
       0, 'medium', 'Disk space @@instance@@ at @@value@@ % on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'disk_usage'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       95, NULL, NULL,
       0, 'critical', 'Disk space critical @@instance@@ at @@value@@ % on @@machine@@',
       1, 20
    FROM `probes` WHERE `probe_key` = 'disk_usage'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'ne',
       NULL, NULL, 'OK',
       0, 'critical', 'SMART status degraded on @@machine@@: @@value@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'disk_smart'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       0, NULL, NULL,
       300, 'high', '@@value@@ failed service(s) on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'service_failed'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'eq',
       0, NULL, NULL,
       0, 'critical', 'No antivirus running on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'antivirus_status'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       7, NULL, NULL,
       0, 'high', 'Antivirus signatures @@value@@ days old on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'antivirus_signatures_age'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'eq',
       0, NULL, NULL,
       0, 'high', 'Firewall disabled on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'firewall_status'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'eq',
       0, NULL, NULL,
       0, 'medium', 'System volume not encrypted on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'disk_encryption'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       10, NULL, NULL,
       0, 'medium', '@@value@@ failed logons on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'failed_logins'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'eq',
       1, NULL, NULL,
       0, 'info', 'Reboot required on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'reboot_required'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);


-- ----------------------------------------------------------------------
-- Condition livree : load_average
--
-- Seuil a 150 % : au-dela, il y a durablement plus de taches pretes que de
-- coeurs pour les prendre. Exigee en continu pendant 600 secondes, comme sur
-- cpu_load : une charge moyenne sur 5 minutes monte deja lentement, une pointe
-- de compilation ou de sauvegarde ne doit pas lever d'alerte.
--
-- display_order 10, premiere condition de cette sonde. Un display_order
-- attribue est definitif : c'est lui qui fait reconnaitre la condition d'une
-- livraison a l'autre.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       150, NULL, NULL,
       600, 'high', 'Load average at @@value@@ % on @@machine@@ (threshold @@threshold@@ %)',
       1, 10
    FROM `probes` WHERE `probe_key` = 'load_average'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Aucune condition livree : process_count
--
-- Volontaire, et c'est deja le cas de pending_updates : un nombre de
-- processus ne dit rien hors contexte. Trois cents processus sont
-- normaux sur un poste Windows et anormaux sur un serveur. Un seuil livre
-- serait faux partout ; chaque entite posera le sien si elle en veut un.
--
-- Rien a ecrire dans probe_conditions, donc : l'absence de bloc est ce qui
-- livre la sonde sans alerte.
-- ----------------------------------------------------------------------

-- ----------------------------------------------------------------------
-- Condition livree : cpu_temperature
--
-- Seuil a 85 degres, tenu 300 secondes. Un pic de quelques secondes est le
-- fonctionnement normal d'un processeur qui accelere ; cinq minutes au-dessus
-- de 85 sont un defaut de refroidissement.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       85, NULL, NULL,
       300, 'high', 'Temperature at @@value@@ °C on @@machine@@ (threshold @@threshold@@ °C)',
       1, 10
    FROM `probes` WHERE `probe_key` = 'cpu_temperature'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : local_admins
--
-- Aucun seuil, et ce n'est pas un oubli. Le nombre normal d'administrateurs
-- locaux depend de l'organisation du client : deux sur un poste tenu par une
-- DSI, une dizaine sur un parc ou les utilisateurs sont administrateurs de
-- leur machine. Un seuil livre serait faux quelque part.
--
-- L'operateur changed repond a la question posee par la specification, un
-- compte administrateur ajoute, sans rien a regler par entite : il compare la
-- mesure a la precedente et ne lit aucun seuil. C'est l'evolution du decompte
-- qui se regarde, pas sa valeur absolue. Les trois colonnes de seuil restent
-- NULL, le serveur refuse un seuil sur cet operateur.
--
-- Il signale aussi le retrait d'un administrateur, qui est notable egalement.
-- Sa limite : un remplacement a effectif constant entre deux mesures passe
-- inapercu, le decompte ne bouge pas.
--
-- Duree nulle, la seule qui ait un sens : exiger qu'une valeur ait change en
-- continu pendant N secondes ne veut rien dire.
--
-- La pose de la sonde ne leve rien : sans mesure precedente, la condition est
-- fausse. Sans cela, poser la sonde alerterait tout le parc d'un coup.
--
-- Gravite elevee et non critique : un administrateur de plus est a regarder
-- le jour meme, la machine continue de fonctionner.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'changed',
       NULL, NULL, NULL,
       0, 'high', 'Local administrators changed on @@machine@@ (now @@value@@)',
       1, 10
    FROM `probes` WHERE `probe_key` = 'local_admins'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : dns_resolution
--
-- Meme forme que celle d'antivirus_status plus haut : comparaison eq a
-- 0, c'est-a-dire la valeur booleenne non. Un booleen se compare a 0 et non a
-- une chaine : la condition reste numerique, default_threshold_text reste
-- NULL.
--
-- Tenue 300 secondes, et non levee au premier echec : un resolveur qui ne
-- repond pas pendant quelques secondes est frequent et sans consequence. Cinq
-- minutes sans resolution, en revanche, coupent la machine de son serveur.
--
-- Gravite elevee et non critique : la machine fonctionne toujours, c'est son
-- rattachement qui est en cause.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'eq',
       0, NULL, NULL,
       300, 'high', 'Name resolution failing on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'dns_resolution'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : critical_log_events
--
-- Seuil a 0, comparaison gt : un seul evenement critique dans la fenetre
-- suffit a alerter. Un evenement critique n'a pas de niveau normal, a la
-- difference d'une authentification en echec dont failed_logins tolere une
-- dizaine.
--
-- Duree NULLE, comme failed_logins. La fenetre de 15 minutes du collecteur
-- porte deja la temporalite de la mesure : demander en plus que le compteur
-- se maintienne n secondes n'ajouterait rien et retarderait l'alerte.
--
-- Gravite medium : un evenement critique merite d'etre vu, il ne dit pas a
-- lui seul que la machine est hors service.
--
-- display_order 10, premiere condition de cette sonde. Un display_order
-- attribue est definitif : c'est lui qui fait reconnaitre la condition d'une
-- livraison a l'autre.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       0, NULL, NULL,
       0, 'medium', '@@value@@ critical system events on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'critical_log_events'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : service_crashes
--
-- Seuil a 0, duree nulle, meme raisonnement que ci-dessus : un service qui
-- s'arrete seul est deja l'anomalie, et la fenetre de 15 minutes porte la
-- temporalite.
--
-- Gravite medium : le service peut avoir ete relance par le systeme. C'est la
-- repetition qui compte, et elle se lit sur la courbe.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       0, NULL, NULL,
       0, 'medium', '@@value@@ services stopped unexpectedly on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'service_crashes'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : unexpected_reboot
--
-- Seuil a 0, duree nulle : la fenetre de 24 heures porte la temporalite.
--
-- Gravite high et non critical : la machine a redemarre, donc elle repond --
-- c'est bien elle qui remonte la mesure. Le probleme est reel, il n'est pas
-- en cours.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       0, NULL, NULL,
       0, 'high', '@@value@@ unexpected reboots on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'unexpected_reboot'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : hardware_errors
--
-- Seuil a 0, duree nulle. Gravite high : une erreur materielle ne se corrige
-- pas toute seule et annonce souvent une panne.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       0, NULL, NULL,
       0, 'high', '@@value@@ hardware errors on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'hardware_errors'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : filesystem_errors
--
-- Seuil a 0, duree nulle. Gravite high : une erreur de systeme de fichiers
-- met en jeu les donnees de la machine, et un volume remonte en lecture seule
-- arrete ce qui ecrivait dessus.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       0, NULL, NULL,
       0, 'high', '@@value@@ filesystem errors on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'filesystem_errors'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Condition livree : system_files_modified
--
-- Seuil a 0, comparaison gt : un seul fichier qui ne correspond plus a son
-- paquet est deja l'anomalie. Il n'y a pas de niveau normal a tolerer ici, a
-- la difference d'une authentification en echec.
--
-- Duree nulle : l'ecart n'est pas un etat passager qu'il faudrait voir se
-- maintenir, il dure jusqu'a ce que quelqu'un le corrige. Exiger en plus une
-- duree n'aurait aucun sens sur une sonde relevee une fois par jour.
--
-- Gravite high : un fichier livre par un paquet qui ne correspond plus a ce
-- que le paquet a pose est soit une intervention manuelle non tracee, soit une
-- compromission. Ni l'un ni l'autre n'attend. Pas critical pour autant : la
-- machine fonctionne, rien n'est interrompu.
--
-- display_order 10, premiere condition de cette sonde, et definitif.
-- ----------------------------------------------------------------------
INSERT INTO `probe_conditions`
    (`probe_id`, `operator`,
     `default_threshold_value`, `default_threshold_value2`, `default_threshold_text`,
     `default_duration_seconds`, `default_severity`, `default_message_template`,
     `default_enabled`, `display_order`)
SELECT `id`, 'gt',
       0, NULL, NULL,
       0, 'high', '@@value@@ modified system files on @@machine@@',
       1, 10
    FROM `probes` WHERE `probe_key` = 'system_files_modified'
ON DUPLICATE KEY UPDATE
    `operator`                 = VALUES(`operator`),
    `default_threshold_value`  = VALUES(`default_threshold_value`),
    `default_threshold_value2` = VALUES(`default_threshold_value2`),
    `default_threshold_text`   = VALUES(`default_threshold_text`),
    `default_duration_seconds` = VALUES(`default_duration_seconds`),
    `default_severity`         = VALUES(`default_severity`),
    `default_message_template` = VALUES(`default_message_template`),
    `default_enabled`          = VALUES(`default_enabled`);

-- ----------------------------------------------------------------------
-- Methodes de collecte des sondes livrees, par systeme d exploitation
--
-- Les absences sont significatives : pas de ligne antivirus pour macOS car
-- le systeme n expose pas d API standard equivalente au Security Center de
-- Windows ; pas de ligne reboot_required pour macOS pour la meme raison.
--
-- ON DUPLICATE KEY UPDATE sur uk_probe_os : le collecteur, ses parametres, sa
-- note documentaire et sa dependance sont des decisions produit, corrigeables
-- par une livraison ulterieure. `enabled` en est exclu, comme dans probes :
-- c'est le seul champ de cette table qu un exploitant peut avoir touche.
--
-- La ligne se reconnait par (probe_id, os). Changer le collecteur d une
-- sonde pour un OS met donc bien a jour la ligne existante ; retirer un OS
-- d une sonde, en revanche, ne supprime rien : la ligne devenue caduque
-- demande un DELETE explicite dans le schema qui la retire.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'cpu.percent', NULL, 'psutil.cpu_percent(interval=1) - average over every logical core', NULL FROM `probes` WHERE `probe_key` = 'cpu_load'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'cpu.percent', NULL, 'psutil.cpu_percent(interval=1) - average over every logical core', NULL FROM `probes` WHERE `probe_key` = 'cpu_load'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'cpu.percent', NULL, 'psutil.cpu_percent(interval=1) - average over every logical core', NULL FROM `probes` WHERE `probe_key` = 'cpu_load'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'mem.virtual', NULL, 'psutil.virtual_memory().percent', NULL FROM `probes` WHERE `probe_key` = 'memory_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'mem.virtual', NULL, 'psutil.virtual_memory() - computed on available, NOT on total minus free: the disk cache must not be counted as used', NULL FROM `probes` WHERE `probe_key` = 'memory_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'mem.virtual', NULL, 'psutil.virtual_memory() - computed on available', NULL FROM `probes` WHERE `probe_key` = 'memory_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'mem.swap', NULL, 'psutil.swap_memory().percent - the Windows page file grows on demand, read with care', NULL FROM `probes` WHERE `probe_key` = 'swap_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'mem.swap', NULL, 'psutil.swap_memory().percent', NULL FROM `probes` WHERE `probe_key` = 'swap_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'mem.swap', NULL, 'psutil.swap_memory().percent', NULL FROM `probes` WHERE `probe_key` = 'swap_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'disk.usage', '{"per_mountpoint": true}', 'psutil.disk_partitions() then psutil.disk_usage() per volume, removable and network drives left out', NULL FROM `probes` WHERE `probe_key` = 'disk_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'disk.usage', '{"per_mountpoint": true, "exclude_fstypes": ["tmpfs","devtmpfs","squashfs","overlay"]}', 'psutil.disk_partitions() then psutil.disk_usage() per mount point', NULL FROM `probes` WHERE `probe_key` = 'disk_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'disk.usage', '{"per_mountpoint": true}', 'psutil.disk_partitions() then psutil.disk_usage() per mount point', NULL FROM `probes` WHERE `probe_key` = 'disk_usage'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'disk.smart_wmi', NULL, 'WMI MSStorageDriver_FailurePredictStatus, or Get-PhysicalDisk for HealthStatus. Value normalised to OK / WARNING / FAILING / UNKNOWN', NULL FROM `probes` WHERE `probe_key` = 'disk_smart'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'disk.smart_smartctl', NULL, 'smartctl -H on every physical disk. Value normalised to OK / WARNING / FAILING / UNKNOWN', 'smartmontools' FROM `probes` WHERE `probe_key` = 'disk_smart'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'disk.smart_diskutil', NULL, 'diskutil info -all, SMART Status field. Value normalised to OK / WARNING / FAILING / UNKNOWN', NULL FROM `probes` WHERE `probe_key` = 'disk_smart'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'service.win_auto_stopped', NULL, 'Services set to start automatically whose state is not Running, through psutil.win_service_iter or Get-Service', NULL FROM `probes` WHERE `probe_key` = 'service_failed'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'service.systemd_failed', NULL, 'systemctl --failed --no-legend --plain: number of failed units', NULL FROM `probes` WHERE `probe_key` = 'service_failed'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'service.launchd_failed', NULL, 'launchctl list: services whose exit code is not zero', NULL FROM `probes` WHERE `probe_key` = 'service_failed'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'security.win_securitycenter', NULL, 'WMI root/SecurityCenter2 class AntiVirusProduct: at least one product with an active productState', NULL FROM `probes` WHERE `probe_key` = 'antivirus_status'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'security.clamav_status', NULL, 'systemctl is-active clamav-daemon or clamd', 'clamav' FROM `probes` WHERE `probe_key` = 'antivirus_status'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'security.win_defender_sig_age', NULL, 'Get-MpComputerStatus, AntivirusSignatureAge field, in days. The measure is unavailable when a third party antivirus is running', NULL FROM `probes` WHERE `probe_key` = 'antivirus_signatures_age'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'security.clamav_sig_age', NULL, 'Age of the most recent .cvd or .cld file in /var/lib/clamav', 'clamav-freshclam' FROM `probes` WHERE `probe_key` = 'antivirus_signatures_age'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'security.win_firewall', NULL, 'Get-NetFirewallProfile: the active profile must be Enabled', NULL FROM `probes` WHERE `probe_key` = 'firewall_status'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'security.linux_firewall', NULL, 'ufw status, or firewall-cmd --state, or the presence of nft or iptables rules, depending on the distribution', NULL FROM `probes` WHERE `probe_key` = 'firewall_status'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'security.macos_firewall', NULL, '/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate', NULL FROM `probes` WHERE `probe_key` = 'firewall_status'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'security.bitlocker', NULL, 'Get-BitLockerVolume on the system volume: ProtectionStatus and VolumeStatus', NULL FROM `probes` WHERE `probe_key` = 'disk_encryption'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'security.luks', NULL, 'lsblk -o NAME,TYPE,FSTYPE: a crypto_LUKS container on the root filesystem', NULL FROM `probes` WHERE `probe_key` = 'disk_encryption'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'security.filevault', NULL, 'fdesetup status', NULL FROM `probes` WHERE `probe_key` = 'disk_encryption'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'security.win_eventlog_4625', '{"window_minutes": 15}', 'Get-WinEvent on the Security log, EventID 4625, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'failed_logins'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'security.linux_authlog', '{"window_minutes": 15}', 'journalctl _SYSTEMD_UNIT=sshd and sudo, or /var/log/auth.log and /var/log/secure: failures over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'failed_logins'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'security.macos_unified_log', '{"window_minutes": 15}', 'log show --predicate on authentication failures, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'failed_logins'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'update.win_session', NULL, 'COM Microsoft.Update.Session, search for IsInstalled=0', NULL FROM `probes` WHERE `probe_key` = 'pending_updates'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'update.apt_dnf', NULL, 'apt-get -s upgrade, or dnf check-update, depending on the package manager', NULL FROM `probes` WHERE `probe_key` = 'pending_updates'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'update.softwareupdate', NULL, 'softwareupdate -l', NULL FROM `probes` WHERE `probe_key` = 'pending_updates'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'system.win_reboot_pending', NULL, 'Registry keys RebootPending of Component Based Servicing and RebootRequired of WindowsUpdate Auto Update', NULL FROM `probes` WHERE `probe_key` = 'reboot_required'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'system.linux_reboot_required', NULL, '/var/run/reboot-required, or needs-restarting -r on RPM distributions', NULL FROM `probes` WHERE `probe_key` = 'reboot_required'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);


-- ----------------------------------------------------------------------
-- Methode de collecte de load_average, par systeme d'exploitation
--
-- Pas de ligne windows : l'absence est significative, le systeme n'expose pas
-- de charge moyenne.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'system.load_average', NULL, 'os.getloadavg()[1] - the 5 minute load average, divided by the logical core count and expressed as a percentage', NULL FROM `probes` WHERE `probe_key` = 'load_average'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'system.load_average', NULL, 'os.getloadavg()[1] - the 5 minute load average, divided by the logical core count and expressed as a percentage', NULL FROM `probes` WHERE `probe_key` = 'load_average'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de process_count, par systeme d'exploitation
--
-- Les trois systemes, meme collecteur : l'enumeration des processus est
-- portable.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'system.process_count', NULL, 'len(psutil.pids()) - the number of processes running on the machine', NULL FROM `probes` WHERE `probe_key` = 'process_count'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'system.process_count', NULL, 'len(psutil.pids()) - the number of processes running on the machine', NULL FROM `probes` WHERE `probe_key` = 'process_count'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'system.process_count', NULL, 'len(psutil.pids()) - the number of processes running on the machine', NULL FROM `probes` WHERE `probe_key` = 'process_count'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de cpu_temperature, par systeme d'exploitation
--
-- Une seule ligne, linux. Pas de dependance a declarer dans requires :
-- psutil lit directement /sys/class/hwmon, lm-sensors n'est pas requis.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'system.temperature', NULL, 'psutil.sensors_temperatures() - the highest current reading across every sensor, in degrees Celsius', NULL FROM `probes` WHERE `probe_key` = 'cpu_temperature'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de local_admins, par systeme d'exploitation
--
-- Les trois systemes, meme collecteur. Le groupe d'administration n'y porte
-- pas le meme nom, c'est le collecteur qui le sait ; la sonde, elle, mesure
-- la meme chose partout.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'security.local_admins', NULL, 'Members of the local Administrators group, resolved by its well known SID S-1-5-32-544 rather than by name, which is localised', NULL FROM `probes` WHERE `probe_key` = 'local_admins'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'security.local_admins', NULL, 'Members of the sudo and wheel groups in /etc/group, plus every account with uid 0 in /etc/passwd, counted once each', NULL FROM `probes` WHERE `probe_key` = 'local_admins'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'security.local_admins', NULL, 'dscl . -read /Groups/admin GroupMembership: the members of the admin group', NULL FROM `probes` WHERE `probe_key` = 'local_admins'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de dns_resolution, par systeme d'exploitation
--
-- Les trois systemes, meme collecteur : la resolution de nom passe par le
-- resolveur du systeme, l'appel est le meme partout.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'network.dns_resolution', NULL, 'socket.getaddrinfo() on the Medulla server name read from the agent configuration: 1 when the name resolves, 0 when it does not', NULL FROM `probes` WHERE `probe_key` = 'dns_resolution'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'network.dns_resolution', NULL, 'socket.getaddrinfo() on the Medulla server name read from the agent configuration: 1 when the name resolves, 0 when it does not', NULL FROM `probes` WHERE `probe_key` = 'dns_resolution'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'network.dns_resolution', NULL, 'socket.getaddrinfo() on the Medulla server name read from the agent configuration: 1 when the name resolves, 0 when it does not', NULL FROM `probes` WHERE `probe_key` = 'dns_resolution'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de critical_log_events, par systeme d'exploitation
--
-- Les trois systemes, meme cle de collecteur. params_json porte la fenetre,
-- en minutes, comme les collecteurs de failed_logins : c'est la que se regle
-- la periode comptee, et elle doit rester coherente avec le
-- _15m de metric_key et avec la description.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'system.critical_log_events', '{"window_minutes": 15}', 'Get-WinEvent on the System log, Level 1 (Critical), over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'critical_log_events'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'system.critical_log_events', '{"window_minutes": 15}', 'journalctl -p crit over the sliding window. Without journalctl the probe reports unavailable: the syslog files do not record the priority of a line, and counting the lines that look severe would answer another question under the same name', NULL FROM `probes` WHERE `probe_key` = 'critical_log_events'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'darwin', 'system.critical_log_events', '{"window_minutes": 15}', 'log show --predicate on messageType fault over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'critical_log_events'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de service_crashes, par systeme d'exploitation
--
-- Pas de ligne darwin : l'absence est significative, voir la sonde plus haut.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'service.unexpected_stops', '{"window_minutes": 15}', 'Get-WinEvent on the System log, Service Control Manager EventID 7031 and 7034, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'service_crashes'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'service.unexpected_stops', '{"window_minutes": 15}', 'journalctl entries from systemd reporting a unit entering the failed state or exiting with a non zero result, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'service_crashes'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de unexpected_reboot, par systeme d'exploitation
--
-- params_json porte 1440 minutes, soit les 24 heures annoncees par metric_key
-- et par la description. Pas de ligne darwin.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'system.unexpected_reboots', '{"window_minutes": 1440}', 'Get-WinEvent on the System log, EventID 6008 (unexpected shutdown), over the sliding window. Kernel-Power 41 is deliberately left out: it describes the same reboot and would double the count', NULL FROM `probes` WHERE `probe_key` = 'unexpected_reboot'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'system.unexpected_reboots', '{"window_minutes": 1440}', 'journalctl --list-boots: boots started within the sliding window whose previous boot carries no clean shutdown record', NULL FROM `probes` WHERE `probe_key` = 'unexpected_reboot'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de hardware_errors, par systeme d'exploitation
--

-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'system.hardware_errors', '{"window_minutes": 1440}', 'Get-WinEvent on the System log, WHEA-Logger error events, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'hardware_errors'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'system.hardware_errors', '{"window_minutes": 1440}', 'journalctl -k: machine check exception, hardware error and EDAC kernel messages, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'hardware_errors'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de filesystem_errors, par systeme d'exploitation
--

-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'windows', 'storage.filesystem_errors', '{"window_minutes": 1440}', 'Get-WinEvent on the System log, Ntfs and Disk source error events, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'filesystem_errors'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'storage.filesystem_errors', '{"window_minutes": 1440}', 'journalctl -k: EXT4-fs error, XFS metadata I/O error and read only remount kernel messages, over the sliding window', NULL FROM `probes` WHERE `probe_key` = 'filesystem_errors'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);

-- ----------------------------------------------------------------------
-- Methode de collecte de system_files_modified, par systeme d'exploitation
--
-- Une seule ligne, linux : l'absence des deux autres est significative, voir
-- la sonde plus haut.
--
-- params_json a NULL, a la difference des sondes de l'axe Journaux : celle-ci
-- ne compte pas les occurrences d'un evenement sur une fenetre glissante, elle
-- constate un ecart present. Il n'y a donc pas de periode a passer au
-- collecteur.
--
-- La cle security.system_files_modified est le contrat avec le collecteur
-- ecrit cote agent : elle ne change plus ensuite.
--
-- Rien a declarer dans requires : l'outil de verification est celui du
-- gestionnaire de paquets du systeme, present partout ou il y a des paquets.
-- ----------------------------------------------------------------------
INSERT INTO `probe_collectors` (`probe_id`,`os`,`collector`,`params_json`,`implementation_note`,`requires`)
SELECT `id`, 'linux', 'security.system_files_modified', NULL, 'dpkg --verify on Debian based systems, rpm -Va on RPM based ones: the number of installed files whose content no longer matches the digest the package manager recorded when the package was installed', NULL FROM `probes` WHERE `probe_key` = 'system_files_modified'
ON DUPLICATE KEY UPDATE `collector` = VALUES(`collector`), `params_json` = VALUES(`params_json`), `implementation_note` = VALUES(`implementation_note`), `requires` = VALUES(`requires`);


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- La table n'a pas de contrainte d'unicite : un INSERT IGNORE n'ignore donc
-- rien et duplique la ligne a chaque rejeu du script. L'insertion n'a lieu
-- que si la table est vide.
INSERT INTO `version` (`Number`)
SELECT 1 FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM `version`);

COMMIT;
