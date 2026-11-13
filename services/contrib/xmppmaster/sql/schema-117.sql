-- SPDX-FileCopyrightText: 2024-2026 Medulla, http://www.medulla-tech.io
-- SPDX-License-Identifier: GPL-2.0-or-later
-- file : services/contrib/xmppmaster/sql/schema-117.sql
--
-- =======================================
-- Database xmppmaster
-- =======================================
-- Retrait de l'ancien moteur des mises a jour et des mises a niveau.

USE `xmppmaster`;

START TRANSACTION;

-- Events
DROP EVENT IF EXISTS `Uninstall_old_package`;
DROP EVENT IF EXISTS `ev_process_pending_events`;

-- Triggers
DROP TRIGGER IF EXISTS `glpi_entity_AFTER_INSERT`;
DROP TRIGGER IF EXISTS `glpi_entity_AFTER_UPDATE`;
DROP TRIGGER IF EXISTS `glpi_entity_AFTER_DELETE`;
DROP TRIGGER IF EXISTS `glpi_entity_AFTER_INSERT_linux_auto_update_policy`;
DROP TRIGGER IF EXISTS `up_action_update_packages_AFTER_INSERT`;
DROP TRIGGER IF EXISTS `up_auto_approve_rules_AFTER_UPDATE`;
DROP TRIGGER IF EXISTS `up_black_list_BEFORE_INSERT`;
DROP TRIGGER IF EXISTS `up_black_list_AFTER_INSERT`;
DROP TRIGGER IF EXISTS `up_black_list_AFTER_UPDATE`;
DROP TRIGGER IF EXISTS `up_white_list_AFTER_INSERT`;
DROP TRIGGER IF EXISTS `up_white_list_AFTER_DELETE`;
DROP TRIGGER IF EXISTS `up_gray_list_AFTER_INSERT`;
DROP TRIGGER IF EXISTS `up_gray_list_AFTER_UPDATE`;
DROP TRIGGER IF EXISTS `up_gray_list_AFTER_DELETE`;
DROP TRIGGER IF EXISTS `up_gray_list_flop_AFTER_DELETE`;
DROP TRIGGER IF EXISTS `up_machine_linux_BEFORE_INSERT`;
DROP TRIGGER IF EXISTS `up_machine_linux_AFTER_INSERT`;
DROP TRIGGER IF EXISTS `up_machine_linux_BEFORE_UPDATE`;
DROP TRIGGER IF EXISTS `up_entity_linux_auto_update_policy_AFTER_UPDATE`;

-- Vue
DROP VIEW IF EXISTS `up_machine_activated`;

-- Procedures
DROP PROCEDURE IF EXISTS `move_update_to_white_list`;
DROP PROCEDURE IF EXISTS `up_apply_entity_linux_auto_update_policy`;
DROP PROCEDURE IF EXISTS `up_create_product_tables`;
DROP PROCEDURE IF EXISTS `up_event_move_to_white_list`;
DROP PROCEDURE IF EXISTS `up_genere_list_produit_entity`;
DROP PROCEDURE IF EXISTS `up_genere_list_rule_entity`;
DROP PROCEDURE IF EXISTS `up_init_packageid`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2003_64bit`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2007_64bit`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2010_64bit`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2013_64bit`;
DROP PROCEDURE IF EXISTS `up_init_packages_office_2016_64bit`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_MSOS_ARM64_24H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_MSOS_X64_21H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_MSOS_X64_22H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_MSOS_X64_23H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_MSOS_X64_24H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_WS_X64_2003`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_WS_X64_2008`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_WS_X64_2012`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_WS_X64_2016`;
DROP PROCEDURE IF EXISTS `up_init_packages_server_WS_X64_2019`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2005`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2008`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2010`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2012`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2013`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2015`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2017`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2019`;
DROP PROCEDURE IF EXISTS `up_init_packages_Vstudio_2022`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win_Malicious_X64`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_1903`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_21H1`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_21H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win10_X64_22H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_21H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_22H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_23H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_24H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_25H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Win11_X64_26H2`;
DROP PROCEDURE IF EXISTS `up_init_packages_Windows_Security_platform`;
DROP PROCEDURE IF EXISTS `up_init_table_download_from_kb`;
DROP PROCEDURE IF EXISTS `up_packages_office_2019_64bit`;
DROP PROCEDURE IF EXISTS `up_regenere_list_produit`;
DROP PROCEDURE IF EXISTS `up_regenere_list_produit_entity`;
DROP PROCEDURE IF EXISTS `up_reinit_table_update_data`;
DROP PROCEDURE IF EXISTS `up_search_kb_update`;
DROP PROCEDURE IF EXISTS `up_search_kb_windows`;
DROP PROCEDURE IF EXISTS `up_search_kb_windows1`;
DROP PROCEDURE IF EXISTS `up_windows_malicious_software_tool`;
DROP PROCEDURE IF EXISTS `update_datetime`;

-- Tables Windows
DROP TABLE IF EXISTS `up_machine_windows`;
DROP TABLE IF EXISTS `up_history`;
DROP TABLE IF EXISTS `up_windows_kb_uninstall`;
DROP TABLE IF EXISTS `up_white_list`;
DROP TABLE IF EXISTS `up_gray_list`;
DROP TABLE IF EXISTS `up_gray_list_flop`;
DROP TABLE IF EXISTS `up_black_list`;
DROP TABLE IF EXISTS `up_user_gray_list_commentaire`;
DROP TABLE IF EXISTS `up_auto_approve_rules`;
DROP TABLE IF EXISTS `up_list_produit`;
DROP TABLE IF EXISTS `pending_events`;
DROP TABLE IF EXISTS `up_action_update_packages`;
DROP TABLE IF EXISTS `up_packages`;
DROP TABLE IF EXISTS `up_download_from_kb`;
DROP TABLE IF EXISTS `up_download_not_kb`;
DROP TABLE IF EXISTS `up_offline_machine`;
DROP TABLE IF EXISTS `up_offline_arch`;
DROP TABLE IF EXISTS `up_offline_os`;
DROP TABLE IF EXISTS `update_datacopy`;
DROP TABLE IF EXISTS `update_data`;

-- Tables produits (une par une : up_packages_major_Lang_code reste)
DROP TABLE IF EXISTS `up_packages_MSOS_ARM64_24H2`;
DROP TABLE IF EXISTS `up_packages_MSOS_X64_21H2`;
DROP TABLE IF EXISTS `up_packages_MSOS_X64_22H2`;
DROP TABLE IF EXISTS `up_packages_MSOS_X64_23H2`;
DROP TABLE IF EXISTS `up_packages_MSOS_X64_24H2`;
DROP TABLE IF EXISTS `up_packages_office_2003_64bit`;
DROP TABLE IF EXISTS `up_packages_office_2007_64bit`;
DROP TABLE IF EXISTS `up_packages_office_2010_64bit`;
DROP TABLE IF EXISTS `up_packages_office_2013_64bit`;
DROP TABLE IF EXISTS `up_packages_office_2016_64bit`;
DROP TABLE IF EXISTS `up_packages_office_2019_64bit`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2005`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2008`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2010`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2012`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2013`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2015`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2017`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2019`;
DROP TABLE IF EXISTS `up_packages_Vstudio_2022`;
DROP TABLE IF EXISTS `up_packages_Win_Malicious_X64`;
DROP TABLE IF EXISTS `up_packages_Win10_X64_1903`;
DROP TABLE IF EXISTS `up_packages_Win10_X64_21H1`;
DROP TABLE IF EXISTS `up_packages_Win10_X64_21H2`;
DROP TABLE IF EXISTS `up_packages_Win10_X64_22H2`;
DROP TABLE IF EXISTS `up_packages_Win11_X64`;
DROP TABLE IF EXISTS `up_packages_Win11_X64_21H2`;
DROP TABLE IF EXISTS `up_packages_Win11_X64_22H2`;
DROP TABLE IF EXISTS `up_packages_Win11_X64_23H2`;
DROP TABLE IF EXISTS `up_packages_Win11_X64_24H2`;
DROP TABLE IF EXISTS `up_packages_Win11_X64_25H2`;
DROP TABLE IF EXISTS `up_packages_Win11_X64_26H2`;
DROP TABLE IF EXISTS `up_packages_Windows_Security_platform`;
DROP TABLE IF EXISTS `up_packages_WS_X64_2003`;
DROP TABLE IF EXISTS `up_packages_WS_X64_2008`;
DROP TABLE IF EXISTS `up_packages_WS_X64_2012`;
DROP TABLE IF EXISTS `up_packages_WS_X64_2016`;
DROP TABLE IF EXISTS `up_packages_WS_X64_2019`;

-- Tables Linux
DROP TABLE IF EXISTS `up_package_cve_linux`;
DROP TABLE IF EXISTS `up_machine_update_linux`;
DROP TABLE IF EXISTS `up_cve_linux`;
DROP TABLE IF EXISTS `up_package_linux`;
DROP TABLE IF EXISTS `up_machine_linux`;
DROP TABLE IF EXISTS `up_entity_linux_approved_releases`;
DROP TABLE IF EXISTS `up_entity_linux_auto_update_policy`;
DROP TABLE IF EXISTS `up_linux_os_versions`;
-- Creees par l'ORM du substitut, sans schema
DROP TABLE IF EXISTS `up_debian_versions`;
DROP TABLE IF EXISTS `up_rhel_versions`;
DROP TABLE IF EXISTS `up_ubuntu_versions`;

-- Parametres de l'ancien moteur, seule utilisation de la table
DROP TABLE IF EXISTS `applicationconfig`;


-- Events
DROP EVENT IF EXISTS `appel_procedure_soir_init_major_table`;
DROP EVENT IF EXISTS `ev_close_release_update_pending_reboot`;

-- Triggers
DROP TRIGGER IF EXISTS `deploy_AFTER_UPDATE_release_watch`;

DROP TRIGGER IF EXISTS `machines_BEFORE_UPDATE`;

DELIMITER $$
CREATE TRIGGER `machines_BEFORE_UPDATE` BEFORE UPDATE ON `machines` FOR EACH ROW
BEGIN
IF NEW.uuid_inventorymachine <> OLD.uuid_inventorymachine THEN
	SET NEW.id_glpi = SUBSTRING(NEW.uuid_inventorymachine, 5);
    END IF;
END$$
DELIMITER ;

-- Procedures
DROP PROCEDURE IF EXISTS `up_init_table_major_win_complet`;
DROP PROCEDURE IF EXISTS `up_close_release_update_pending_reboot`;

-- Tables
DROP TABLE IF EXISTS `up_release_update_watch`;
DROP TABLE IF EXISTS `up_machine_major_windows`;
DROP TABLE IF EXISTS `up_major_win`;
DROP TABLE IF EXISTS `up_packages_major_Lang_code`;

-- Action rapide
DELETE FROM `qa_custom_command`
 WHERE `user` = 'allusers' AND `os` = 'windows' AND `namecmd` = 'Disable Windows Updates';

-- Statuts de deploiement de l'ancien moteur (schemas 112 et 114)
DELETE FROM `def_remote_deploy_status`
 WHERE (`regex_logmessage` = '.*Windows release update: connected user=.*; target release=.*'
        AND `status` = 'RELEASE_UPDATE_PENDING_REBOOT')
    OR (`regex_logmessage` = '.*Windows release update: no connected user; target release=.*'
        AND `status` = 'RELEASE_UPDATE_PENDING_REBOOT')
    OR (`regex_logmessage` = '.*Windows release update aborted by user .*'
        AND `status` = 'ABORT PACKAGE EXECUTION BY USER')
    OR (`regex_logmessage` = '.*Windows release update aborted: user response timed out .*'
        AND `status` = 'ABORT PACKAGE EXECUTION ON USER TIMEOUT')
    OR (`regex_logmessage` = '.*Windows release update execution confirmed: ISO control started.*'
        AND `status` = 'DEPLOYEMENT RELEASE CONTROLE TOTAL ISO WINDOWS');

UPDATE version SET Number = 117;

COMMIT;
