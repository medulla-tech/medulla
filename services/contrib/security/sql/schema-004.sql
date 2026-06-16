START TRANSACTION;

-- Schema 004: Add source_package column to software_cves table
-- Sur les distributions Linux, plusieurs paquets binaires (libfreerdp2-2,
-- libwinpr2-2, libfreerdp-server2-2) proviennent d'un meme paquet SOURCE
-- (freerdp2) et portent les memes CVE. On memorise le source pour regrouper
-- l'affichage (une ligne au lieu de N). NULL pour Windows (pas de paquet source).
ALTER TABLE `software_cves` ADD COLUMN `source_package` varchar(255) DEFAULT NULL COMMENT 'Paquet source distro Linux (ex: libfreerdp2-2 -> freerdp2), NULL pour Windows' AFTER `glpi_software_name`;

UPDATE `version` SET `Number` = 4;

COMMIT;
