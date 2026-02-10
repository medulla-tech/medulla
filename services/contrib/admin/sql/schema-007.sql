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

UPDATE version SET Number = 7;

COMMIT;