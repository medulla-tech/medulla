--
-- (c) 2012 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Medulla 2, http://medulla.mandriva.org
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

-- Update menu items for Davos and PXELINUX
UPDATE Internationalization SET label = 'Ajouter comme client Medulla' WHERE id = 5 AND fk_language = 2;
UPDATE Internationalization SET label = 'Registrar Cliente Medulla' WHERE id = 5 AND fk_language = 3;
UPDATE Internationalization SET label = 'Als Medulla-Medulla registrieren' WHERE id = 5 AND fk_language = 4;
UPDATE Internationalization SET label = 'Déployer les agents Medulla (SSH, OCS, VNC) au prochain redémarrage' WHERE id = 20 AND fk_language = 2;
UPDATE Internationalization SET label = 'Implantar Agentes Medulla (SSH, OCS e VNC) na proxima inicialização' WHERE id = 20 AND fk_language = 3;
UPDATE Internationalization SET label = 'Verteilen von Medulla-Agents (SSH, OCS, VNC) beim nächsten Neustart' WHERE id = 20 AND fk_language = 4;
UPDATE Internationalization SET label = 'Déployer les Agents Medulla' WHERE id = 30 AND fk_language = 2;
UPDATE Internationalization SET label = 'Implantar Agentes do Medulla' WHERE id = 30 AND fk_language = 3;
UPDATE Internationalization SET label = 'Medulla-Agents verteilen' WHERE id = 30 AND fk_language = 4;

UPDATE version set Number = 24;

