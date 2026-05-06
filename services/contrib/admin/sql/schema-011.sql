SET NAMES utf8mb4;
START TRANSACTION;
USE admin;

-- Minimal storage for core web settings used by authentication.
CREATE TABLE IF NOT EXISTS mmc_conf (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section VARCHAR(50) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    activer BOOLEAN NOT NULL DEFAULT TRUE,
    valeur TEXT,
    valeur_defaut TEXT DEFAULT NULL,
    description TEXT NOT NULL,
    CONSTRAINT uc_mmc_section_nom UNIQUE (section, nom)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO mmc_conf (section, nom, activer, valeur, valeur_defaut, description)
VALUES ('global', 'magic_link_ttl_minutes', 1, '5', '5', 'Magic link expiration time in minutes')
ON DUPLICATE KEY UPDATE
    activer = VALUES(activer),
    valeur_defaut = VALUES(valeur_defaut),
    description = VALUES(description);

UPDATE version SET Number = 11;

COMMIT;