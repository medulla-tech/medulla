-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
--
-- FILE contrib/xmppmaster/sql/schema-111.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
--
-- Corrige l'index unique malforme `index_uniq_entity_uuid` sur
-- `up_machine_windows`.
--
-- Contexte
--   `up_machine_windows` est une table PAR MACHINE : sa cle primaire est
--   (id_machine, update_id). L'index ajoute par schema-095 :
--       UNIQUE INDEX index_uniq_entity_uuid (update_id, entityid)
--   ne contient pas id_machine. Il impose donc qu'une seule machine du
--   parc puisse porter un update donne pour une entite donnee : la 2e
--   machine tombe en "Duplicate entry '<update_id>-<entityid>'", l'INSERT
--   echoue (IntegrityError attrapee puis ignoree cote agent dans
--   setUp_machine_windows), et la machine n'est jamais marquee
--   "update requis". Resultat : l'auto-approbation ne couvre en pratique
--   qu'une poignee de machines par entite.
--
-- Correctif
--   - suppression de l'index unique fautif ;
--   - ajout d'un index NON unique (update_id, entityid) pour les
--     recherches / jointures (move_update_to_white_list, selection de
--     deploiement).
--   L'unicite par machine reste garantie par la cle primaire
--   (id_machine, update_id) et par l'index unique index_uniq_kb
--   (id_machine, kb).
--

start transaction;

use xmppmaster;

ALTER TABLE `xmppmaster`.`up_machine_windows`
  DROP INDEX IF EXISTS `index_uniq_entity_uuid`;

ALTER TABLE `xmppmaster`.`up_machine_windows`
  ADD INDEX IF NOT EXISTS `idx_update_entity` (`update_id`, `entityid`);


UPDATE version SET Number = 111;


commit;
