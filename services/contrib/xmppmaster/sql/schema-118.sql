-- SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-118.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Retrait de l'ancien monitoring : tables mon_*, Grafana et sondes Vector.
-- Le module n'a jamais ete configure (aucune regle, aucun evenement) ; seule
-- mon_machine se remplissait, ecrite par l'agent et lue par personne.

USE `xmppmaster`;

START TRANSACTION;

-- mon_devices et mon_event portent une cle etrangere vers mon_machine :
-- elles partent avant elle.
DROP TABLE IF EXISTS `mon_devices`;
DROP TABLE IF EXISTS `mon_event`;
DROP TABLE IF EXISTS `mon_machine`;

DROP TABLE IF EXISTS `mon_device_service`;
DROP TABLE IF EXISTS `mon_rules`;
DROP TABLE IF EXISTS `mon_panels_template`;

UPDATE version SET Number = 118;

COMMIT;
