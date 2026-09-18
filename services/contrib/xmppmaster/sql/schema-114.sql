-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-114.sql
--
-- ============================================================
-- Database xmppmaster
-- ============================================================
-- Regeneration complete de la base agent via une file d'attente
-- dediee, avec validation systematique du relay attribue a la
-- machine cible.
--
-- Regle metier:
--   Une demande de regeneration_agent ne doit etre acceptee que si
--   la machine possede un relay ARS valide dans xmppmaster.machines.groupdeploy.
--   Cela evite les demandes orphelines et garantit une reconstitution
--   de l'image agent via le flux standard updateagent/relayupdateagent.
--
-- Principe technique retenu:
--   1. Le flux de regeneration repose sur la meme logique que resetagent:
--      vider img_agent, reinitialiser le contexte, puis relancer un ars_update.
--   2. La regeneration est traitee avant les reset classiques pour eviter les
--      conflits sur l'image locale.
--   3. La table conserve le JID de la machine, le JID relay associe, le motif,
--      l'heure de demande et le nombre de tentatives.

START TRANSACTION;

USE `xmppmaster`;

-- ----------------------------------------------------------------------
-- 1. File d'attente de regeneration complete de base agent.
-- ----------------------------------------------------------------------

DROP TABLE IF EXISTS `xmppmaster`.`regenerate_agent`;
CREATE TABLE `xmppmaster`.`regenerate_agent` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `jid` varchar(255) NOT NULL,
    `jidrelay` varchar(255) NOT NULL,
    `reason` varchar(255) NOT NULL DEFAULT '',
    `date_request` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `nb_attempt` int(11) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uniq_jid` (`jid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT = 'Queue de regeneration de la base agent machine. Permet de forcer la reconstruction complete de l''image/agent via le flux standard updateagent/ars_update, avant le traitement des reset_machine.';

-- ----------------------------------------------------------------------
-- 2. Trigger de validation: une machine doit avoir un relay attribue.
-- ----------------------------------------------------------------------

DROP TRIGGER IF EXISTS `xmppmaster`.`regenerate_agent_BEFORE_INSERT`;

DELIMITER $$

CREATE DEFINER = CURRENT_USER TRIGGER `xmppmaster`.`regenerate_agent_BEFORE_INSERT`
BEFORE INSERT ON `xmppmaster`.`regenerate_agent` FOR EACH ROW
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

UPDATE version SET Number = 114;

COMMIT;
