--
--  (c) 2024-2025 Medulla, http://www.medulla-tech.io
--
--
-- This file is part of MMC, http://www.medulla-tech.io
--
-- MMC is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 3 of the License, or
-- (at your option) any later version.
--
-- MMC is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with MMC; If not, see <http://www.gnu.org/licenses/.>

-- Ajout du paramètre glpi_crypt_key pour le déchiffrement des tokens GLPI 11
-- La clé doit être encodée en base64 (contenu de /usr/share/glpi/config/glpicrypt.key)
INSERT INTO saas_application (setting_name, setting_value, setting_description)
VALUES ('glpi_crypt_key', NULL, 'GLPI 11 sodium encryption key (base64)')
ON DUPLICATE KEY UPDATE setting_description = VALUES(setting_description);

UPDATE version SET Number = 8;

COMMIT;
