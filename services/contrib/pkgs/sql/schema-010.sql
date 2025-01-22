-- -*- coding: utf-8; -*-
-- SPDX-FileCopyrightText: 2022-2024 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

START TRANSACTION;

USE `pkgs`;

ALTER TABLE `pkgs`.`pkgs_rules_global` 
ADD UNIQUE IF NOT EXISTS (pkgs_rules_algos_id, pkgs_cluster_ars_id, subject);

UPDATE version SET Number = 10;

COMMIT;
