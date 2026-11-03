-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-112.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Ajout du statut de deploiement Windows release majeure lorsque le paquet
-- de mise a jour a ete depose, qu'un utilisateur soit connecte ou non.
-- Dans les deux cas Medulla a termine la phase de deploiement; l'application
-- effective de la release Windows reste attendue au prochain redemarrage et
-- sera confirmee par le prochain inventaire.
--
-- Voir pulse_xmpp_agent/bin/process-deploiement-release-windows.md pour le
-- detail du process fonctionnel (messages emis par l'etape action_comment
-- "release_user_context" du workflow xmppdeploy.json).

START TRANSACTION;

USE `xmppmaster`;

INSERT IGNORE INTO `def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES
('.*Windows release update: connected user=.*; target release=.*', 'RELEASE_UPDATE_PENDING_REBOOT', 'releaseupdatependingreboot'),
('.*Windows release update: no connected user; target release=.*', 'RELEASE_UPDATE_PENDING_REBOOT', 'releaseupdatependingreboot');

UPDATE version SET Number = 112;

COMMIT;
