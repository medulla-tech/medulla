-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-114.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Ajout des statuts metier emis par les notifications du workflow de mise a
-- niveau majeure Windows. Les motifs ciblent les prefixes canoniques des
-- messages apres substitution des templates du descripteur de package.
--
-- Regle metier:
--   Une annulation explicite par l'utilisateur ne doit pas etre confondue
--   avec une erreur technique d'execution du package. Une absence de reponse
--   utilisateur est un statut distinct.
--
-- Messages canoniques a utiliser dans les action_notification du package:
--   Windows release update aborted by user @@@CONNECTED_USER@@@
--     -> ABORT PACKAGE EXECUTION BY USER
--   Windows release update aborted: user response timed out @@@CONNECTED_USER@@@
--     -> ABORT PACKAGE EXECUTION ON USER TIMEOUT
--   Windows release update execution confirmed: ISO control started
--     -> DEPLOYEMENT RELEASE CONTROLE TOTAL ISO WINDOWS
--
-- Les templates sont resolus par l'agent avant la journalisation et le
-- rapprochement avec les expressions regulieres ci-dessous.

START TRANSACTION;

USE `xmppmaster`;

INSERT IGNORE INTO `def_remote_deploy_status` (`regex_logmessage`, `status`, `label`) VALUES
('.*Windows release update aborted by user .*', 'ABORT PACKAGE EXECUTION BY USER', 'abortpackageexecutionbyuser'),
('.*Windows release update aborted: user response timed out .*', 'ABORT PACKAGE EXECUTION ON USER TIMEOUT', 'abortpackageexecutiononusertimeout'),
('.*Windows release update execution confirmed: ISO control started.*', 'DEPLOYEMENT RELEASE CONTROLE TOTAL ISO WINDOWS', 'deploymentreleasecontroltotalisowindows');

UPDATE version SET Number = 114;

COMMIT;
