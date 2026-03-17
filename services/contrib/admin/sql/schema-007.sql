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


UPDATE version SET Number = 7;

COMMIT;