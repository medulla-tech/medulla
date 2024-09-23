-- -*- coding: utf-8; -*-
-- SPDX-FileCopyrightText: 2022-2024 Siveo <support@siveo.net>
-- SPDX-License-Identifier: GPL-3.0-or-later

START TRANSACTION;

USE xmppmater;

create table local_glpi_entities(
    id int(10) unsigned not null default 0, primary key(id),
    name varchar(255) null default NULL,
    entities_id int(10) unsigned null default 0,
    completename text null default null,
    comment text null default null,
    level int(11) unsigned not null default 0,
    sons_cache longtext null default NULL,
    ancestors_cache longtext null default null
)ENGINE=FEDERATED CONNECTION='itsm_federated/glpi_entities';

UPDATE version SET Number = 91;

COMMIT;
