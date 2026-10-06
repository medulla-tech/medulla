-- SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-113.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Cloture automatique des deploiements de mise a jour majeure Windows
-- laisses dans l'etat intermediaire RELEASE_UPDATE_PENDING_REBOOT (voir
-- schema-112.sql et pulse_xmpp_agent/bin/process-deploiement-release-windows.md).
--
-- Regle metier:
--   Un deploiement dans l'etat RELEASE_UPDATE_PENDING_REBOOT ne doit etre
--   cloture (SUCCES/ERREUR) que si un inventaire machine posterieur au
--   lancement du deploiement (deploy.start) est disponible. Sans inventaire
--   plus recent, le statut doit rester RELEASE_UPDATE_PENDING_REBOOT.
--   -> Ne jamais ajouter RELEASE_UPDATE_PENDING_REBOOT a la liste
--      Stateforupdateontimeout (services/pulse2/database/xmppmaster/__init__.py,
--      Timeouterrordeploy()): cet etat est volontairement long a vivre
--      (en attente du redemarrage utilisateur) et ne doit pas etre
--      transforme en ABORT ON TIMEOUT par le job de recuperation generique.
--
-- Principe technique retenu:
--   1. La version cible (target release) d'un deploiement pending est figee
--      au moment ou le statut RELEASE_UPDATE_PENDING_REBOOT est pose, dans
--      la table up_release_update_watch. On ne la re-derive pas plus tard
--      depuis les logs (purges au bout de 30 jours, cf. event `purgelogs`)
--      ni depuis up_machine_major_windows (reconstruite chaque nuit et qui
--      ne liste plus une machine une fois la mise a jour appliquee).
--   2. La fraicheur de l'inventaire est verifiee via
--      COALESCE(local_glpi_machines.last_inventory_update, local_glpi_machines.date_mod)
--      (colonnes ajoutees ici sur cette table FEDERATED, deja connectee a
--      glpi.glpi_computers). Ce COALESCE reprend la meme convention que
--      celle deja utilisee cote GLPI natif dans
--      services/mmc/plugins/glpi/database_110.py.
--      Limite connue: `last_inventory_update` est une colonne GLPI native
--      (10.x/11.0). Les backends ITSM-NG (database_itsm_ng_14.py,
--      database_itsm_ng_21.py) ne l'exploitent pas et retombent sur
--      `date_mod` (voire `glpi_plugin_fusioninventory_agents.last_contact`).
--      Si l'installation cible tourne sur ITSM-NG, verifier au prealable
--      que `glpi_computers.last_inventory_update` existe reellement cote
--      serveur GLPI avant d'appliquer cette migration (DESCRIBE
--      glpi_computers;), sous peine d'erreur SQL sur la table FEDERATED.
--   3. La version reellement installee est relue directement depuis les
--      tables miroir local_glpi_softwares/local_glpi_items_softwareversions
--      (meme convention de parsing que up_init_table_major_win_complet()),
--      pour une seule machine, au moment de la cloture.
--   4. Un event MariaDB planifie appelle la procedure de cloture
--      periodiquement (event_scheduler doit rester ON).

START TRANSACTION;

USE `xmppmaster`;

-- ----------------------------------------------------------------------
-- 1. Exposer last_inventory_update / last_boot / date_mod sur le miroir
--    FEDERATED de glpi_computers (colonnes ignorees jusqu'ici, deja
--    disponibles cote glpi.glpi_computers). date_mod sert de repli pour
--    les installations ou last_inventory_update n'existe pas (cf. limite
--    documentee plus haut).
-- ----------------------------------------------------------------------

ALTER TABLE `xmppmaster`.`local_glpi_machines`
    ADD COLUMN IF NOT EXISTS `last_inventory_update` timestamp NULL DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS `last_boot` timestamp NULL DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS `date_mod` timestamp NULL DEFAULT NULL;

-- ----------------------------------------------------------------------
-- 2. Table de suivi: version cible figee au moment du passage en
--    RELEASE_UPDATE_PENDING_REBOOT, par sessionid de deploiement.
-- ----------------------------------------------------------------------

DROP TABLE IF EXISTS `xmppmaster`.`up_release_update_watch`;
CREATE TABLE `xmppmaster`.`up_release_update_watch` (
    `sessionid` varchar(45) NOT NULL,
    `id_machine` int(11) NOT NULL,
    `glpi_id` int(10) unsigned NOT NULL,
    `target_version` varchar(50) DEFAULT NULL,
    `target_code` varchar(50) DEFAULT NULL,
    `pending_since` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`sessionid`),
    KEY `idx_up_release_update_watch_glpi` (`glpi_id`),
    CONSTRAINT `fk_up_release_update_watch_deploy`
        FOREIGN KEY (`sessionid`) REFERENCES `xmppmaster`.`deploy` (`sessionid`)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
COMMENT = 'target release captured when a deploy enters RELEASE_UPDATE_PENDING_REBOOT, used to close it after a later inventory';

-- ----------------------------------------------------------------------
-- 3. Trigger: a chaque passage de deploy.state a
--    RELEASE_UPDATE_PENDING_REBOOT, figer la version cible connue via
--    up_machine_major_windows pour la machine concernee.
--
--    Regle metier: la version cible d'un deploiement de release Windows
--    est celle connue au moment du lancement, jamais recalculee apres
--    coup. Si la machine n'est plus candidate dans up_machine_major_windows
--    a cet instant (cas limite non attendu), aucune ligne de suivi n'est
--    creee et le deploiement restera RELEASE_UPDATE_PENDING_REBOOT jusqu'a
--    intervention manuelle: a surveiller si ce cas se presente.
-- ----------------------------------------------------------------------

DROP TRIGGER IF EXISTS `xmppmaster`.`deploy_AFTER_UPDATE_release_watch`;

DELIMITER $$

CREATE DEFINER = CURRENT_USER TRIGGER `xmppmaster`.`deploy_AFTER_UPDATE_release_watch`
AFTER UPDATE ON `xmppmaster`.`deploy` FOR EACH ROW
BEGIN
    IF NEW.state = 'RELEASE_UPDATE_PENDING_REBOOT'
       AND (OLD.state IS NULL OR OLD.state <> NEW.state) THEN
        INSERT IGNORE INTO xmppmaster.up_release_update_watch
            (sessionid, id_machine, glpi_id, target_version, target_code)
        SELECT
            NEW.sessionid, umw.id_machine, umw.glpi_id, umw.new_version, umw.newcode
        FROM xmppmaster.up_machine_major_windows umw
        INNER JOIN xmppmaster.machines m ON m.id = umw.id_machine
        WHERE m.uuid_inventorymachine = NEW.inventoryuuid
        ORDER BY umw.id_machine
        LIMIT 1;
    END IF;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- 4. Procedure de cloture: pour chaque deploiement encore
--    RELEASE_UPDATE_PENDING_REBOOT avec une ligne de suivi, verifier si un
--    inventaire posterieur au lancement confirme ou infirme la version
--    cible, et cloturer en RELEASE_UPDATE_SUCCESS / RELEASE_UPDATE_ERROR.
-- ----------------------------------------------------------------------

DROP PROCEDURE IF EXISTS `xmppmaster`.`up_close_release_update_pending_reboot`;

DELIMITER $$

CREATE PROCEDURE `xmppmaster`.`up_close_release_update_pending_reboot`()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE v_sessionid VARCHAR(45);
    DECLARE v_glpi_id INT UNSIGNED;
    DECLARE v_target_version VARCHAR(50);
    DECLARE v_target_code VARCHAR(50);
    DECLARE v_deploy_start TIMESTAMP;
    DECLARE v_last_inventory TIMESTAMP;
    DECLARE v_current_version VARCHAR(50);
    DECLARE v_current_code VARCHAR(50);

    DECLARE cur_pending CURSOR FOR
        SELECT w.sessionid, w.glpi_id, w.target_version, w.target_code,
               d.start, COALESCE(lgm.last_inventory_update, lgm.date_mod)
        FROM xmppmaster.up_release_update_watch w
        INNER JOIN xmppmaster.deploy d ON d.sessionid = w.sessionid
        LEFT JOIN xmppmaster.local_glpi_machines lgm ON lgm.id = w.glpi_id
        WHERE d.state = 'RELEASE_UPDATE_PENDING_REBOOT';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur_pending;

    read_loop: LOOP
        FETCH cur_pending INTO v_sessionid, v_glpi_id, v_target_version, v_target_code,
                                v_deploy_start, v_last_inventory;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Regle metier: pas d'inventaire posterieur au lancement -> on ne
        -- cloture pas, le deploiement reste RELEASE_UPDATE_PENDING_REBOOT.
        IF v_last_inventory IS NOT NULL AND v_last_inventory > v_deploy_start THEN

            SELECT
                SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 1), '_', -1),
                SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1)
            INTO v_current_version, v_current_code
            FROM xmppmaster.local_glpi_items_softwareversions si
            LEFT JOIN xmppmaster.local_glpi_softwareversions sv ON si.softwareversions_id = sv.id
            LEFT JOIN xmppmaster.local_glpi_softwares s ON sv.softwares_id = s.id
            WHERE si.items_id = v_glpi_id
              AND s.name LIKE 'Medulla\_%'
            ORDER BY s.id DESC
            LIMIT 1;

            IF v_current_code IS NULL THEN
                -- Inventaire plus recent mais pas encore de remontee de la
                -- cle Medulla Update Info: on ne peut pas encore conclure.
                -- Le deploiement reste RELEASE_UPDATE_PENDING_REBOOT.
                SET v_current_code = NULL;
            ELSEIF v_current_version = v_target_version AND v_current_code = v_target_code THEN
                UPDATE xmppmaster.deploy
                SET state = 'RELEASE_UPDATE_SUCCESS', endcmd = NOW()
                WHERE sessionid = v_sessionid;
                DELETE FROM xmppmaster.up_release_update_watch WHERE sessionid = v_sessionid;
            ELSE
                UPDATE xmppmaster.deploy
                SET state = 'RELEASE_UPDATE_ERROR', endcmd = NOW()
                WHERE sessionid = v_sessionid;
                DELETE FROM xmppmaster.up_release_update_watch WHERE sessionid = v_sessionid;
            END IF;

        END IF;
    END LOOP;

    CLOSE cur_pending;
END$$

DELIMITER ;

-- ----------------------------------------------------------------------
-- 5. Event: appelle la procedure de cloture toutes les 15 minutes.
--    event_scheduler doit etre a ON (SHOW VARIABLES LIKE 'event_scheduler';).
-- ----------------------------------------------------------------------

DROP EVENT IF EXISTS `xmppmaster`.`ev_close_release_update_pending_reboot`;

CREATE EVENT `xmppmaster`.`ev_close_release_update_pending_reboot`
ON SCHEDULE EVERY 15 MINUTE
DO CALL xmppmaster.up_close_release_update_pending_reboot();

UPDATE version SET Number = 113;

COMMIT;
