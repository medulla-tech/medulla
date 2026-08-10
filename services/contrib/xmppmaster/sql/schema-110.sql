-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
--
-- FILE contrib/xmppmaster/sql/schema-110.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Ajout de la table reset_machine : file d'attente de reinitialisation
-- forcee de la base agent sur les machines problematiques.
--
-- Usage : l'administrateur inscrit un JID dans cette table.
-- Le plugin_resetagent (master substitut) detecte la machine quand elle
-- passe en ligne, envoie l'ordre de reset, puis supprime la ligne.
-- Les machines hors ligne sont conservees avec un compteur de tentatives.
--


start transaction;

use xmppmaster;

-- Add inventory_id column into machines table
-- This column simplifies the joins based on uuid_inventorymachine
ALTER TABLE machines ADD COLUMN inventory_id INT GENERATED ALWAYS AS ( CAST(REPLACE(uuid_inventorymachine,'UUID','') AS UNSIGNED) ) STORED;
CREATE INDEX idx_inventory_id on machines (inventory_id);




-- create table with the uptime_machine summary
-- This table get a summary by entities of distincts uptime_machines counts
-- It specifies the entity concerned by the counts and the date range included in the count
drop table if exists uptime_machine_summary;
create table if not exists uptime_machine_summary(
    entity_id int not null, primary key(entity_id),
    month1 int not null default 0,
    month2 int not null default 0,
    month3 int not null default 0,
    month4 int not null default 0,
    month5 int not null default 0,
    month6 int not null default 0,
    begin_date datetime not null,
    end_date datetime not null default NOW()
);



-- This stored procedure delete the datas stored into uptime_machine_summary then regenerate it.
-- The procedure is launched every day by an event.
-- call refresh_uptime_machine_summary()
DELIMITER //
create or replace procedure refresh_uptime_machine_summary()
BEGIN
    delete from uptime_machine_summary;

    insert into uptime_machine_summary
        WITH machines_filtrees AS
        (
        SELECT
            jid,
            lgf.entities_id as entity_id
        FROM machines m
        JOIN local_glpi_filters lgf ON concat("UUID",lgf.id) = m.uuid_inventorymachine
        WHERE m.agenttype = 'machine'
        AND m.uuid_inventorymachine IS NOT NULL
        )

        SELECT
            mf.entity_id,
        COUNT(DISTINCT CASE
        WHEN um.date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
        AND um.date < NOW()
        THEN um.jid END) AS m1,

        COUNT(DISTINCT CASE
            WHEN um.date >= DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
            AND um.date <  DATE_FORMAT(CURDATE(), '%Y-%m-01')
            THEN um.jid END) AS m2,

        COUNT(DISTINCT CASE
            WHEN um.date >= DATE_FORMAT(CURDATE() - INTERVAL 2 MONTH, '%Y-%m-01')
            AND um.date <  DATE_FORMAT(CURDATE() - INTERVAL 1 MONTH, '%Y-%m-01')
            THEN um.jid END) AS m3,

        COUNT(DISTINCT CASE
            WHEN um.date >= DATE_FORMAT(CURDATE() - INTERVAL 3 MONTH, '%Y-%m-01')
            AND um.date <  DATE_FORMAT(CURDATE() - INTERVAL 2 MONTH, '%Y-%m-01')
            THEN um.jid END) AS m4,

        COUNT(DISTINCT CASE
            WHEN um.date >= DATE_FORMAT(CURDATE() - INTERVAL 4 MONTH, '%Y-%m-01')
            AND um.date <  DATE_FORMAT(CURDATE() - INTERVAL 3 MONTH, '%Y-%m-01')
            THEN um.jid END) AS m5,

        COUNT(DISTINCT CASE
            WHEN um.date >= DATE_FORMAT(CURDATE() - INTERVAL 5 MONTH, '%Y-%m-01')
            AND um.date <  DATE_FORMAT(CURDATE() - INTERVAL 4 MONTH, '%Y-%m-01')
            THEN um.jid END) AS m6,

            DATE_FORMAT(CURDATE() - INTERVAL 5 MONTH, '%Y-%m-01') as begin_date,
            now() as end_date

        FROM uptime_machine um
        JOIN machines_filtrees mf
        ON mf.jid = um.jid
        WHERE um.date >= DATE_FORMAT(CURDATE() - INTERVAL 5 MONTH, '%Y-%m-01')
        group by entity_id;
END;
//
DELIMITER ;



-- Create scheduled event every day at 5am, call the procedure
DELIMITER //
CREATE or replace EVENT ev_refresh_uptime_machine_summary ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE, '05:00:00')
DO
BEGIN
    call refresh_uptime_machine_summary();
END;
//
DELIMITER ;


UPDATE version SET Number = 110;


commit;
