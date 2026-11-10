-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
--
-- FILE contrib/xmppmaster/sql/schema-108.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================


start transaction;

use xmppmaster;

-- Add inventory_id column into machines table
-- This column simplifies the joins based on uuid_inventorymachine
ALTER TABLE machines ADD COLUMN IF NOT EXISTS inventory_id INT GENERATED ALWAYS AS ( CAST(REPLACE(uuid_inventorymachine,'UUID','') AS UNSIGNED) ) STORED;
CREATE INDEX IF NOT EXISTS idx_inventory_id on machines (inventory_id);




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

ALTER TABLE `xmppmaster`.`up_machine_windows`
  DROP INDEX IF EXISTS `index_uniq_entity_uuid`;

ALTER TABLE `xmppmaster`.`up_machine_windows`
  ADD INDEX IF NOT EXISTS `idx_update_entity` (`update_id`, `entityid`);


-- ----------------------------------------------------------------------
-- File d'attente de regeneration complete de base agent.
-- ----------------------------------------------------------------------

ALTER TABLE `xmppmaster`.`reset_machine`
    ADD COLUMN IF NOT EXISTS `jidrelay` varchar(255) NOT NULL AFTER `jid`;

-- ----------------------------------------------------------------------
-- Trigger de validation: une machine doit avoir un relay attribue.
-- ----------------------------------------------------------------------

DROP TRIGGER IF EXISTS `xmppmaster`.`reset_machine_BEFORE_INSERT`;

DELIMITER $$

CREATE DEFINER = CURRENT_USER TRIGGER `xmppmaster`.`reset_machine_BEFORE_INSERT`
BEFORE INSERT ON `xmppmaster`.`reset_machine` FOR EACH ROW
BEGIN
    DECLARE v_jidrelay VARCHAR(255);
    DECLARE v_jidmachine VARCHAR(255);
    DECLARE v_machine_key VARCHAR(255);

    -- Regle de normalisation du JID machine :
    --  - un JID XMPP peut etre sous forme machine@domain/resource
    --  - la ressource (/5254000d56ea) ne definit pas l'identite machine
    --  - le suffixe .u2o, s'il existe, fait partie de la cle machine
    --    pour eviter les collisions de hostname entre clients/environnements.
    --  - on recherche donc la machine sur la partie avant @ puis sans la
    --    resource, par exemple :
    --       W11-pro1-LOCAL.u2o@pulse/5254000d56ea -> W11-pro1-LOCAL.u2o
    --       W11-pro1-LOCAL.u2o@pulse            -> W11-pro1-LOCAL.u2o
    --       W11-pro1-LOCAL.u2o                  -> W11-pro1-LOCAL.u2o
    SET v_machine_key = SUBSTRING_INDEX(SUBSTRING_INDEX(NEW.jid, '/', 1), '@', 1);

        SELECT m.jid, m.groupdeploy
            INTO v_jidmachine, v_jidrelay
            FROM xmppmaster.machines m
         WHERE m.jid = v_machine_key
                OR m.jid LIKE CONCAT(v_machine_key, '@%')
         LIMIT 1;

        IF v_jidrelay IS NULL OR v_jidrelay = '' THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'No relay assigned for this machine; regenerate request rejected';
        END IF;

    SET NEW.jidrelay = v_jidrelay;
        SET NEW.jid = v_jidmachine;
END$$

DELIMITER ;


UPDATE version SET Number = 108;


commit;
