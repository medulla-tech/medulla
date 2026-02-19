-- =============================================================
-- Création des tables de configuration des plugins pour Medulla
--
-- Contexte :
-- Centralisation des paramètres de configuration dynamiques liés à GLPI.
-- Cette table remplace le fichier de configuration glpi.ini.local.
--
-- Qui ?
-- - Administrateurs / techniciens : gestion des paramètres via le module admin.
-- - Applications / services Medulla : lecture des paramètres de configuration.
--
-- Où ?
-- - Base de données 'admin'.
--
-- Quoi ?
-- - Stocke les paramètres de configuration sous forme structurée :
--   section, nom, type, valeur, valeur par défaut et description.
--
-- Règles :
-- - Unicité du couple (section, nom) afin d'éviter les doublons.
-- - Le paramètre est actif par défaut (`activer = TRUE`).
-- - Le type par défaut est `string`.
-- - La description est obligatoire pour documenter l’usage du paramètre.
-- =============================================================

START TRANSACTION;

USE admin;

-- ====================================================================
-- GLPI CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS glpi_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_glpi_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration GLPI pour Medulla';


INSERT INTO glpi_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin GLPI (0=actif, 1=inactif)'),
('main', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données (mysql, postgresql, etc.)'),
('main', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données GLPI'),
('main', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données GLPI'),
('main', 'dbname', 1, 'string', 'glpi', 'glpi', 'Nom de la base de données GLPI'),
('main', 'dbuser', 1, 'string', 'glpi', 'glpi', 'Utilisateur de base de données GLPI'),
('main', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données GLPI (format: {scheme}value)'),
('main', 'localisation', 1, 'booleen', '1', '1', 'Permettre aux utilisateurs de filtrer les ordinateurs avec un sélecteur d''entité'),
('main', 'hide_itsm_link', 1, 'booleen', '0', '0', 'Masquer le lien ITSM'),
('main', 'glpi_computer_uri', 1, 'string', 'http://hba.medulla-tech.io/glpi/front/computer.form.php?id=', NULL, 'URI pour accéder à un ordinateur dans GLPI'),
('global', 'taskdeploy', 1, 'booleen', '0', '0', 'Déploiements gérés par master (0=oui, 1=non)'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de base de données'),
('connection', 'server', 1, 'string', '192.168.200.72', NULL, 'Serveur XMPP ou de connexion'),
('connection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe de connexion au serveur'),
('defaultconnection', 'serverip', 1, 'string', '192.168.200.72', NULL, 'Adresse IP du serveur par défaut'),
('defaultconnection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe de connexion par défaut'),
('defaultconnection', 'guacamole_baseurl', 1, 'string', 'http://hba.medulla-tech.io/guacamole/#/client/@@CUX_ID@@?username=root&password=42JZO9B3SV7Kx9V6csKJkz3pcVvtgvc31bCQXfWq', NULL, 'URL de base de Guacamole avec identifiants'),
('defaultconnection', 'keyAES32', 1, 'string', 'ng4yUQpHvVZDnVstCSweMJOpcdgFwqP4', NULL, 'Clé AES 32 caractères pour le chiffrement'),
('syncthing', 'announce_server', 1, 'string', 'https://sync-relay.siveo.net:8443/?id=CSI6OUD-VYW773R-J6I54Y7-NWHPXGJ-NDTWLPU-3G3MCAM-6FTYJJX-BRX62Q5', NULL, 'Serveur d''annonce Syncthing'),
('grafana_api', 'api_key', 1, 'string', 'eyJrIjoiUjNMbzhBUFAzdHViV0ZPSlVxNFZzRjlvOW5wY21yb0IiLCJuIjoiYWRtaW5rZXkiLCJpZCI6MX0=', NULL, 'Clé API Grafana'),
('grafana_api', 'render_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/render/d-solo', NULL, 'URL de rendu Grafana'),
('grafana_api', 'graph_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/d-solo', NULL, 'URL des graphiques Grafana'),
('browserfile', 'rootfilesystem', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Répertoire racine du système de fichiers pour le navigateur'),
('browserfile', 'defaultdir', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Répertoire par défaut du navigateur'),
('webservices', 'purge_machine', 1, 'booleen', '1', '1', 'Activer la purge automatique des machines (0=désactivé, 1=activé)'),
('webservices', 'glpi_base_url', 1, 'string', 'http://hba.medulla-tech.io/glpi/apirest.php/', NULL, 'URL de base de l''API REST GLPI'),
('webservices', 'glpi_username', 1, 'string', 'root', 'root', 'Utilisateur pour l''authentification API GLPI'),
('webservices', 'glpi_password', 1, 'string', 'M3dull4+HBA', NULL, 'Mot de passe pour l''authentification API GLPI (format: {scheme}value)'),
('authentication_glpi', 'baseurl', 1, 'string', 'http://hba.medulla-tech.io/glpi', NULL, 'URL de base de GLPI pour l''authentification'),
('authentication_glpi', 'doauth', 1, 'booleen', '1', '1', 'Activer l''authentification GLPI (0=désactivé, 1=activé)'),
('provisioning_glpi', 'exclude', 1, 'string', 'root', 'root', 'Utilisateurs à exclure du provisioning (séparés par virgules)'),
('provisioning_glpi', 'profiles_order', 1, 'string', 'Super-Admin Admin Technician', 'Super-Admin Admin Technician', 'Ordre des profils GLPI à provisionner (espace-séparé)'),
('provisioning_glpi', 'profile_acl_Super-Admin', 1, 'string', ':inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#editEntity:admin#admin#deleteEntity:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#deleteProfileUser:admin#admin#desactivateUser:admin#admin#downloadAgent:dashboard#main#default:dashboard#main#alertsentity:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs/', NULL, 'Liste des ACL pour le profil Super-Admin'),
('provisioning_glpi', 'profile_acl_Admin', 1, 'string', ':inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#deleteProfileUser:admin#admin#desactivateUser:admin#admin#downloadAgent:dashboard#main#default:dashboard#main#alertsentity:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs/', NULL, 'Liste des ACL pour le profil Admin'),
('provisioning_glpi', 'profile_acl_Technician', 1, 'string', ':inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#listUsersofEntity:admin#admin#downloadAgent:dashboard#main#default:dashboard#main#alertsentity:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs/', NULL, 'Liste des ACL pour le profil Technician')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


CREATE TABLE IF NOT EXISTS glpi_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_glpi_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration GLPI pour Medulla';


INSERT INTO glpi_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin GLPI (0=actif, 1=inactif)'),
('main', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données (mysql, postgresql, etc.)'),
('main', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données GLPI'),
('main', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données GLPI'),
('main', 'dbname', 1, 'string', 'glpi', 'glpi', 'Nom de la base de données GLPI'),
('main', 'dbuser', 1, 'string', 'glpi', 'glpi', 'Utilisateur de base de données GLPI'),
('main', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données GLPI (format: {scheme}value)'),
('main', 'localisation', 1, 'booleen', '1', '1', 'Permettre aux utilisateurs de filtrer les ordinateurs avec un sélecteur d''entité'),
('main', 'hide_itsm_link', 1, 'booleen', '0', '0', 'Masquer le lien ITSM'),
('main', 'glpi_computer_uri', 1, 'string', 'http://hba.medulla-tech.io/glpi/front/computer.form.php?id=', NULL, 'URI pour accéder à un ordinateur dans GLPI'),
('global', 'taskdeploy', 1, 'booleen', '0', '0', 'Déploiements gérés par master (0=oui, 1=non)'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de base de données'),
('connection', 'server', 1, 'string', '192.168.200.72', NULL, 'Serveur XMPP ou de connexion'),
('connection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe de connexion au serveur'),
('defaultconnection', 'serverip', 1, 'string', '192.168.200.72', NULL, 'Adresse IP du serveur par défaut'),
('defaultconnection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe de connexion par défaut'),
('defaultconnection', 'guacamole_baseurl', 1, 'string', 'http://hba.medulla-tech.io/guacamole/#/client/@@CUX_ID@@?username=root&password=42JZO9B3SV7Kx9V6csKJkz3pcVvtgvc31bCQXfWq', NULL, 'URL de base de Guacamole avec identifiants'),
('defaultconnection', 'keyAES32', 1, 'string', 'ng4yUQpHvVZDnVstCSweMJOpcdgFwqP4', NULL, 'Clé AES 32 caractères pour le chiffrement'),
('syncthing', 'announce_server', 1, 'string', 'https://sync-relay.siveo.net:8443/?id=CSI6OUD-VYW773R-J6I54Y7-NWHPXGJ-NDTWLPU-3G3MCAM-6FTYJJX-BRX62Q5', NULL, 'Serveur d''annonce Syncthing'),
('grafana_api', 'api_key', 1, 'string', 'eyJrIjoiUjNMbzhBUFAzdHViV0ZPSlVxNFZzRjlvOW5wY21yb0IiLCJuIjoiYWRtaW5rZXkiLCJpZCI6MX0=', NULL, 'Clé API Grafana'),
('grafana_api', 'render_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/render/d-solo', NULL, 'URL de rendu Grafana'),
('grafana_api', 'graph_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/d-solo', NULL, 'URL des graphiques Grafana'),
('browserfile', 'rootfilesystem', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Répertoire racine du système de fichiers pour le navigateur'),
('browserfile', 'defaultdir', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Répertoire par défaut du navigateur'),
('webservices', 'purge_machine', 1, 'booleen', '1', '1', 'Activer la purge automatique des machines (0=désactivé, 1=activé)'),
('webservices', 'glpi_base_url', 1, 'string', 'http://hba.medulla-tech.io/glpi/apirest.php/', NULL, 'URL de base de l''API REST GLPI'),
('webservices', 'glpi_username', 1, 'string', 'root', 'root', 'Utilisateur pour l''authentification API GLPI'),
('webservices', 'glpi_password', 1, 'string', 'M3dull4+HBA', NULL, 'Mot de passe pour l''authentification API GLPI (format: {scheme}value)'),
('authentication_glpi', 'baseurl', 1, 'string', 'http://hba.medulla-tech.io/glpi', NULL, 'URL de base de GLPI pour l''authentification'),
('authentication_glpi', 'doauth', 1, 'booleen', '1', '1', 'Activer l''authentification GLPI (0=désactivé, 1=activé)'),
('provisioning_glpi', 'exclude', 1, 'string', 'root', 'root', 'Utilisateurs à exclure du provisioning (séparés par virgules)'),
('provisioning_glpi', 'profiles_order', 1, 'string', 'Super-Admin Admin Technician', 'Super-Admin Admin Technician', 'Ordre des profils GLPI à provisionner (espace-séparé)'),
('provisioning_glpi', 'profile_acl_Super-Admin', 1, 'string', ':inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#editEntity:admin#admin#deleteEntity:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#deleteProfileUser:admin#admin#desactivateUser:admin#admin#downloadAgent:dashboard#main#default:dashboard#main#alertsentity:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs/', NULL, 'Liste des ACL pour le profil Super-Admin'),
('provisioning_glpi', 'profile_acl_Admin', 1, 'string', ':inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#listUsersofEntity:admin#admin#editUser:admin#admin#deleteUser:admin#admin#deleteProfileUser:admin#admin#desactivateUser:admin#admin#downloadAgent:dashboard#main#default:dashboard#main#alertsentity:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs/', NULL, 'Liste des ACL pour le profil Admin'),
('provisioning_glpi', 'profile_acl_Technician', 1, 'string', ':inventory#inventory#incoming:inventory#inventory#index:inventory#inventory#hardware:inventory#inventory#network:inventory#inventory#controller:inventory#inventory#drive:inventory#inventory#input:inventory#inventory#memory:inventory#inventory#monitor:inventory#inventory#port:inventory#inventory#printer:inventory#inventory#sound:inventory#inventory#storage:inventory#inventory#videocard:inventory#inventory#software:inventory#inventory#registry:inventory#inventory#view:inventory#inventory#infos:inventory#inventory#graphs:inventory#inventory#graph:inventory#inventory#csv:inventory#inventory#header:mail#domains#index:mail#domains#add:mail#domains#edit:mail#domains#members:mail#domains#delete:mail#aliases#index:mail#aliases#add:mail#aliases#edit:mail#aliases#delete:network#network#index:network#network#delete:network#network#deletehost:network#network#deleterecord:network#network#edithost:network#network#editrecord:network#network#add:network#network#edit:network#network#addhost:network#network#addrecord:network#network#zonemembers:network#network#zonerecords:network#network#subnetadd:network#network#subnetedit:network#network#subnetindex:network#network#subnetdelete:network#network#subnetaddhost:network#network#subnetedithost:network#network#subnetdeletehost:network#network#subnetmembers:network#network#services:network#network#servicelog:network#network#servicestart:network#network#servicestop:network#network#servicereload:network#network#servicerestart:samba#shares#index:samba#shares#add:samba#shares#backup:samba#shares#delete:samba#shares#details:samba#machines#index:samba#machines#edit:samba#machines#delete:samba#config#index:samba#config#restart:samba#config#reload:base#main#default:base#status#index:base#computers#index:base#computers#add:base#computers#edit:base#computers#delete:base#computers#get_file:base#computers#computersgroupcreator:base#computers#computersgroupcreatesubedit:base#computers#computersgroupcreatesubdel:base#computers#computersgroupedit:base#computers#computersgroupsubedit:base#computers#computersgroupsubdel:base#computers#tmpdisplay:base#computers#display:base#computers#edit_share:base#computers#creator_step2:base#computers#save:base#computers#save_detail:base#computers#list:base#computers#listFavourite:base#computers#delete_group:base#computers#remove_machine:base#computers#csv:base#computers#updateMachineCache:base#computers#machinesList:base#computers#ajaxMachinesList:base#computers#machinesListglpi:base#computers#ajaxMachinesListglpi:base#computers#xmppMachinesList:base#computers#ajaxXmppMachinesList:base#computers#createStaticGroup:base#computers#createAntivirusStaticGroup:base#computers#createOSStaticGroup:base#computers#createMachinesStaticGroup:base#computers#createMachinesStaticGroupdeploy:base#computers#createBackupStaticGroup:base#computers#entityList:base#computers#addEntity:base#computers#locationList:base#computers#addLocation:base#computers#entityRules:base#computers#addEntityRule:base#computers#deleteEntityRule:base#computers#moveRuleUp:base#computers#moveRuleDown:base#computers#glpitabs:base#computers#register_target:base#computers#createCustomMenuStaticGroup:base#computers#imgtabs:base#computers#bootmenu_remove:base#computers#showtarget:base#computers#showsyncstatus:base#computers#addservice:base#computers#editservice:base#computers#delservice:base#computers#addimage:base#computers#editimage:base#computers#images_delete:base#computers#multicast:base#computers#computers_list:base#computers#select_location:base#computers#remove_from_pull:base#computers#groupmsctabs:base#computers#msctabs:base#computers#download_file:base#computers#download_file_remove:base#computers#download_file_get:base#computers#vnc_client:base#computers#msctabsplay:base#computers#msctabspause:base#computers#msctabsstop:base#computers#msctabsstatus:base#computers#reschedule:base#computers#delete_command:base#computers#msctabssinglestatus:base#computers#package_detail:base#computers#start_command:base#computers#start_adv_command:base#computers#convergence:base#computers#convergenceuninstall:base#computers#start_quick_action:base#computers#packages:base#computers#statuscsv:admin#admin#entitiesManagement:admin#admin#listUsersofEntity:admin#admin#downloadAgent:dashboard#main#default:dashboard#main#alertsentity:kiosk#kiosk#index:kiosk#kiosk#add:kiosk#kiosk#edit:kiosk#kiosk#acknowledges:pkgs#pkgs#index:pkgs#pkgs#add:pkgs#pkgs#edit:pkgs#pkgs#detail:pkgs#pkgs#createGroupLicence:pkgs#pkgs#pending:pkgs#pkgs#rsync:pkgs#pkgs#desynchronization:pkgs#pkgs#delete:updates#updates#index:updates#updates#detailsByMachines:updates#updates#deployAllUpdates:updates#updates#deploySpecificUpdate:updates#updates#detailsByUpdates:updates#updates#hardwareConstraintsForMajorUpdates:updates#updates#detailsSpecificUpdate:updates#updates#MajorEntitiesList:updates#updates#pendingUpdateByMachine:updates#updates#auditUpdateByMachine:updates#updates#updatesListMajorWin:updates#updates#majorDetailsByMachines:updates#updates#groupUpdateMajorEntity:updates#updates#auditByEntity:updates#updates#auditByUpdate:xmppmaster#xmppmaster#auditmypastdeploys:xmppmaster#xmppmaster#auditmypastdeploysteam:xmppmaster#xmppmaster#auditteam:xmppmaster#xmppmaster#convergence:xmppmaster#xmppmaster#auditteamconvergence:xmppmaster#xmppmaster#consolexmpp:xmppmaster#xmppmaster#customQA:xmppmaster#xmppmaster#shareqa:xmppmaster#xmppmaster#machine_xmpp_detail:xmppmaster#xmppmaster#editqa:xmppmaster#xmppmaster#listconffile:xmppmaster#xmppmaster#deleteqa:xmppmaster#xmppmaster#logbymachine:xmppmaster#xmppmaster#consolecomputerxmpp:xmppmaster#xmppmaster#monitoringview:xmppmaster#xmppmaster#remoteeditorconfiguration:xmppmaster#xmppmaster#remoteeditorconfigurationlist:xmppmaster#xmppmaster#listfichierconf:xmppmaster#xmppmaster#ActionQuickconsole:xmppmaster#xmppmaster#ActionQuickGroup:xmppmaster#xmppmaster#QAcustommachgrp:xmppmaster#xmppmaster#xmppMonitoring:xmppmaster#xmppmaster#deployquick:xmppmaster#xmppmaster#deployquickgroup:xmppmaster#xmppmaster#viewlogs:xmppmaster#xmppmaster#loglistgrpmachine:xmppmaster#xmppmaster#packageslist:xmppmaster#xmppmaster#popupReloadDeploy:xmppmaster#xmppmaster#rescheduleconvergence:xmppmaster#xmppmaster#reloaddeploy:base#computers#computersgroupcreator#tabdyn:base#computers#computersgroupcreator#tabsta:base#computers#computersgroupcreator#tabfromfile:base#computers#computersgroupcreatesubedit#tabdyn:base#computers#computersgroupcreatesubedit#tabsta:base#computers#computersgroupcreatesubedit#tabfromfile:base#computers#computersgroupcreatesubdel#tabdyn:base#computers#computersgroupcreatesubdel#tabsta:base#computers#computersgroupcreatesubdel#tabfromfile:base#computers#glpitabs#tab0:base#computers#glpitabs#tab1:base#computers#glpitabs#tab2:base#computers#glpitabs#tab3:base#computers#glpitabs#tab4:base#computers#glpitabs#tab5:base#computers#glpitabs#tab6:base#computers#glpitabs#tab7:base#computers#glpitabs#tab8:base#computers#glpitabs#tab9:base#computers#imgtabs#tabbootmenu:base#computers#imgtabs#tabimages:base#computers#imgtabs#tabservices:base#computers#imgtabs#tabimlogs:base#computers#imgtabs#tabconfigure:base#computers#groupmsctabs#grouptablaunch:base#computers#groupmsctabs#grouptablogs:base#computers#msctabs#tablaunch:base#computers#msctabs#tablogs/', NULL, 'Liste des ACL pour le profil Technician')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- XMPP CONF
-- ====================================================================

CREATE TABLE IF NOT EXISTS xmpp_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_xmpp_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration XMPP master pour Medulla';


INSERT INTO xmpp_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin XMPP (0=actif)'),
('main', 'tempdir', 1, 'string', '/var/tmp/mmc-xmppmaster', '/var/tmp/mmc-xmppmaster', 'Répertoire temporaire du plugin'),
('global', 'log_level', 1, 'string', 'INFO', 'INFO', 'Niveau de log (DEBUG/INFO/...)'),
('global', 'inter_agent', 1, 'booleen', '0', '0', 'Autoriser les messages inter-agent'),
('global', 'taskdeploy', 1, 'booleen', '0', '0', 'Déploiements gérés par master'),
('database', 'dbdriver', 1, 'string', 'mysql+mysqldb', 'mysql+mysqldb', 'Driver base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte base XMPP'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port base XMPP'),
('database', 'dbname', 1, 'string', 'xmppmaster', 'xmppmaster', 'Nom base XMPP'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur base XMPP'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe base XMPP'),
('database', 'dbpoolrecycle', 1, 'entier', '5', '5', 'Recyclage des connexions (s)'),
('database', 'dbpoolsize', 1, 'entier', '60', '60', 'Taille du pool de connexions'),
('database', 'dbpooltimeout', 1, 'entier', '30', '30', 'Timeout du pool (s)'),
('configuration_server', 'confmuc_password', 1, 'string', 'chatroomsecret', 'chatroomsecret', 'Mot de passe du MUC de config'),
('configuration_server', 'confmuc_chatroom', 1, 'string', 'configmaster', 'configmaster', 'Nom du salon MUC de config'),
('connection', 'server', 1, 'string', '192.168.200.72', '192.168.56.2', 'Serveur XMPP principal'),
('connection', 'port', 1, 'entier', '5222', '5222', 'Port XMPP'),
('connection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe XMPP'),
('chatroom', 'server', 1, 'string', 'conference.pulse', 'conference.pulse', 'Serveur des salons XMPP'),
('chatroom', 'password', 1, 'string', 'chatroomsecret', 'chatroomsecret', 'Mot de passe des salons XMPP'),
('chat', 'domain', 1, 'string', 'pulse', 'pulse', 'Domaine XMPP pour le chat'),
('master', 'showinfo', 1, 'booleen', '0', '0', 'Afficher les infos master'),
('master', 'showplugins', 1, 'booleen', '0', '0', 'Afficher les plugins master'),
('master', 'blacklisted_mac_addresses', 1, 'string', '00:00:00:00:00:00', '00:00:00:00:00:00', 'Liste noire des MAC doublons'),
('plugins', 'dirplugins', 1, 'string', '/var/lib/pulse2/xmpp_baseplugin/', '/var/lib/pulse2/xmpp_baseplugin/', 'Répertoire des plugins XMPP'),
('plugins', 'dirschedulerplugins', 1, 'string', '/var/lib/pulse2/xmpp_basepluginscheduler/', '/var/lib/pulse2/xmpp_basepluginscheduler/', 'Répertoire des plugins scheduler'),
('plugins', 'pluginlist', 1, 'string', 'resultinventory, inventoryconf, assessor_agent, registeryagent', 'resultinventory, inventoryconf, assessor_agent, registeryagent', 'Liste des plugins chargés'),
('plugins', 'pluginliststart', 1, 'string', 'loadpluginschedulerlistversion, loadautoupdate, loadpluginlistversion, loadshowregistration, loadreconf', 'loadpluginschedulerlistversion, loadautoupdate, loadpluginlistversion, loadshowregistration, loadreconf', 'Plugins chargés au démarrage'),
('defaultconnection', 'serverip', 1, 'string', '192.168.200.72', '192.168.56.2', 'IP du serveur par défaut'),
('defaultconnection', 'port', 1, 'entier', '5222', '5222', 'Port du serveur par défaut'),
('defaultconnection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe par défaut'),
('defaultconnection', 'jid', 1, 'string', '0a0027000000@localhost', '0a0027000000@localhost', 'JID forcé'),
('defaultconnection', 'guacamole_baseurl', 1, 'string', 'http://hba.medulla-tech.io/guacamole/#/client/@@CUX_ID@@?username=root&password=42JZO9B3SV7Kx9V6csKJkz3pcVvtgvc31bCQXfWq', 'http://192.168.56.2/guacamole/', 'URL Guacamole par défaut'),
('defaultconnection', 'keyAES32', 1, 'string', 'ng4yUQpHvVZDnVstCSweMJOpcdgFwqP4', 'abcdefghijklmnopqrstuvwxyz012345', 'Clé AES 32 caractères'),
('browserfile', 'rootfilesystem', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Racine transfert de fichiers'),
('browserfile', 'defaultdir', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Répertoire par défaut transfert'),
('syncthing', 'announce_server', 1, 'string', 'https://sync-relay.siveo.net:8443/?id=CSI6OUD-VYW773R-J6I54Y7-NWHPXGJ-NDTWLPU-3G3MCAM-6FTYJJX-BRX62Q5', 'https://192.168.56.2:8443/?id=IGQIW2T-OHEFK3P-JHSB6KH-OHHYABS-YEWJRVC-M6F4NLZ-D6U55ES-VXIVMA3', 'Serveur d''annonce Syncthing'),
('grafana_api', 'api_key', 1, 'string', 'eyJrIjoiUjNMbzhBUFAzdHViV0ZPSlVxNFZzRjlvOW5wY21yb0IiLCJuIjoiYWRtaW5rZXkiLCJpZCI6MX0=', NULL, 'Clé API Grafana'),
('grafana_api', 'render_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/render/d-solo', 'http://192.168.56.2/grafana/render/d-solo', 'URL de rendu Grafana'),
('grafana_api', 'graph_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/d-solo', 'http://192.168.56.2/grafana/d-solo', 'URL des graphiques Grafana'),
('computer_list', 'summary', 1, 'string', 'cn description os type user entity', 'cn description os type user entity', 'Colonnes liste machines'),
('computer_list', 'ordered', 1, 'booleen', '1', '1', 'Trier la liste des machines'),
('submaster', 'host', 1, 'string', '127.0.0.1', '127.0.0.1', 'Hôte du master substitut'),
('submaster', 'port', 1, 'entier', '57040', '57040', 'Port du master substitut'),
('submaster', 'ip_format', 1, 'string', 'ipv4', 'ipv4', 'Format IP utilisé'),
('submaster', 'allowed_token', 1, 'string', '4O&vHYKG3Cqq3RCUJu!vnQu+dBGwDkpZ', '4O&vHYKG3Cqq3RCUJu!vnQu+dBGwDkpZ', 'Jeton autorisé pour le substitut'),
('submaster', 'check_hostname', 1, 'booleen', '1', '1', 'Vérifier le certificat du serveur')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


CREATE TABLE IF NOT EXISTS xmpp_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_xmpp_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration XMPP master pour Medulla';


INSERT INTO xmpp_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin XMPP (0=actif)'),
('main', 'tempdir', 1, 'string', '/var/tmp/mmc-xmppmaster', '/var/tmp/mmc-xmppmaster', 'Répertoire temporaire du plugin'),
('global', 'log_level', 1, 'string', 'INFO', 'INFO', 'Niveau de log (DEBUG/INFO/...)'),
('global', 'inter_agent', 1, 'booleen', '0', '0', 'Autoriser les messages inter-agent'),
('global', 'taskdeploy', 1, 'booleen', '0', '0', 'Déploiements gérés par master'),
('database', 'dbdriver', 1, 'string', 'mysql+mysqldb', 'mysql+mysqldb', 'Driver base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte base XMPP'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port base XMPP'),
('database', 'dbname', 1, 'string', 'xmppmaster', 'xmppmaster', 'Nom base XMPP'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur base XMPP'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe base XMPP'),
('database', 'dbpoolrecycle', 1, 'entier', '5', '5', 'Recyclage des connexions (s)'),
('database', 'dbpoolsize', 1, 'entier', '60', '60', 'Taille du pool de connexions'),
('database', 'dbpooltimeout', 1, 'entier', '30', '30', 'Timeout du pool (s)'),
('configuration_server', 'confmuc_password', 1, 'string', 'chatroomsecret', 'chatroomsecret', 'Mot de passe du MUC de config'),
('configuration_server', 'confmuc_chatroom', 1, 'string', 'configmaster', 'configmaster', 'Nom du salon MUC de config'),
('connection', 'server', 1, 'string', '192.168.200.72', '192.168.56.2', 'Serveur XMPP principal'),
('connection', 'port', 1, 'entier', '5222', '5222', 'Port XMPP'),
('connection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe XMPP'),
('chatroom', 'server', 1, 'string', 'conference.pulse', 'conference.pulse', 'Serveur des salons XMPP'),
('chatroom', 'password', 1, 'string', 'chatroomsecret', 'chatroomsecret', 'Mot de passe des salons XMPP'),
('chat', 'domain', 1, 'string', 'pulse', 'pulse', 'Domaine XMPP pour le chat'),
('master', 'showinfo', 1, 'booleen', '0', '0', 'Afficher les infos master'),
('master', 'showplugins', 1, 'booleen', '0', '0', 'Afficher les plugins master'),
('master', 'blacklisted_mac_addresses', 1, 'string', '00:00:00:00:00:00', '00:00:00:00:00:00', 'Liste noire des MAC doublons'),
('plugins', 'dirplugins', 1, 'string', '/var/lib/pulse2/xmpp_baseplugin/', '/var/lib/pulse2/xmpp_baseplugin/', 'Répertoire des plugins XMPP'),
('plugins', 'dirschedulerplugins', 1, 'string', '/var/lib/pulse2/xmpp_basepluginscheduler/', '/var/lib/pulse2/xmpp_basepluginscheduler/', 'Répertoire des plugins scheduler'),
('plugins', 'pluginlist', 1, 'string', 'resultinventory, inventoryconf, assessor_agent, registeryagent', 'resultinventory, inventoryconf, assessor_agent, registeryagent', 'Liste des plugins chargés'),
('plugins', 'pluginliststart', 1, 'string', 'loadpluginschedulerlistversion, loadautoupdate, loadpluginlistversion, loadshowregistration, loadreconf', 'loadpluginschedulerlistversion, loadautoupdate, loadpluginlistversion, loadshowregistration, loadreconf', 'Plugins chargés au démarrage'),
('defaultconnection', 'serverip', 1, 'string', '192.168.200.72', '192.168.56.2', 'IP du serveur par défaut'),
('defaultconnection', 'port', 1, 'entier', '5222', '5222', 'Port du serveur par défaut'),
('defaultconnection', 'password', 1, 'string', 'uTGurjR8rS0y', NULL, 'Mot de passe par défaut'),
('defaultconnection', 'jid', 1, 'string', '0a0027000000@localhost', '0a0027000000@localhost', 'JID forcé'),
('defaultconnection', 'guacamole_baseurl', 1, 'string', 'http://hba.medulla-tech.io/guacamole/#/client/@@CUX_ID@@?username=root&password=42JZO9B3SV7Kx9V6csKJkz3pcVvtgvc31bCQXfWq', 'http://192.168.56.2/guacamole/', 'URL Guacamole par défaut'),
('defaultconnection', 'keyAES32', 1, 'string', 'ng4yUQpHvVZDnVstCSweMJOpcdgFwqP4', 'abcdefghijklmnopqrstuvwxyz012345', 'Clé AES 32 caractères'),
('browserfile', 'rootfilesystem', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Racine transfert de fichiers'),
('browserfile', 'defaultdir', 1, 'string', '/var/lib/pulse2/file-transfer', '/var/lib/pulse2/file-transfer', 'Répertoire par défaut transfert'),
('syncthing', 'announce_server', 1, 'string', 'https://sync-relay.siveo.net:8443/?id=CSI6OUD-VYW773R-J6I54Y7-NWHPXGJ-NDTWLPU-3G3MCAM-6FTYJJX-BRX62Q5', 'https://192.168.56.2:8443/?id=IGQIW2T-OHEFK3P-JHSB6KH-OHHYABS-YEWJRVC-M6F4NLZ-D6U55ES-VXIVMA3', 'Serveur d''annonce Syncthing'),
('grafana_api', 'api_key', 1, 'string', 'eyJrIjoiUjNMbzhBUFAzdHViV0ZPSlVxNFZzRjlvOW5wY21yb0IiLCJuIjoiYWRtaW5rZXkiLCJpZCI6MX0=', NULL, 'Clé API Grafana'),
('grafana_api', 'render_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/render/d-solo', 'http://192.168.56.2/grafana/render/d-solo', 'URL de rendu Grafana'),
('grafana_api', 'graph_url', 1, 'string', 'http://hba.medulla-tech.io/grafana/d-solo', 'http://192.168.56.2/grafana/d-solo', 'URL des graphiques Grafana'),
('computer_list', 'summary', 1, 'string', 'cn description os type user entity', 'cn description os type user entity', 'Colonnes liste machines'),
('computer_list', 'ordered', 1, 'booleen', '1', '1', 'Trier la liste des machines'),
('submaster', 'host', 1, 'string', '127.0.0.1', '127.0.0.1', 'Hôte du master substitut'),
('submaster', 'port', 1, 'entier', '57040', '57040', 'Port du master substitut'),
('submaster', 'ip_format', 1, 'string', 'ipv4', 'ipv4', 'Format IP utilisé'),
('submaster', 'allowed_token', 1, 'string', '4O&vHYKG3Cqq3RCUJu!vnQu+dBGwDkpZ', '4O&vHYKG3Cqq3RCUJu!vnQu+dBGwDkpZ', 'Jeton autorisé pour le substitut'),
('submaster', 'check_hostname', 1, 'booleen', '1', '1', 'Vérifier le certificat du serveur')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


-- ====================================================================
-- KIOSK CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS kiosk_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_kiosk_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de gestion des parametres de configuration Kiosk pour Medulla';


INSERT INTO kiosk_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Desactiver le plugin Kiosk (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/var/tmp/mmc-kiosk', '/var/tmp/mmc-kiosk', 'Repertoire temporaire du plugin'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees'),
('database', 'dbname', 1, 'string', 'kiosk', 'kiosk', 'Nom de la base de donnees Kiosk'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de base de donnees'),
('provider', 'use_external_ldap', 1, 'booleen', '0', '0', 'Utiliser un LDAP externe pour la recherche d''OU'),
('display', 'enable_acknowledgements', 1, 'booleen', '0', '0', 'Activer ou desactiver la fonction d''accuse de reception')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


CREATE TABLE IF NOT EXISTS kiosk_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_kiosk_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de versionnage des parametres de configuration Kiosk pour Medulla';


INSERT INTO kiosk_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Desactiver le plugin Kiosk (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/var/tmp/mmc-kiosk', '/var/tmp/mmc-kiosk', 'Repertoire temporaire du plugin'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees'),
('database', 'dbname', 1, 'string', 'kiosk', 'kiosk', 'Nom de la base de donnees Kiosk'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de base de donnees'),
('provider', 'use_external_ldap', 1, 'booleen', '0', '0', 'Utiliser un LDAP externe pour la recherche d''OU'),
('display', 'enable_acknowledgements', 1, 'booleen', '0', '0', 'Activer ou desactiver la fonction d''accuse de reception')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- MEDULLA SERVER CONF
-- ====================================================================

CREATE TABLE IF NOT EXISTS medulla_server_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_medulla_server_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de gestion des parametres de configuration Medulla Server pour Medulla';


INSERT INTO medulla_server_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Desactiver le serveur Medulla (0=actif, 1=inactif)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees (mysql, postgresql, etc.)'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees Medulla'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees Medulla'),
('database', 'dbname', 1, 'string', 'pulse2', 'pulse2', 'Nom de la base de donnees Medulla'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees Medulla'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de donnees Medulla (format: {scheme}value)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


CREATE TABLE IF NOT EXISTS medulla_server_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_medulla_server_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de versionnage des parametres de configuration Medulla Server pour Medulla';


INSERT INTO medulla_server_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Desactiver le serveur Medulla (0=actif, 1=inactif)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees (mysql, postgresql, etc.)'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees Medulla'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees Medulla'),
('database', 'dbname', 1, 'string', 'pulse2', 'pulse2', 'Nom de la base de donnees Medulla'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees Medulla'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de donnees Medulla (format: {scheme}value)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- MSC CONF
-- ====================================================================

CREATE TABLE IF NOT EXISTS msc_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_msc_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de gestion des parametres de configuration MSC pour Medulla';


INSERT INTO msc_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Desactiver le module MSC (0=actif, 1=inactif)'),
('msc', 'repopath', 1, 'string', '/var/lib/pulse2/packages', '/var/lib/pulse2/packages', 'Repertoire des packages MSC'),
('msc', 'qactionspath', 1, 'string', '/var/lib/pulse2/qactions', '/var/lib/pulse2/qactions', 'Repertoire des qactions'),
('msc', 'download_directory_path', 1, 'string', '/var/lib/pulse2/downloads', '/var/lib/pulse2/downloads', 'Repertoire de telechargement MSC'),
('msc', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees (mysql, postgresql, etc.)'),
('msc', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees MSC'),
('msc', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees MSC'),
('msc', 'dbname', 1, 'string', 'msc', 'msc', 'Nom de la base de donnees MSC'),
('msc', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees MSC'),
('msc', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de donnees MSC (format: {scheme}value)'),
('msc', 'default_scheduler', 1, 'string', 'scheduler_01', 'scheduler_01', 'Scheduler par defaut pour MSC'),
('scheduler_api', 'host', 1, 'string', '127.0.0.1', '127.0.0.1', 'Hote API scheduler'),
('scheduler_api', 'port', 1, 'entier', '9990', '9990', 'Port API scheduler'),
('scheduler_api', 'username', 1, 'string', '', '', 'Utilisateur API scheduler'),
('scheduler_api', 'password', 1, 'string', '', '', 'Mot de passe API scheduler'),
('scheduler_api', 'enablessl', 1, 'booleen', '1', '1', 'Activer SSL pour API scheduler'),
('scheduler_01', 'host', 1, 'string', '127.0.0.1', '127.0.0.1', 'Hote du scheduler_01'),
('scheduler_01', 'port', 1, 'entier', '8000', '8000', 'Port du scheduler_01'),
('scheduler_01', 'username', 1, 'string', 'username', 'username', 'Utilisateur scheduler_01'),
('scheduler_01', 'password', 1, 'string', 'password', 'password', 'Mot de passe scheduler_01'),
('scheduler_01', 'enablessl', 1, 'booleen', '1', '1', 'Activer SSL pour scheduler_01'),
('web', 'vnc_show_icon', 1, 'booleen', '1', '1', 'Afficher icone VNC'),
('web', 'vnc_view_only', 1, 'booleen', '0', '0', 'VNC en lecture seule pour l''interface web'),
('web', 'vnc_allow_user_control', 1, 'booleen', '1', '1', 'Autoriser controle VNC par utilisateur'),
('package_api', 'mserver', 1, 'string', '127.0.0.1', '127.0.0.1', 'Adresse du package server (mserver)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


CREATE TABLE IF NOT EXISTS msc_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_msc_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de versionnage des parametres de configuration MSC pour Medulla';


INSERT INTO msc_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Desactiver le module MSC (0=actif, 1=inactif)'),
('msc', 'repopath', 1, 'string', '/var/lib/pulse2/packages', '/var/lib/pulse2/packages', 'Repertoire des packages MSC'),
('msc', 'qactionspath', 1, 'string', '/var/lib/pulse2/qactions', '/var/lib/pulse2/qactions', 'Repertoire des qactions'),
('msc', 'download_directory_path', 1, 'string', '/var/lib/pulse2/downloads', '/var/lib/pulse2/downloads', 'Repertoire de telechargement MSC'),
('msc', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees (mysql, postgresql, etc.)'),
('msc', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees MSC'),
('msc', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees MSC'),
('msc', 'dbname', 1, 'string', 'msc', 'msc', 'Nom de la base de donnees MSC'),
('msc', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees MSC'),
('msc', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de donnees MSC (format: {scheme}value)'),
('msc', 'default_scheduler', 1, 'string', 'scheduler_01', 'scheduler_01', 'Scheduler par defaut pour MSC'),
('scheduler_api', 'host', 1, 'string', '127.0.0.1', '127.0.0.1', 'Hote API scheduler'),
('scheduler_api', 'port', 1, 'entier', '9990', '9990', 'Port API scheduler'),
('scheduler_api', 'username', 1, 'string', '', '', 'Utilisateur API scheduler'),
('scheduler_api', 'password', 1, 'string', '', '', 'Mot de passe API scheduler'),
('scheduler_api', 'enablessl', 1, 'booleen', '1', '1', 'Activer SSL pour API scheduler'),
('scheduler_01', 'host', 1, 'string', '127.0.0.1', '127.0.0.1', 'Hote du scheduler_01'),
('scheduler_01', 'port', 1, 'entier', '8000', '8000', 'Port du scheduler_01'),
('scheduler_01', 'username', 1, 'string', 'username', 'username', 'Utilisateur scheduler_01'),
('scheduler_01', 'password', 1, 'string', 'password', 'password', 'Mot de passe scheduler_01'),
('scheduler_01', 'enablessl', 1, 'booleen', '1', '1', 'Activer SSL pour scheduler_01'),
('web', 'vnc_show_icon', 1, 'booleen', '1', '1', 'Afficher icone VNC'),
('web', 'vnc_view_only', 1, 'booleen', '0', '0', 'VNC en lecture seule pour l''interface web'),
('web', 'vnc_allow_user_control', 1, 'booleen', '1', '1', 'Autoriser controle VNC par utilisateur'),
('package_api', 'mserver', 1, 'string', '127.0.0.1', '127.0.0.1', 'Adresse du package server (mserver)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


-- ====================================================================
-- MOBILE CONF
-- ====================================================================

CREATE TABLE IF NOT EXISTS mobile_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_mobile_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de gestion des parametres de configuration Mobile pour Medulla';


INSERT INTO mobile_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Desactiver le plugin Mobile (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-mobile', '/tmp/mmc-mobile', 'Repertoire temporaire du plugin mobile'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees'),
('database', 'dbname', 1, 'string', 'mobile', 'mobile', 'Nom de la base de donnees Mobile'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de donnees'),
('hmdm', 'url', 1, 'string', 'http://localhost/hmdm/rest', 'http://localhost/hmdm/rest', 'URL de l''API HMDM'),
('hmdm', 'login', 1, 'string', 'admin', 'admin', 'Login pour l''API HMDM'),
('hmdm', 'password', 1, 'string', 'admin', NULL, 'Mot de passe pour l''API HMDM')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);


CREATE TABLE IF NOT EXISTS mobile_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du parametre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du parametre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le parametre est actif (TRUE par defaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du parametre, utilise pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectee au parametre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par defaut utilisee si le parametre est desactive',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du parametre (usage, format, exemples)',

    CONSTRAINT uc_mobile_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicite du parametre par section'
)
COMMENT='Table de versionnage des parametres de configuration Mobile pour Medulla';


INSERT INTO mobile_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Desactiver le plugin Mobile (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-mobile', '/tmp/mmc-mobile', 'Repertoire temporaire du plugin mobile'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de donnees'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hote du serveur de base de donnees'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de donnees'),
('database', 'dbname', 1, 'string', 'mobile', 'mobile', 'Nom de la base de donnees Mobile'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de donnees'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de donnees'),
('hmdm', 'url', 1, 'string', 'http://localhost/hmdm/rest', 'http://localhost/hmdm/rest', 'URL de l''API HMDM'),
('hmdm', 'login', 1, 'string', 'admin', 'admin', 'Login pour l''API HMDM'),
('hmdm', 'password', 1, 'string', 'admin', NULL, 'Mot de passe pour l''API HMDM')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- MASTERING CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS mastering_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_mastering_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration Mastering pour Medulla';


INSERT INTO mastering_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '1', '0', 'Désactiver le plugin Mastering (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-mastering', '/tmp/mmc-mastering', 'Répertoire temporaire du plugin Mastering'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'mastering', 'mastering', 'Nom de la base de données Mastering'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS mastering_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_mastering_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration Mastering pour Medulla';


INSERT INTO mastering_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '1', '0', 'Désactiver le plugin Mastering (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-mastering', '/tmp/mmc-mastering', 'Répertoire temporaire du plugin Mastering'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'mastering', 'mastering', 'Nom de la base de données Mastering'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- URBACKUP CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS urbackup_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_urbackup_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration UrBackup pour Medulla';


INSERT INTO urbackup_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Désactiver le plugin UrBackup (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/var/tmp/mmc-urbackup', '/var/tmp/mmc-urbackup', 'Répertoire temporaire du plugin UrBackup'),
('urbackup', 'url', 1, 'string', 'http://127.0.0.1/urbackup/x', 'http://127.0.0.1/urbackup/x', 'URL de l''API UrBackup'),
('urbackup', 'username', 1, 'string', 'admin', 'admin', 'Nom d''utilisateur pour UrBackup'),
('urbackup', 'password', 1, 'string', 'M3dull4+HBA', NULL, 'Mot de passe pour UrBackup'),
('urbackup', 'usernameapi', 1, 'string', 'adminapi', 'adminapi', 'Nom d''utilisateur API pour UrBackup'),
('urbackup', 'passwordapi', 1, 'string', '32t6mRiljsfc', NULL, 'Mot de passe API pour UrBackup'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'urbackup', 'urbackup', 'Nom de la base de données UrBackup'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS urbackup_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_urbackup_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration UrBackup pour Medulla';


INSERT INTO urbackup_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Désactiver le plugin UrBackup (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/var/tmp/mmc-urbackup', '/var/tmp/mmc-urbackup', 'Répertoire temporaire du plugin UrBackup'),
('urbackup', 'url', 1, 'string', 'http://127.0.0.1/urbackup/x', 'http://127.0.0.1/urbackup/x', 'URL de l''API UrBackup'),
('urbackup', 'username', 1, 'string', 'admin', 'admin', 'Nom d''utilisateur pour UrBackup'),
('urbackup', 'password', 1, 'string', 'M3dull4+HBA', NULL, 'Mot de passe pour UrBackup'),
('urbackup', 'usernameapi', 1, 'string', 'adminapi', 'adminapi', 'Nom d''utilisateur API pour UrBackup'),
('urbackup', 'passwordapi', 1, 'string', '32t6mRiljsfc', NULL, 'Mot de passe API pour UrBackup'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'urbackup', 'urbackup', 'Nom de la base de données UrBackup'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- SECURITY CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS security_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_security_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration Security pour Medulla';


INSERT INTO security_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '1', '0', 'Désactiver le plugin Security (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-security', '/tmp/mmc-security', 'Répertoire temporaire du plugin Security'),
('main', 'log_level', 1, 'string', 'INFO', 'INFO', 'Niveau de journalisation (DEBUG, INFO, WARNING, ERROR, CRITICAL)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'security', 'security', 'Nom de la base de données Security'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('cve_central', 'url', 1, 'string', '', 'https://cve-central.example.com', 'URL du serveur CVE Central'),
('cve_central', 'server_id', 1, 'string', '', NULL, 'ID du serveur enregistré sur CVE Central'),
('cve_central', 'keyAES32', 1, 'string', '', NULL, 'Clé AES-256 (32 caractères)'),
('display', 'min_cvss', 1, 'decimal', '0.0', '0.0', 'Score CVSS minimum à afficher (0.0-10.0)'),
('display', 'min_severity', 1, 'string', 'None', 'None', 'Sévérité minimum à afficher (None, Low, Medium, High, Critical)'),
('display', 'show_patched', 1, 'booleen', '1', '1', 'Afficher les CVE avec correctifs disponibles (0=non, 1=oui)'),
('display', 'max_age_days', 1, 'entier', '0', '0', 'Âge maximum des CVE en jours (0 = pas de limite)'),
('display', 'min_published_year', 1, 'entier', '2000', '2000', 'Ignorer les CVE publiées avant cette année'),
('exclusions', 'vendors', 1, 'string', '', NULL, 'Vendeurs à exclure (séparés par virgules, insensible à la casse)'),
('exclusions', 'names', 1, 'string', '', NULL, 'Noms de logiciels exacts à exclure (séparés par virgules)'),
('exclusions', 'cve_ids', 1, 'string', '', NULL, 'IDs CVE spécifiques à exclure (séparés par virgules)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS security_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_security_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration Security pour Medulla';


INSERT INTO security_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '1', '0', 'Désactiver le plugin Security (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-security', '/tmp/mmc-security', 'Répertoire temporaire du plugin Security'),
('main', 'log_level', 1, 'string', 'INFO', 'INFO', 'Niveau de journalisation (DEBUG, INFO, WARNING, ERROR, CRITICAL)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'security', 'security', 'Nom de la base de données Security'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('cve_central', 'url', 1, 'string', '', 'https://cve-central.example.com', 'URL du serveur CVE Central'),
('cve_central', 'server_id', 1, 'string', '', NULL, 'ID du serveur enregistré sur CVE Central'),
('cve_central', 'keyAES32', 1, 'string', '', NULL, 'Clé AES-256 (32 caractères)'),
('display', 'min_cvss', 1, 'decimal', '0.0', '0.0', 'Score CVSS minimum à afficher (0.0-10.0)'),
('display', 'min_severity', 1, 'string', 'None', 'None', 'Sévérité minimum à afficher (None, Low, Medium, High, Critical)'),
('display', 'show_patched', 1, 'booleen', '1', '1', 'Afficher les CVE avec correctifs disponibles (0=non, 1=oui)'),
('display', 'max_age_days', 1, 'entier', '0', '0', 'Âge maximum des CVE en jours (0 = pas de limite)'),
('display', 'min_published_year', 1, 'entier', '2000', '2000', 'Ignorer les CVE publiées avant cette année'),
('exclusions', 'vendors', 1, 'string', '', NULL, 'Vendeurs à exclure (séparés par virgules, insensible à la casse)'),
('exclusions', 'names', 1, 'string', '', NULL, 'Noms de logiciels exacts à exclure (séparés par virgules)'),
('exclusions', 'cve_ids', 1, 'string', '', NULL, 'IDs CVE spécifiques à exclure (séparés par virgules)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- IMAGING CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS imaging_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_imaging_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration Imaging pour Medulla';


INSERT INTO imaging_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Désactiver le plugin Imaging (0=actif, 1=inactif)'),
('main', 'purge_interval', 0, 'string', '23 0 * * 0', '23 0 * * 0', 'Intervalle de purge (cron) — paramètre commenté par défaut'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'imaging', 'imaging', 'Nom de la base de données Imaging'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (0=non, 1=oui)'),
('database', 'dbsslca', 0, 'string', '/etc/mmc/pulse2/imaging/cacert.pem', '/etc/mmc/pulse2/imaging/cacert.pem', 'Chemin vers le certificat CA SSL'),
('database', 'dbsslcert', 0, 'string', '/etc/mmc/pulse2/imaging/cert.pem', '/etc/mmc/pulse2/imaging/cert.pem', 'Chemin vers le certificat client SSL'),
('database', 'dbsslkey', 0, 'string', '/etc/mmc/pulse2/imaging/key.pem', '/etc/mmc/pulse2/imaging/key.pem', 'Chemin vers la clé privée SSL'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de vie des connexions (dbpoolrecycle)'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool de connexions (dbpoolsize)'),
('web', 'web_def_date_fmt', 0, 'string', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', 'Format de date par défaut pour l''interface web'),
('web', 'web_def_default_menu_name', 0, 'string', 'Menu', 'Menu', 'Nom du menu par défaut'),
('web', 'web_def_default_timeout', 0, 'entier', '60', '60', 'Timeout par défaut de l''interface web (secondes)'),
('web', 'web_def_default_hidden_menu', 0, 'booleen', '0', '0', 'Masquer le menu par défaut (0=non, 1=oui)'),
('web', 'web_def_default_background_uri', 0, 'string', NULL, NULL, 'URI de fond par défaut (commenté)'),
('web', 'web_def_default_message', 0, 'string', 'Warning ! Your PC is being backed up or restored. Do not reboot !', 'Warning ! Your PC is being backed up or restored. Do not reboot !', 'Message d''avertissement par défaut'),
('web', 'web_def_kernel_parameters', 0, 'string', 'quiet', 'quiet', 'Paramètres noyau par défaut'),
('web', 'web_def_image_parameters', 0, 'string', NULL, NULL, 'Paramètres d''image par défaut (commenté)'),
('web', 'web_def_image_hidden', 0, 'booleen', '1', '1', 'Masquer les images par défaut (0=non, 1=oui)'),
('web', 'web_def_image_hidden_WOL', 0, 'booleen', '0', '0', 'Masquer les images WOL par défaut'),
('web', 'web_def_image_default', 0, 'booleen', '0', '0', 'Image par défaut (0=non, 1=oui)'),
('web', 'web_def_image_default_WOL', 0, 'booleen', '0', '0', 'Image WOL par défaut (0=non, 1=oui)'),
('web', 'web_def_service_hidden', 0, 'booleen', '1', '1', 'Masquer les services par défaut'),
('web', 'web_def_service_hidden_WOL', 0, 'booleen', '0', '0', 'Masquer les services WOL par défaut'),
('web', 'web_def_service_default', 0, 'booleen', '0', '0', 'Service par défaut (0=non, 1=oui)'),
('web', 'web_def_service_default_WOL', 0, 'booleen', '0', '0', 'Service WOL par défaut (0=non, 1=oui)'),
('network', 'resolv_order', 0, 'string', 'ip netbios dns fqdn hosts', 'ip netbios dns fqdn hosts', 'Ordre des méthodes de résolution'),
('network', 'preferred_network', 0, 'string', NULL, NULL, 'Réseaux préférés (format ip/netmask)'),
('network', 'netbios_path', 0, 'string', '/usr/bin/nmblookup', '/usr/bin/nmblookup', 'Chemin vers nmblookup')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS imaging_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_imaging_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration Imaging pour Medulla';


INSERT INTO imaging_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Désactiver le plugin Imaging (0=actif, 1=inactif)'),
('main', 'purge_interval', 0, 'string', '23 0 * * 0', '23 0 * * 0', 'Intervalle de purge (cron) — paramètre commenté par défaut'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'imaging', 'imaging', 'Nom de la base de données Imaging'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (0=non, 1=oui)'),
('database', 'dbsslca', 0, 'string', '/etc/mmc/pulse2/imaging/cacert.pem', '/etc/mmc/pulse2/imaging/cacert.pem', 'Chemin vers le certificat CA SSL'),
('database', 'dbsslcert', 0, 'string', '/etc/mmc/pulse2/imaging/cert.pem', '/etc/mmc/pulse2/imaging/cert.pem', 'Chemin vers le certificat client SSL'),
('database', 'dbsslkey', 0, 'string', '/etc/mmc/pulse2/imaging/key.pem', '/etc/mmc/pulse2/imaging/key.pem', 'Chemin vers la clé privée SSL'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de vie des connexions (dbpoolrecycle)'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool de connexions (dbpoolsize)'),
('web', 'web_def_date_fmt', 0, 'string', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', 'Format de date par défaut pour l''interface web'),
('web', 'web_def_default_menu_name', 0, 'string', 'Menu', 'Menu', 'Nom du menu par défaut'),
('web', 'web_def_default_timeout', 0, 'entier', '60', '60', 'Timeout par défaut de l''interface web (secondes)'),
('web', 'web_def_default_hidden_menu', 0, 'booleen', '0', '0', 'Masquer le menu par défaut (0=non, 1=oui)'),
('web', 'web_def_default_background_uri', 0, 'string', NULL, NULL, 'URI de fond par défaut (commenté)'),
('web', 'web_def_default_message', 0, 'string', 'Warning ! Your PC is being backed up or restored. Do not reboot !', 'Warning ! Your PC is being backed up or restored. Do not reboot !', 'Message d''avertissement par défaut'),
('web', 'web_def_kernel_parameters', 0, 'string', 'quiet', 'quiet', 'Paramètres noyau par défaut'),
('web', 'web_def_image_parameters', 0, 'string', NULL, NULL, 'Paramètres d''image par défaut (commenté)'),
('web', 'web_def_image_hidden', 0, 'booleen', '1', '1', 'Masquer les images par défaut (0=non, 1=oui)'),
('web', 'web_def_image_hidden_WOL', 0, 'booleen', '0', '0', 'Masquer les images WOL par défaut'),
('web', 'web_def_image_default', 0, 'booleen', '0', '0', 'Image par défaut (0=non, 1=oui)'),
('web', 'web_def_image_default_WOL', 0, 'booleen', '0', '0', 'Image WOL par défaut (0=non, 1=oui)'),
('web', 'web_def_service_hidden', 0, 'booleen', '1', '1', 'Masquer les services par défaut'),
('web', 'web_def_service_hidden_WOL', 0, 'booleen', '0', '0', 'Masquer les services WOL par défaut'),
('web', 'web_def_service_default', 0, 'booleen', '0', '0', 'Service par défaut (0=non, 1=oui)'),
('web', 'web_def_service_default_WOL', 0, 'booleen', '0', '0', 'Service WOL par défaut (0=non, 1=oui)'),
('network', 'resolv_order', 0, 'string', 'ip netbios dns fqdn hosts', 'ip netbios dns fqdn hosts', 'Ordre des méthodes de résolution'),
('network', 'preferred_network', 0, 'string', NULL, NULL, 'Réseaux préférés (format ip/netmask)'),
('network', 'netbios_path', 0, 'string', '/usr/bin/nmblookup', '/usr/bin/nmblookup', 'Chemin vers nmblookup')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- SUPPORT CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS support_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_support_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration Support pour Medulla';


INSERT INTO support_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin Support (0=actif, 1=inactif)'),
('main', 'pid_path', 0, 'string', '/var/run/pulse2/ssh_support', '/var/run/pulse2/ssh_support', 'Chemin du fichier PID (commenté par défaut)'),
('main', 'ssh_path', 0, 'string', '/usr/bin/ssh', '/usr/bin/ssh', 'Chemin vers l''exécutable ssh (commenté par défaut)'),
('main', 'support_url', 0, 'string', NULL, NULL, 'URL du service de support (commenté)'),
('main', 'support_user', 0, 'string', 'support', 'support', 'Utilisateur de support par défaut (commenté)'),
('main', 'identify_file', 0, 'string', '/etc/mmc/plugins/support/id_rsa', '/etc/mmc/plugins/support/id_rsa', 'Fichier d''identité SSH (clé privée, commenté)'),
('main', 'session_timeout', 0, 'entier', '7200', '7200', 'Timeout de session en secondes (commenté)'),
('main', 'license_server_url', 0, 'string', NULL, NULL, 'URL du serveur de licence (commenté)'),
('main', 'install_id_path', 0, 'string', '/etc/pulse-licensing/installation_id', '/etc/pulse-licensing/installation_id', 'Chemin vers l''installation_id de licence (commenté)'),
('main', 'cron_search_for_updates', 0, 'string', '0 6 * * *', '0 6 * * *', 'Cron pour les vérifications quotidiennes de licence (commenté)'),
('main', 'license_tmp_file', 0, 'string', '/var/lib/mmc/pulse_license_info', '/var/lib/mmc/pulse_license_info', 'Fichier temporaire d''info licence (commenté)'),
('main', 'country', 0, 'string', 'FR', 'FR', 'Code pays par défaut (commenté)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS support_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_support_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration Support pour Medulla';


INSERT INTO support_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin Support (0=actif, 1=inactif)'),
('main', 'pid_path', 0, 'string', '/var/run/pulse2/ssh_support', '/var/run/pulse2/ssh_support', 'Chemin du fichier PID (commenté par défaut)'),
('main', 'ssh_path', 0, 'string', '/usr/bin/ssh', '/usr/bin/ssh', 'Chemin vers l''exécutable ssh (commenté par défaut)'),
('main', 'support_url', 0, 'string', NULL, NULL, 'URL du service de support (commenté)'),
('main', 'support_user', 0, 'string', 'support', 'support', 'Utilisateur de support par défaut (commenté)'),
('main', 'identify_file', 0, 'string', '/etc/mmc/plugins/support/id_rsa', '/etc/mmc/plugins/support/id_rsa', 'Fichier d''identité SSH (clé privée, commenté)'),
('main', 'session_timeout', 0, 'entier', '7200', '7200', 'Timeout de session en secondes (commenté)'),
('main', 'license_server_url', 0, 'string', NULL, NULL, 'URL du serveur de licence (commenté)'),
('main', 'install_id_path', 0, 'string', '/etc/pulse-licensing/installation_id', '/etc/pulse-licensing/installation_id', 'Chemin vers l''installation_id de licence (commenté)'),
('main', 'cron_search_for_updates', 0, 'string', '0 6 * * *', '0 6 * * *', 'Cron pour les vérifications quotidiennes de licence (commenté)'),
('main', 'license_tmp_file', 0, 'string', '/var/lib/mmc/pulse_license_info', '/var/lib/mmc/pulse_license_info', 'Fichier temporaire d''info licence (commenté)'),
('main', 'country', 0, 'string', 'FR', 'FR', 'Code pays par défaut (commenté)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- PKGS CONF
-- ====================================================================

CREATE TABLE IF NOT EXISTS pkgs_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_pkgs_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration PKGS pour Medulla';


INSERT INTO pkgs_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin PKGS (0=actif, 1=inactif)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'pkgs', 'pkgs', 'Nom de la base de données PKGS'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (commenté)'),
('database', 'dbsslca', 0, 'string', NULL, NULL, 'Chemin vers le CA SSL (commenté)'),
('database', 'dbsslcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat client SSL (commenté)'),
('database', 'dbsslkey', 0, 'string', NULL, NULL, 'Chemin vers la clé privée SSL (commenté)'),
('database', 'dbpooltimeout', 0, 'entier', '30', '30', 'Timeout du pool de connexions DB (commenté)'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de recyclage du pool DB (commenté)'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool DB (commenté)'),

('user_package_api', 'server', 1, 'string', 'localhost', 'localhost', 'Serveur de l''API user_package'),
('user_package_api', 'port', 1, 'entier', '9990', '9990', 'Port de l''API user_package'),
('user_package_api', 'mountpoint', 1, 'string', '/upaa', '/upaa', 'Point de montage de l''API user_package'),
('user_package_api', 'username', 1, 'string', NULL, NULL, 'Nom d''utilisateur pour l''API (vide)'),
('user_package_api', 'password', 1, 'string', NULL, NULL, 'Mot de passe pour l''API (vide)'),
('user_package_api', 'enablessl', 1, 'booleen', '1', '1', 'Activer SSL pour l''API user_package (0=non,1=oui)'),
('user_package_api', 'verifypeer', 0, 'booleen', '0', '0', 'Vérifier le pair SSL (commenté)'),
('user_package_api', 'cacert', 0, 'string', NULL, NULL, 'Chemin vers le CA pour l''API (commenté)'),
('user_package_api', 'localcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat local (commenté)'),
('user_package_api', 'tmp_dir', 0, 'string', '/tmp/pkgs_tmp', '/tmp/pkgs_tmp', 'Répertoire temporaire pour uploads (commenté)'),

('quick_deploy', 'max_size_stanza_xmpp', 0, 'entier', '1048576', '1048576', 'Taille maximale pour déploiements rapides (commenté)'),

('pkgs', 'centralizedmultiplesharing', 1, 'booleen', '1', '0', 'Activer le partage centralisé des paquets (override .ini.local)'),
('pkgs', 'movepackage', 0, 'booleen', '0', '0', 'Permettre le déplacement de paquets si l''utilisateur a les droits (commenté)'),

('integrity_checks', 'generate_hash', 0, 'booleen', '0', '0', 'Générer des hash pour vérification d''intégrité (commenté)'),
('integrity_checks', 'hashing_algo', 0, 'string', 'SHA256', 'SHA256', 'Algorithme de hachage (commenté)'),
('integrity_checks', 'keyAES32', 0, 'string', 'abcdefghijklnmopqrstuvwxyz012345', 'abcdefghijklnmopqrstuvwxyz012345', 'Clé AES-256 d''exemple (commenté)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS pkgs_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_pkgs_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration PKGS pour Medulla';


INSERT INTO pkgs_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin PKGS (0=actif, 1=inactif)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'pkgs', 'pkgs', 'Nom de la base de données PKGS'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (commenté)'),
('database', 'dbsslca', 0, 'string', NULL, NULL, 'Chemin vers le CA SSL (commenté)'),
('database', 'dbsslcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat client SSL (commenté)'),
('database', 'dbsslkey', 0, 'string', NULL, NULL, 'Chemin vers la clé privée SSL (commenté)'),
('database', 'dbpooltimeout', 0, 'entier', '30', '30', 'Timeout du pool de connexions DB (commenté)'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de recyclage du pool DB (commenté)'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool DB (commenté)'),

('user_package_api', 'server', 1, 'string', 'localhost', 'localhost', 'Serveur de l''API user_package'),
('user_package_api', 'port', 1, 'entier', '9990', '9990', 'Port de l''API user_package'),
('user_package_api', 'mountpoint', 1, 'string', '/upaa', '/upaa', 'Point de montage de l''API user_package'),
('user_package_api', 'username', 1, 'string', NULL, NULL, 'Nom d''utilisateur pour l''API (vide)'),
('user_package_api', 'password', 1, 'string', NULL, NULL, 'Mot de passe pour l''API (vide)'),
('user_package_api', 'enablessl', 1, 'booleen', '1', '1', 'Activer SSL pour l''API user_package (0=non,1=oui)'),
('user_package_api', 'verifypeer', 0, 'booleen', '0', '0', 'Vérifier le pair SSL (commenté)'),
('user_package_api', 'cacert', 0, 'string', NULL, NULL, 'Chemin vers le CA pour l''API (commenté)'),
('user_package_api', 'localcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat local (commenté)'),
('user_package_api', 'tmp_dir', 0, 'string', '/tmp/pkgs_tmp', '/tmp/pkgs_tmp', 'Répertoire temporaire pour uploads (commenté)'),

('quick_deploy', 'max_size_stanza_xmpp', 0, 'entier', '1048576', '1048576', 'Taille maximale pour déploiements rapides (commenté)'),

('pkgs', 'centralizedmultiplesharing', 1, 'booleen', '1', '0', 'Activer le partage centralisé des paquets (valeur de .ini.local)'),
('pkgs', 'movepackage', 0, 'booleen', '0', '0', 'Permettre le déplacement de paquets si l''utilisateur a les droits (commenté)'),

('integrity_checks', 'generate_hash', 0, 'booleen', '0', '0', 'Générer des hash pour vérification d''intégrité (commenté)'),
('integrity_checks', 'hashing_algo', 0, 'string', 'SHA256', 'SHA256', 'Algorithme de hachage (commenté)'),
('integrity_checks', 'keyAES32', 0, 'string', 'abcdefghijklnmopqrstuvwxyz012345', 'abcdefghijklnmopqrstuvwxyz012345', 'Clé AES-256 d''exemple (commenté)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- DYN GROUP CONF 
-- ====================================================================

CREATE TABLE IF NOT EXISTS dyngroup_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_dyngroup_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration Dyngroup pour Medulla';


INSERT INTO dyngroup_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin Dyngroup (0=actif, 1=inactif)'),
('main', 'dynamic_enable', 1, 'booleen', '1', '1', 'Activer les groupes dynamiques (0=non, 1=oui)'),
('main', 'profiles_enable', 0, 'booleen', '1', '1', 'Activer les profils (imaging sur groupe) — commenté par défaut'),
('main', 'default_module', 0, 'string', NULL, NULL, 'Module pré‑sélectionné pour la création de groupes dynamiques (commenté)'),
('main', 'max_elements_for_static_list', 0, 'entier', '2000', '2000', 'Nombre maximum d''éléments pour la liste statique (commenté)'),
('main', 'check_db_enable', 0, 'booleen', '0', '0', 'Activer la boucle de vérification DB (commenté; False=0)'),
('main', 'check_db_interval', 0, 'entier', '300', '300', 'Intervalle de vérification DB en secondes (commenté)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'dyngroup', 'dyngroup', 'Nom de la base de données Dyngroup'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (commenté)'),
('database', 'dbsslca', 0, 'string', NULL, NULL, 'Chemin vers le CA SSL (commenté)'),
('database', 'dbsslcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat client SSL (commenté)'),
('database', 'dbsslkey', 0, 'string', NULL, NULL, 'Chemin vers la clé privée SSL (commenté)'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de vie des connexions (dbpoolrecycle) — commenté'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool de connexions (dbpoolsize) — commenté'),
('querymanager', 'activate', 1, 'booleen', '1', '1', 'Autoriser les requêtes sur les noms de groupe (0=non,1=oui)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS dyngroup_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_dyngroup_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration Dyngroup pour Medulla';


INSERT INTO dyngroup_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin Dyngroup (0=actif, 1=inactif)'),
('main', 'dynamic_enable', 1, 'booleen', '1', '1', 'Activer les groupes dynamiques (0=non, 1=oui)'),
('main', 'profiles_enable', 0, 'booleen', '1', '1', 'Activer les profils (imaging sur groupe) — commenté par défaut'),
('main', 'default_module', 0, 'string', NULL, NULL, 'Module pré‑sélectionné pour la création de groupes dynamiques (commenté)'),
('main', 'max_elements_for_static_list', 0, 'entier', '2000', '2000', 'Nombre maximum d''éléments pour la liste statique (commenté)'),
('main', 'check_db_enable', 0, 'booleen', '0', '0', 'Activer la boucle de vérification DB (commenté; False=0)'),
('main', 'check_db_interval', 0, 'entier', '300', '300', 'Intervalle de vérification DB en secondes (commenté)'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'dyngroup', 'dyngroup', 'Nom de la base de données Dyngroup'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (commenté)'),
('database', 'dbsslca', 0, 'string', NULL, NULL, 'Chemin vers le CA SSL (commenté)'),
('database', 'dbsslcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat client SSL (commenté)'),
('database', 'dbsslkey', 0, 'string', NULL, NULL, 'Chemin vers la clé privée SSL (commenté)'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de vie des connexions (dbpoolrecycle) — commenté'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool de connexions (dbpoolsize) — commenté'),
('querymanager', 'activate', 1, 'booleen', '1', '1', 'Autoriser les requêtes sur les noms de groupe (0=non,1=oui)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- UPDATES CONF
-- ====================================================================

CREATE TABLE IF NOT EXISTS updates_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_updates_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration Updates pour Medulla';


INSERT INTO updates_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Désactiver le plugin Updates (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-updates', '/tmp/mmc-updates', 'Répertoire temporaire du plugin Updates'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'updates', 'updates', 'Nom de la base de données Updates'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (commenté)'),
('database', 'dbsslca', 0, 'string', NULL, NULL, 'Chemin vers le CA SSL (commenté)'),
('database', 'dbsslcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat client SSL (commenté)'),
('database', 'dbsslkey', 0, 'string', NULL, NULL, 'Chemin vers la clé privée SSL (commenté)'),
('database', 'dbpooltimeout', 0, 'entier', '30', '30', 'Timeout du pool de connexions DB (commenté)'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de recyclage du pool DB (commenté)'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool DB (commenté)'),
('products', 'families', 1, 'string', 'Win10, Win11', 'Vstudio, Win10, Win11, Win_Malicious, office', 'Familles de produits à gérer (valeur effective : .ini.local)'),
('products', 'Vstudio_versions', 1, 'string', '2005, 2008, 2010, 2012, 2013, 2015, 2017, 2019, 2022', '2005, 2008, 2010, 2012, 2013, 2015, 2017, 2019, 2022', 'Versions Vstudio'),
('products', 'Win10_versions', 1, 'string', 'X64_21H2, X64_22H2', 'X64_1903, X64_21H1, X64_21H2, X64_22H2', 'Versions Win10 (valeur effective : .ini.local)'),
('products', 'Win11_versions', 1, 'string', 'X64', 'X64', 'Versions Win11'),
('products', 'Win_Malicious_versions', 1, 'string', 'X64', 'X64', 'Versions Win_Malicious'),
('products', 'office_versions', 1, 'string', '2003_64bit, 2007_64bit, 2010_64bit, 2013_64bit, 2016_64bit', '2003_64bit, 2007_64bit, 2010_64bit, 2013_64bit, 2016_64bit', 'Versions Office')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS updates_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_updates_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration Updates pour Medulla';


INSERT INTO updates_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '1', 'Désactiver le plugin Updates (0=actif, 1=inactif)'),
('main', 'tempdir', 1, 'string', '/tmp/mmc-updates', '/tmp/mmc-updates', 'Répertoire temporaire du plugin Updates'),
('database', 'dbdriver', 1, 'string', 'mysql', 'mysql', 'Driver de base de données'),
('database', 'dbhost', 1, 'string', 'localhost', 'localhost', 'Hôte du serveur de base de données'),
('database', 'dbport', 1, 'entier', '3306', '3306', 'Port du serveur de base de données'),
('database', 'dbname', 1, 'string', 'updates', 'updates', 'Nom de la base de données Updates'),
('database', 'dbuser', 1, 'string', 'mmc', 'mmc', 'Utilisateur de base de données'),
('database', 'dbpasswd', 1, 'string', 'pBWfpjErqtsU', NULL, 'Mot de passe de la base de données'),
('database', 'dbsslenable', 0, 'booleen', '0', '0', 'Activer SSL pour la connexion à la base de données (commenté)'),
('database', 'dbsslca', 0, 'string', NULL, NULL, 'Chemin vers le CA SSL (commenté)'),
('database', 'dbsslcert', 0, 'string', NULL, NULL, 'Chemin vers le certificat client SSL (commenté)'),
('database', 'dbsslkey', 0, 'string', NULL, NULL, 'Chemin vers la clé privée SSL (commenté)'),
('database', 'dbpooltimeout', 0, 'entier', '30', '30', 'Timeout du pool de connexions DB (commenté)'),
('database', 'dbpoolrecycle', 0, 'entier', '60', '60', 'Durée de recyclage du pool DB (commenté)'),
('database', 'dbpoolsize', 0, 'entier', '5', '5', 'Taille du pool DB (commenté)'),
('products', 'families', 1, 'string', 'Win10, Win11', 'Vstudio, Win10, Win11, Win_Malicious, office', 'Familles de produits à gérer (valeur effective : .ini.local)'),
('products', 'Vstudio_versions', 1, 'string', '2005, 2008, 2010, 2012, 2013, 2015, 2017, 2019, 2022', '2005, 2008, 2010, 2012, 2013, 2015, 2017, 2019, 2022', 'Versions Vstudio'),
('products', 'Win10_versions', 1, 'string', 'X64_21H2, X64_22H2', 'X64_1903, X64_21H1, X64_21H2, X64_22H2', 'Versions Win10 (valeur effective : .ini.local)'),
('products', 'Win11_versions', 1, 'string', 'X64', 'X64', 'Versions Win11'),
('products', 'Win_Malicious_versions', 1, 'string', 'X64', 'X64', 'Versions Win_Malicious'),
('products', 'office_versions', 1, 'string', '2003_64bit, 2007_64bit, 2010_64bit, 2013_64bit, 2016_64bit', '2003_64bit, 2007_64bit, 2010_64bit, 2013_64bit, 2016_64bit', 'Versions Office')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

-- ====================================================================
-- GUACAMOLE CONF
-- ====================================================================

CREATE TABLE IF NOT EXISTS guacamole_conf (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_guacamole_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de gestion des paramètres de configuration Guacamole pour Medulla';


INSERT INTO guacamole_conf (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin Guacamole (0=actif, 1=inactif)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

CREATE TABLE IF NOT EXISTS guacamole_conf_version (
    id INT AUTO_INCREMENT PRIMARY KEY
        COMMENT 'Identifiant unique du paramètre de configuration',

    section VARCHAR(50) NOT NULL
        COMMENT 'Section du fichier de configuration (ex : [main] devient "main")',

    nom VARCHAR(100) NOT NULL
        COMMENT 'Nom du paramètre, unique au sein de sa section',

    activer BOOLEAN NOT NULL DEFAULT TRUE
        COMMENT 'Indique si le paramètre est actif (TRUE par défaut)',

    type ENUM('string', 'booleen', 'entier', 'decimal', 'autre')
        NOT NULL DEFAULT 'string'
        COMMENT 'Type du paramètre, utilisé pour la validation et l''affichage',

    valeur TEXT
        COMMENT 'Valeur actuellement affectée au paramètre',

    valeur_defaut TEXT DEFAULT NULL
        COMMENT 'Valeur par défaut utilisée si le paramètre est désactivé',

    description TEXT NOT NULL
        COMMENT 'Description fonctionnelle obligatoire du paramètre (usage, format, exemples)',

    CONSTRAINT uc_guacamole_version_section_nom UNIQUE (section, nom)
        COMMENT 'Garantit l''unicité du paramètre par section'
)
COMMENT='Table de versionnage des paramètres de configuration Guacamole pour Medulla';


INSERT INTO guacamole_conf_version (section, nom, activer, type, valeur, valeur_defaut, description) VALUES
('main', 'disable', 1, 'booleen', '0', '0', 'Désactiver le plugin Guacamole (0=actif, 1=inactif)')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    type = VALUES(type),
    valeur = VALUES(valeur),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

UPDATE version SET Number = 7;

COMMIT;