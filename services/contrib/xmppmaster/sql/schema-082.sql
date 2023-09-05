--
-- (c) 2023 Siveo, http://www.siveo.net/
--
--
-- This file is part of Pulse 2, http://www.siveo.net/
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

START TRANSACTION;
USE `xmppmaster`;

-- ----------------------------------------------------------------------
-- Database additionne events
-- ----------------------------------------------------------------------
-- [Event] Désinstallation des packages inutilisés depuis plus de 10 jours

-- Cet événement automatisé, nommé "Uninstall_unused_packages", vise à optimiser l'utilisation des ressources en supprimant les packages qui n'ont pas été demandés ou utilisés depuis plus de 10 jours.

-- L'événement surveille les enregistrements dans la base de données et effectue les actions suivantes :
-- - Pour les packages non demandés par aucune machine depuis 10 jours, il bascule dans la "graylistflipflop" (liste grise) et les désinstalle.
-- - Les packages en liste blanche ("white list") ne sont jamais désinstallés.
-- - Si des demandes sont présentes dans la table "up_machine_windows" mais ne sont pas satisfaites, ces demandes sont supprimées.
-- - Si une machine refait une demande ultérieurement, le package est automatiquement réinséré dans la "graylist" et réinstallé.

-- Cet événement contribue à optimiser l'espace et les ressources en supprimant les packages inutilisés et en maintenant la liste des packages pertinente et efficace. Il garantit également que les demandes non satisfaites sont gérées de manière appropriée.

-- Notez que l'événement fonctionne de manière automatique et continue, contribuant ainsi à la maintenance 1 list beaucoup plus humaine en nombre de package deployable.

DROP EVENT IF EXISTS   xmppmaster.Uninstall_old_package;
DELIMITER $$
CREATE EVENT xmppmaster.Uninstall_old_package
ON SCHEDULE EVERY 1 DAY -- Planification chaque jour
DO
BEGIN
    -- Verification que les evenement soit activer.
    -- command SHOW VARIABLES LIKE 'event_scheduler';
    -- pour passer event_scheduler a ON
    -- SET GLOBAL event_scheduler = ON;
    DELETE FROM xmppmaster.up_machine_windows WHERE xmppmaster.up_machine_windows.update_id IN
(SELECT t1.updateid FROM xmppmaster.up_gray_list t1 WHERE
t1.updateid NOT IN (SELECT  updateid  FROM  xmppmaster.up_white_list)
AND NOW() > t1.validity_date);
   delete from `xmppmaster`.`up_gray_list` where now() > validity_date;
END$$
DELIMITER ;



-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 82;

COMMIT;
