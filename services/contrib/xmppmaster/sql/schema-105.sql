--
-- (c) 2026, http://www.medulla-tech.io/
--
-- FILE contrib/xmppmaster/sql/schema-105.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- Correction du label partage entre deux statuts de deploiement.
--
-- Les regles 'ABORT ON TIMEOUT' et 'ABORT RESUMPTION ERROR' pointaient
-- toutes les deux sur le meme label interne 'abortontimeout'. Comme le
-- code (camembert et creation de groupe au clic) indexe ces regles par
-- label (le dernier ecrase le premier), la part "abortontimeout" etait
-- nommee a tort "Abort resumption error", et le clic filtrait les
-- machines sur le statut 'ABORT RESUMPTION ERROR' (absent en base, les
-- machines etant en 'ABORT ON TIMEOUT') -> groupe vide.
--
-- On donne un label propre a 'ABORT RESUMPTION ERROR' pour separer les
-- deux cas : l'affichage redevient correct et le clic cree le groupe
-- avec les bonnes machines.

START TRANSACTION;

USE `xmppmaster`;

UPDATE `def_remote_deploy_status`
SET `label` = 'abortresumptionerror'
WHERE `status` = 'ABORT RESUMPTION ERROR'
  AND `label`  = 'abortontimeout';


-- 1. Table des CVE
CREATE TABLE IF NOT EXISTS up_cve_linux (
    id INT(11) NOT NULL AUTO_INCREMENT,
    cve VARCHAR(32) NOT NULL,
    severity INT(11),
    description VARCHAR(128),
    PRIMARY KEY (id),
    UNIQUE KEY (cve)
) ENGINE=InnoDB;


-- 2. Table des packages
CREATE TABLE IF NOT EXISTS  up_package_linux (
    id INT(11) NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(255),
    PRIMARY KEY (id),
    UNIQUE KEY (name, version)
) ENGINE=InnoDB;


-- 3. Table de jointure entre CVE et packages
CREATE TABLE IF NOT EXISTS up_package_cve_linux (
    package_id INT(11) NOT NULL,
    cve_id INT(11) NOT NULL,
    PRIMARY KEY (package_id, cve_id),
    FOREIGN KEY (package_id) REFERENCES up_package_linux(id) ON DELETE CASCADE,
    FOREIGN KEY (cve_id) REFERENCES up_cve_linux(id) ON DELETE CASCADE,
    INDEX idx_up_package_cve_linux_cve_package (cve_id, package_id)
) ENGINE=InnoDB;


-- 4. Table des machines
CREATE TABLE `up_machine_linux` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_id` int(11) NOT NULL,
  `harduuid` varchar(64) NOT NULL,
  `distributor_id` varchar(64) DEFAULT NULL,
  `description` varchar(128) DEFAULT NULL,
  `release_version` varchar(32) DEFAULT NULL,
  `codename` varchar(64) DEFAULT NULL,
  `kernel_version` varchar(64) DEFAULT '0',
  `security_count` int(11) DEFAULT 0,
  `security_require` tinyint(1) DEFAULT 0,
  `security_curent` tinyint(1) DEFAULT 0,
  `security_start` datetime DEFAULT NULL,
  `security_stop` datetime DEFAULT NULL,
  `security_login` varchar(64) DEFAULT '0',
  `security_interval` varchar(64) DEFAULT '0',
  `kernel_count` int(11) DEFAULT 0,
  `kernel_current` tinyint(1) DEFAULT 0,
  `kernel_start` datetime DEFAULT NULL,
  `kernel_stop` datetime DEFAULT NULL,
  `kernel_login` varchar(64) DEFAULT '0',
  `kernel_interval` varchar(64) DEFAULT '0',
  `other_count` int(11) DEFAULT 0,
  `other_require` tinyint(1) DEFAULT 0,
  `other_current` tinyint(1) DEFAULT 0,
  `other_start` datetime DEFAULT NULL,
  `other_stop` datetime DEFAULT NULL,
  `other_login` varchar(64) DEFAULT '0',
  `other_interval` varchar(64) DEFAULT '0',
  `total_count` int(11) DEFAULT 0,
  `last_scan` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `harduuid` (`harduuid`),
  KEY `idx_last_scan` (`last_scan`),
  KEY `idx_kernel_require` (`kernel_require`),
  KEY `idx_distributor_id` (`distributor_id`),
  KEY `idx_kernel_version` (`kernel_version`),
  KEY `idx_security_require` (`security_require`),
  KEY `idx_other_require` (`other_require`),
  KEY `idx_security_stop` (`security_stop`),
  KEY `idx_kernel_start` (`kernel_start`),
  KEY `idx_kernel_stop` (`kernel_stop`),
  KEY `idx_other_start` (`other_start`),
  KEY `idx_other_stop` (`other_stop`),
  KEY `idx_security_login` (`security_login`),
  KEY `idx_kernel_login` (`kernel_login`),
  KEY `idx_other_login` (`other_login`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- 4.bis Table de politique d'auto-update Linux par entite/distribution
-- Convention: les objets du domaine update sont prefixes par up_.
-- 1 ligne = 1 combinaison (entity_id, distributor_id).
-- S'applique a toutes les machines de cette entite/distribution.
CREATE TABLE IF NOT EXISTS up_entity_linux_auto_update_policy (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT 'PK technique de la policy',
    entity_id INT(11) NOT NULL COMMENT 'Identifiant de l entite GLPI/MMC',
    distributor_id VARCHAR(64) NOT NULL COMMENT 'Distribution Linux normalisee (debian, ubuntu, rhel, ...)',
    release_version VARCHAR(20) NOT NULL DEFAULT '' COMMENT 'Conserve pour compatibilite historique (non discriminant)',
    auto_update_kernel TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Intention auto-update kernel (non propagee en require automatiquement)',
    auto_update_security TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Active la propagation vers security_require',
    auto_update_other TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Active la propagation vers other_require',
    created_at DATETIME NOT NULL DEFAULT current_timestamp() COMMENT 'Date de creation de la ligne',
    updated_at DATETIME NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT 'Date de derniere modification',
    PRIMARY KEY (id),
    UNIQUE KEY uniq_entity_distributor (entity_id, distributor_id),
    KEY idx_entity_id (entity_id),
    KEY idx_distributor_id (distributor_id),
    KEY idx_release_version (release_version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
COMMENT='Politique auto-update Linux par entite et distribution';


-- Initialisation depuis les machines deja presentes (sans erreur sur doublons)
-- 1 ligne par combinaison unique (entity_id, distributor_id)
INSERT IGNORE INTO up_entity_linux_auto_update_policy (
    entity_id,
    distributor_id,
    release_version
)
SELECT DISTINCT
    upl.entity_id,
    LOWER(TRIM(upl.distributor_id)),
    ''
FROM up_machine_linux upl
WHERE upl.entity_id IS NOT NULL
  AND upl.distributor_id IS NOT NULL
  AND TRIM(upl.distributor_id) <> '';

-- Normalisation de compatibilite: 1 seule ligne par entity+distribution
-- 1) conserve uniquement la ligne la plus recente (id le plus eleve)
DELETE p_old
FROM up_entity_linux_auto_update_policy p_old
INNER JOIN up_entity_linux_auto_update_policy p_new
    ON p_old.entity_id = p_new.entity_id
   AND p_old.distributor_id = p_new.distributor_id
   AND p_old.id < p_new.id;

-- 2) force release_version a '' car non discriminante metier
UPDATE up_entity_linux_auto_update_policy
SET release_version = ''
WHERE release_version <> '';

-- Initialisation generique depuis les entites connues et le catalogue de distributions gerees
-- 1 ligne par couple (entity_id, distributor_id) avec release_version = ''
INSERT IGNORE INTO up_entity_linux_auto_update_policy (
    entity_id,
    distributor_id,
    release_version
)
SELECT
    ge.glpi_id,
    LOWER(TRIM(v.distributor_id)),
    ''
FROM glpi_entity ge
INNER JOIN (
    SELECT DISTINCT distributor_id
    FROM up_linux_os_versions
    WHERE is_managed = 1
      AND distributor_id IS NOT NULL
      AND TRIM(distributor_id) <> ''
) v
WHERE ge.glpi_id IS NOT NULL;


-- Synchronisation automatique a chaque nouvelle machine Linux
DROP TRIGGER IF EXISTS `xmppmaster`.`up_machine_linux_AFTER_INSERT`;
DELIMITER $$

-- Propagation immediate des changements de policy entite vers les machines Linux
DROP TRIGGER IF EXISTS `xmppmaster`.`up_entity_linux_auto_update_policy_AFTER_UPDATE`;
DELIMITER $$
CREATE TRIGGER `xmppmaster`.`up_entity_linux_auto_update_policy_AFTER_UPDATE`
AFTER UPDATE ON `xmppmaster`.`up_entity_linux_auto_update_policy`
FOR EACH ROW
BEGIN
    CALL up_apply_entity_linux_auto_update_policy(NEW.entity_id, NEW.distributor_id);
END$$
DELIMITER ;

-- Creation automatique des lignes policy Linux pour chaque nouvelle entite
DROP TRIGGER IF EXISTS `xmppmaster`.`glpi_entity_AFTER_INSERT_linux_auto_update_policy`;
DELIMITER $$
CREATE TRIGGER `xmppmaster`.`glpi_entity_AFTER_INSERT_linux_auto_update_policy`
AFTER INSERT ON `xmppmaster`.`glpi_entity`
FOR EACH ROW
BEGIN
    IF NEW.glpi_id IS NOT NULL THEN
        INSERT IGNORE INTO up_entity_linux_auto_update_policy (
            entity_id,
            distributor_id,
            release_version
        )
        SELECT
            NEW.glpi_id,
            LOWER(TRIM(v.distributor_id)),
            ''
        FROM (
            SELECT DISTINCT distributor_id
            FROM up_linux_os_versions
            WHERE is_managed = 1
              AND distributor_id IS NOT NULL
              AND TRIM(distributor_id) <> ''
        ) v;
    END IF;
END$$
DELIMITER ;
CREATE TRIGGER `xmppmaster`.`up_machine_linux_AFTER_INSERT`
AFTER INSERT ON `xmppmaster`.`up_machine_linux`
FOR EACH ROW
BEGIN
    IF NEW.entity_id IS NOT NULL
       AND NEW.distributor_id IS NOT NULL
       AND TRIM(NEW.distributor_id) <> '' THEN
        INSERT IGNORE INTO up_entity_linux_auto_update_policy (
            entity_id,
            distributor_id,
            release_version
        ) VALUES (
            NEW.entity_id,
            LOWER(TRIM(NEW.distributor_id)),
            ''
        );
    END IF;
END$$
DELIMITER ;


-- Procedure explicite: applique la policy entite/distribution sur les machines Linux
-- Cette propagation est volontairement procedural (pas de trigger UPDATE sur la table policy)
-- pour eviter des effets de bord et garder un controle explicite depuis l'UI/API.
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_apply_entity_linux_auto_update_policy`;
DELIMITER $$
CREATE PROCEDURE `xmppmaster`.`up_apply_entity_linux_auto_update_policy`(
    IN p_entity_id INT,
    IN p_distributor_id VARCHAR(64)
)
BEGIN
    -- Propage les flags kernel/security/other vers toutes les machines de l entite+distribution.
    UPDATE up_machine_linux uml
    INNER JOIN up_entity_linux_auto_update_policy p
        ON  p.entity_id = uml.entity_id
        AND p.distributor_id = LOWER(TRIM(uml.distributor_id))
    SET
        uml.kernel_require = CASE
            WHEN p.auto_update_kernel = 1 AND uml.kernel_count > 0 THEN 1
            ELSE 0
        END,
        uml.security_require = CASE
            WHEN p.auto_update_security = 1 AND uml.security_count > 0 THEN 1
            ELSE 0
        END,
        uml.other_require = CASE
            WHEN p.auto_update_other = 1 AND uml.other_count > 0 THEN 1
            ELSE 0
        END
    WHERE uml.entity_id = p_entity_id
      AND LOWER(TRIM(uml.distributor_id)) = LOWER(TRIM(p_distributor_id));

    -- 3) Fin de traitement: la procedure n ecrit pas dans la table policy,
    --    donc aucun risque de boucle trigger/procedure.
END$$
DELIMITER ;


-- 5. Table des mises à jour des machines
CREATE TABLE IF NOT EXISTS up_machine_update_linux (
    id INT(11) NOT NULL AUTO_INCREMENT,
    machine_id INT(11) NOT NULL,
    package_id INT(11) NOT NULL,
    type ENUM('security', 'kernel', 'other', 'normal') NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (machine_id) REFERENCES up_machine_linux(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES up_package_linux(id) ON DELETE CASCADE,
    INDEX idx_up_machine_update_linux_machine_package (machine_id, package_id),
    INDEX idx_up_machine_update_linux_package_machine (package_id, machine_id),
    INDEX idx_up_machine_update_linux_machine_type (machine_id, type)
) ENGINE=InnoDB;



DROP TABLE IF EXISTS up_linux_os_versions;

CREATE TABLE up_linux_os_versions (
    id INT NOT NULL AUTO_INCREMENT COMMENT 'Identifiant unique',

    distributor_id VARCHAR(64) NOT NULL COMMENT 'Distribution Linux normalisee (debian, ubuntu, rhel, ...)',
    release_version VARCHAR(20) NOT NULL COMMENT 'Version de la distribution',
    is_current_stable TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Compatibilite historique: non pilote par Approved Linux releases',
    is_recommended TINYINT(1) NOT NULL DEFAULT 0 COMMENT 'Version majeure la plus haute cible pour la mise a jour',

    end_vendor_support DATETIME DEFAULT NULL COMMENT 'Fin du support standard éditeur',
    end_extended_support DATETIME DEFAULT NULL COMMENT 'Fin du support étendu',

    description VARCHAR(255) DEFAULT NULL COMMENT 'Description',

    package VARCHAR(36) DEFAULT NULL,
    packagename VARCHAR(45) DEFAULT NULL,

    PRIMARY KEY (id),

    UNIQUE KEY uniq_distributor_release_version (
        distributor_id,
        release_version
    ),

    KEY idx_distributor_id (
        distributor_id
    ),
    KEY idx_release_version (
        release_version
    ),

    KEY idx_distribution_stable (
        distributor_id,
        is_current_stable
    ),

    KEY idx_distribution_recommended (
        distributor_id,
        is_recommended
    ),

    KEY idx_managed (
        is_managed
    ),

    KEY idx_vendor_support (
        end_vendor_support
    ),

    KEY idx_extended_support (
        end_extended_support
    )

) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_general_ci
COMMENT='Versions des systèmes d exploitation Linux';


-- UPSERT : preserve les ids existants pour ne pas casser les FK des tables dependantes
-- (up_entity_linux_approved_releases.release_id reference up_linux_os_versions.id)
INSERT IGNORE INTO up_linux_os_versions
(
 distributor_id,
 release_version,
 name,
 is_managed,
 is_current_stable,
 is_recommended,
 end_vendor_support,
 end_extended_support,
 description
)
VALUES

/* ==========================
   Debian
   ========================== */

('debian','13','Trixie',0,1,1,'2028-08-09','2035-06-30','Debian 13'),
('debian','12','Bookworm',0,0,0,'2026-06-10','2033-06-30','Debian 12'),
('debian','11','Bullseye',0,0,0,'2024-08-14','2031-06-30','Debian 11'),
('debian','10','Buster',0,0,0,'2022-09-10','2029-06-30','Debian 10'),
('debian','9','Stretch',0,0,0,'2020-07-18','2027-06-30','Debian 9'),
('debian','8','Jessie',0,0,0,'2018-06-01','2025-06-30','Debian 8'),

/* ==========================
   Ubuntu
   ========================== */

('ubuntu','26.04','Resolute Raccoon',0,1,1,'2031-05-31','2041-04-30','Ubuntu 26.04 LTS'),
('ubuntu','24.04','Noble Numbat',0,0,0,'2029-06-30','2039-04-30','Ubuntu 24.04 LTS'),
('ubuntu','22.04','Jammy Jellyfish',0,0,0,'2027-06-30','2037-04-30','Ubuntu 22.04 LTS'),
('ubuntu','20.04','Focal Fossa',0,0,0,'2025-05-31','2035-04-30','Ubuntu 20.04 LTS'),
('ubuntu','18.04','Bionic Beaver',0,0,0,'2023-05-31','2033-04-30','Ubuntu 18.04 LTS'),

/* ==========================
    Zorin OS
    ========================== */

('zorin','17','Zorin OS 17',0,1,1,'2029-06-30',NULL,'Zorin OS 17 (Ubuntu 22.04 base)'),
('zorin','16','Zorin OS 16',0,0,0,'2027-04-30',NULL,'Zorin OS 16 (Ubuntu 20.04 base)'),

/* ==========================
   Linux Mint
   ========================== */

('mint','22.3','Zena',0,1,1,'2029-04-30',NULL,'Linux Mint 22.3'),
('mint','22.2','Zara',0,0,0,'2029-04-30',NULL,'Linux Mint 22.2'),
('mint','22.1','Xia',0,0,0,'2029-04-30',NULL,'Linux Mint 22.1'),
('mint','22','Wilma',0,0,0,'2029-04-30',NULL,'Linux Mint 22'),
('mint','21.3','Virginia',0,0,0,'2027-04-30',NULL,'Linux Mint 21.3'),
('mint','21.2','Victoria',0,0,0,'2027-04-30',NULL,'Linux Mint 21.2'),
('mint','21.1','Vera',0,0,0,'2027-04-30',NULL,'Linux Mint 21.1'),
('mint','21','Vanessa',0,0,0,'2027-04-30',NULL,'Linux Mint 21'),

/* ==========================
   RHEL
   ========================== */

('rhel','10',NULL,0,1,1,'2035-05-31','2038-05-31','RHEL 10'),
('rhel','9',NULL,0,0,0,'2032-05-31','2035-05-31','RHEL 9'),
('rhel','8',NULL,0,0,0,'2029-05-31','2032-05-31','RHEL 8'),
('rhel','7',NULL,0,0,0,'2024-06-30','2028-06-30','RHEL 7'),
('rhel','6',NULL,0,0,0,'2020-11-30','2024-11-30','RHEL 6'),

/* ==========================
   AlmaLinux
   ========================== */

('almalinux','10',NULL,0,1,1,'2035-05-31','2038-05-31','AlmaLinux 10'),
('almalinux','9',NULL,0,0,0,'2032-05-31','2035-05-31','AlmaLinux 9'),
('almalinux','8',NULL,0,0,0,'2029-05-31','2032-05-31','AlmaLinux 8'),

/* ==========================
   Rocky Linux
   ========================== */

('rocky','10',NULL,0,1,1,'2035-05-31','2038-05-31','Rocky Linux 10'),
('rocky','9',NULL,0,0,0,'2032-05-31','2035-05-31','Rocky Linux 9'),
('rocky','8',NULL,0,0,0,'2029-05-31','2032-05-31','Rocky Linux 8'),

/* ==========================
   SUSE Linux Enterprise
   ========================== */

('suse','15.6','SLES 15 SP6',0,1,1,'2027-12-31','2034-12-31','SUSE Linux Enterprise Server 15 SP6'),
('suse','15.5','SLES 15 SP5',0,0,0,'2026-12-31','2033-12-31','SUSE Linux Enterprise Server 15 SP5'),
('suse','15.4','SLES 15 SP4',0,0,0,'2025-12-31','2032-12-31','SUSE Linux Enterprise Server 15 SP4'),

/* ==========================
   openSUSE
   ========================== */

('opensuse','15.6',NULL,0,1,1,'2026-12-31',NULL,'openSUSE Leap 15.6'),
('opensuse','15.5',NULL,0,0,0,'2025-12-31',NULL,'openSUSE Leap 15.5'),
('opensuse','15.4',NULL,0,0,0,'2024-12-31',NULL,'openSUSE Leap 15.4'),

/* ==========================
   Fedora
   ========================== */

('fedora','42',NULL,0,1,1,'2026-12-31',NULL,'Fedora 42'),
('fedora','41',NULL,0,0,0,'2025-12-31',NULL,'Fedora 41'),
('fedora','40',NULL,0,0,0,'2025-05-31',NULL,'Fedora 40'),
('fedora','39',NULL,0,0,0,'2024-12-31',NULL,'Fedora 39'),
('fedora','38',NULL,0,0,0,'2024-06-30',NULL,'Fedora 38')

ON DUPLICATE KEY UPDATE
    name                 = VALUES(name),
    is_managed           = VALUES(is_managed),
    is_current_stable    = VALUES(is_current_stable),
    is_recommended       = VALUES(is_recommended),
    end_vendor_support   = VALUES(end_vendor_support),
    end_extended_support = VALUES(end_extended_support),
    description          = VALUES(description);

-- ----------------------------------------------------------------------
-- Clarification des commentaires metier (base actuelle)
-- ----------------------------------------------------------------------
ALTER TABLE up_entity_linux_approved_releases
    MODIFY is_current_stable TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'Compatibilite historique: non pilote par Approved Linux releases',
    MODIFY is_recommended TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'Version majeure la plus haute cible pour la mise a jour';

ALTER TABLE up_linux_os_versions
    MODIFY is_current_stable TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'Compatibilite historique: non pilote par Approved Linux releases',
    MODIFY is_recommended TINYINT(1) NOT NULL DEFAULT 0
        COMMENT 'Version majeure la plus haute cible pour la mise a jour';

INSERT IGNORE INTO applicationconfig (`key`, `value`, `comment`, `context`, `module`, `enable`)
VALUES 
('linux_generic_package_uuid', 'dfd3b8dc-linuxupdategenericcommand_p', 'UUID du package Linux generic update (fallback)', 'linux', 'updates', 1),
('linux_generic_package_name', 'linux-update-generic-command', 'Nom du package Linux generic update', 'linux', 'updates', 1);



INSERT IGNORE INTO xmppmaster.up_linux_os_versions
(distributor_id, release_version, name, is_managed, is_current_stable, is_recommended, end_vendor_support, end_extended_support, description, package, packagename)
VALUES
('zorin', '17.3', 'Zorin OS 17.3', 1, 0,1, '2027-04-01 00:00:00', NULL, 'Zorin OS 17.3', NULL, NULL),
('zorin', '17.2', 'Zorin OS 17.2', 0, 0, 0, '2027-04-01 00:00:00', NULL, 'Zorin OS 17.2', NULL, NULL),
('zorin', '17.1', 'Zorin OS 17.1', 0, 0, 0, '2027-04-01 00:00:00', NULL, 'Zorin OS 17.1', NULL, NULL),
('zorin', '17', 'Zorin OS 17', 0, 0, 0, '2027-04-01 00:00:00', NULL, 'Zorin OS 17', NULL, NULL);

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 105;

commit;
