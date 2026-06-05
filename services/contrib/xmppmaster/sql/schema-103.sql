--
-- (c) 2026, http://www.medulla-tech.io/
--
-- FILE contrib/xmppmaster/sql/schema-102.sql
-- =======================================
-- Database xmppmaster
-- =======================================
-- Redefinition de up_init_table_major_win_complet
-- Priorite GLPI pour l'entite/hostname et selection unique d'une ligne XMPP par machine inventaire.

START TRANSACTION;

USE `xmppmaster`;

DELIMITER $$

USE `xmppmaster`$$
DROP PROCEDURE IF EXISTS `up_init_table_major_win_complet`$$

USE `xmppmaster`$$
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_table_major_win_complet`$$

CREATE PROCEDURE `up_init_table_major_win_complet`()
BEGIN
    START TRANSACTION;

    DROP TABLE IF EXISTS up_major_win;

    CREATE TABLE up_major_win (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        xmpp_id INT UNSIGNED NOT NULL,
        glpi_id INT UNSIGNED NOT NULL,
        ent_id INT UNSIGNED NOT NULL,
        hostname VARCHAR(255),
        enabled TINYINT(1),
        jid VARCHAR(255),
        serial VARCHAR(255),
        platform VARCHAR(100),
        name VARCHAR(255),
        comment TEXT,
        entity VARCHAR(255),
        lang_code VARCHAR(10),
        iso_filename VARCHAR(255),
        package_uuid VARCHAR(255) NOT NULL,
        prefix VARCHAR(50),
        old_version VARCHAR(50),
        oldcode VARCHAR(50),
        isolang VARCHAR(10),
        internal_code VARCHAR(50),
        target_name VARCHAR(255),
        is_active VARCHAR(10),
        lang_version VARCHAR(50),
        new_version VARCHAR(50),
        newcode VARCHAR(50),
        PRIMARY KEY (id),
        INDEX idx_glpi_id (glpi_id),
        INDEX idx_ent_id (ent_id),
        INDEX idx_package_uuid (package_uuid)
    );

    INSERT IGNORE INTO up_major_win (
        xmpp_id, glpi_id, ent_id,
        hostname, enabled, jid, serial, platform,
        name, comment, entity,
        lang_code, iso_filename, package_uuid,
        prefix, old_version, oldcode, isolang,
        internal_code, target_name, is_active, lang_version,
        new_version, newcode
    )
    WITH parts AS (
        SELECT
            s.id AS soft_id,
            s.name AS fullname,
            SUBSTRING_INDEX(s.name, '@', 1) AS part1,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 2), '@', -1) AS part2,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 3), '@', -1) AS part3,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 4), '@', -1) AS part4,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 5), '@', -1) AS part5,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 6), '@', -1) AS part6,
            SUBSTRING_INDEX(SUBSTRING_INDEX(s.name, '@', 7), '@', -1) AS part7
        FROM xmppmaster.local_glpi_softwares s
        WHERE s.name LIKE 'Medulla\_%'
    ),
    mx_one AS (
        SELECT
            m1.id,
            m1.hostname,
            m1.enabled,
            m1.jid,
            m1.uuid_serial_machine,
            m1.platform,
            NULLIF(REPLACE(m1.uuid_inventorymachine, 'UUID', ''), '') AS glpi_machine_id
        FROM xmppmaster.machines m1
        INNER JOIN (
            SELECT
                mxn.glpi_machine_id,
                COALESCE(
                    NULLIF(MAX(CASE WHEN mxn.enabled = 1 THEN mxn.id ELSE 0 END), 0),
                    MAX(mxn.id)
                ) AS selected_id
            FROM (
                SELECT
                    id,
                    enabled,
                    NULLIF(REPLACE(uuid_inventorymachine, 'UUID', ''), '') AS glpi_machine_id
                FROM xmppmaster.machines
            ) mxn
            WHERE mxn.glpi_machine_id IS NOT NULL
              AND mxn.glpi_machine_id <> ''
            GROUP BY mxn.glpi_machine_id
        ) mx_pick ON mx_pick.selected_id = m1.id
    )
    SELECT
        mx.id AS xmpp_id,
        m.id AS glpi_id,
        COALESCE(e.id, m.entities_id) AS ent_id,
        COALESCE(NULLIF(m.name, ''), mx.hostname) AS hostname,
        mx.enabled,
        mx.jid,
        mx.uuid_serial_machine AS serial,
        mx.platform,
        parts.fullname AS name,
        s.comment,
        e.completename AS entity,
        lc.lang_code,
        lc.iso_filename,
        lc.package_uuid,
        SUBSTRING_INDEX(parts.part1, '_', 1) AS prefix,
        SUBSTRING_INDEX(parts.part1, '_', -1) AS old_version,
        parts.part2 AS oldcode,
        parts.part3 AS isolang,
        parts.part4 AS internal_code,
        parts.part5 AS target_name,
        parts.part6 AS is_active,
        parts.part7 AS lang_version,
        SUBSTRING_INDEX(parts.part7, '-', -1) AS new_version,
        SUBSTRING_INDEX(SUBSTRING_INDEX(parts.part5, '_', 2), '_', -1) AS newcode
    FROM xmppmaster.local_glpi_items_softwareversions si
    LEFT JOIN xmppmaster.local_glpi_softwareversions sv ON si.softwareversions_id = sv.id
    LEFT JOIN xmppmaster.local_glpi_machines m ON si.items_id = m.id
    LEFT JOIN xmppmaster.local_glpi_entities e ON e.id = m.entities_id
    LEFT JOIN xmppmaster.local_glpi_softwares s ON sv.softwares_id = s.id
    LEFT JOIN parts ON parts.soft_id = s.id
    INNER JOIN mx_one mx ON mx.glpi_machine_id = si.items_id
    LEFT JOIN xmppmaster.up_packages_major_Lang_code lc
        ON lc.lang_code = parts.part3
        AND lc.major = SUBSTRING_INDEX(parts.part7, '-', -1)
    WHERE s.name LIKE 'Medulla\_%';

    COMMIT;

    TRUNCATE TABLE up_machine_major_windows;

    INSERT INTO up_machine_major_windows (
        id_machine, update_id, kb, msrcseverity,
        glpi_id, ent_id, hostname, enabled, jid, serial,
        platform, is_active, name, comment, entity,
        lang_code, old_version, new_version, oldcode, newcode, isolang
    )
    SELECT
        xmpp_id,
        LEFT(COALESCE(package_uuid, ''), 36),
        LEFT(COALESCE(package_uuid, ''), 36),
        NULL,
        glpi_id,
        ent_id,
        hostname,
        enabled,
        jid,
        serial,
        platform,
        'True',
        name,
        comment,
        entity,
        lang_code,
        old_version,
        new_version,
        oldcode,
        newcode,
        isolang
    FROM up_major_win
    WHERE
        (
            TRIM(COALESCE(old_version, '')) = '11'
            AND TRIM(COALESCE(new_version, '')) = '11'
            AND UPPER(TRIM(COALESCE(oldcode, ''))) != UPPER(TRIM(COALESCE(newcode, ''))) 
            AND UPPER(TRIM(COALESCE(oldcode, ''))) != '26H1'  -- Exclusion de 26h1 tanque pas  26hx pas encore en iso
        )
        OR
        (
            TRIM(COALESCE(old_version, '')) = '10'
            AND TRIM(COALESCE(new_version, '')) = '11'
            AND UPPER(TRIM(COALESCE(is_active, ''))) = 'TRUE'
        );
END$$

DELIMITER ;

-- L'index unique rule_unique (msrcseverity, updateclassification), hérité de
-- schema-094, ignore entityid : il interdit la même règle sur deux entités et
-- fait planter up_genere_list_rule_entity pour toute entité autre que la racine.
-- uniq_entity_rule (entityid, msrcseverity, updateclassification) le remplace.
ALTER TABLE `xmppmaster`.`up_auto_approve_rules` DROP INDEX IF EXISTS `rule_unique`;

UPDATE version SET Number = 103;

commit;
