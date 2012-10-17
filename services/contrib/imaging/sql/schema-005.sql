--
-- (c) 2012 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Pulse 2, http://pulse2.mandriva.org
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

SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

UPDATE BootService SET default_name = "Register as Pulse Client" WHERE default_name LIKE "Register as Pulse 2 Client";
UPDATE BootService SET default_desc = "Record this computer in a Pulse server" WHERE default_desc LIKE "Record this computer in Pulse 2 Server";
UPDATE BootService SET default_name = "Create a Backup" WHERE default_name LIKE "Create a backup";
UPDATE BootService SET default_name = "Memory Test" WHERE default_name LIKE "Memory test";

UPDATE PostInstallScript SET default_desc = "Write the current date on system disk in a date.txt file" WHERE id = 1;
UPDATE PostInstallScript SET default_name = "Copy Sysprep File" WHERE default_name LIKE "Sysprep";
UPDATE PostInstallScript SET default_desc = "Copy sysprep.inf or unattended.xml on system disk" WHERE default_desc LIKE "Copy sysprep.inf on C:\\";
UPDATE PostInstallScript SET default_name = "Change SID And Name" WHERE default_name LIKE "SID";
UPDATE PostInstallScript SET default_name = "Debug Shell" WHERE default_name LIKE "Debug";
UPDATE PostInstallScript SET default_desc = "Launch a debug shell" WHERE default_desc LIKE "Debug Shell";
UPDATE PostInstallScript SET default_name = "Single Partition Extension" WHERE default_name LIKE "Partition extension";
UPDATE PostInstallScript SET default_desc = "The first partition (and the only one) will be extended across the whole disk" WHERE default_desc LIKE "The first partition will be extend across the whole disk";
UPDATE PostInstallScript SET default_desc = "Deploy Pulse agents (SSH, OCS, VNC) on next reboot" WHERE default_desc LIKE "Deploy Pulse agents (SSH, OCS, VNC)";
UPDATE PostInstallScript SET default_name = "ICH5 Sync" WHERE default_name LIKE "ICH 5 sync";
UPDATE PostInstallScript SET default_desc = "Halt client after operations" WHERE default_desc LIKE "Halt client";

UPDATE Internationalization SET label = "Continuer le Démarrage Normalement" WHERE id = 2 AND fk_language = 2;
UPDATE Internationalization SET label = "Enregistrement Pulse" WHERE id = 4 AND fk_language = 2;
UPDATE Internationalization SET label = "Enregistrer ce poste auprès du serveur Pulse" WHERE id = 5 and fk_language = 2;
UPDATE Internationalization SET label = "Créer Une Image" WHERE id = 6 AND fk_language = 2;
UPDATE Internationalization SET label = "Démarrage Sans Disque" WHERE id = 8 AND fk_language = 2;
UPDATE Internationalization SET label = "Test Mémoire" WHERE id = 10 AND fk_language = 2;
UPDATE Internationalization SET label = "Inscrire la date sur le disque système dans le fichier date.txt" WHERE id = 13 AND fk_language = 2;
UPDATE Internationalization SET label = "Copier le fichier sysprep.inf ou unattended.txt sur le disque système" WHERE id = 14 AND fk_language = 2;
UPDATE Internationalization SET label = "Menu Par Défaut" WHERE id = 22 AND fk_language = 2;
UPDATE Internationalization SET label = "Effacement de Disque Sécurisé" WHERE id = 23 AND fk_language = 2;
UPDATE Internationalization SET label = "Eteindre le client après les opérations" WHERE id = 16 AND fk_language = 2;
UPDATE Internationalization SET label = "Lancer une invite de commande de débogage" WHERE id = 17 AND fk_language = 2;
UPDATE Internationalization SET label = "Déployer les agents Pulse (SSH, OCS, VNC) au prochain redémarrage" WHERE id = 20 AND fk_language = 2;
UPDATE Internationalization SET label = "Synchronisation RAID1 pour chipsets ICH5, duplique le 1er disque sur le second" WHERE id = 21 AND fk_language = 2;
UPDATE Internationalization SET label = "Changement du SID et du nom Netbios" WHERE id = 15 AND fk_language = 2;
UPDATE Internationalization SET label = "La première partition (et uniquement celle-ci) sera étendue à l'intégralité du disque dur" WHERE id = 18 AND fk_language = 2;
UPDATE Internationalization SET label = "Effacer un disque de manière sécurisée en écrivant des nombres pseudoaléatoires" WHERE id = 24 AND fk_language = 2;

INSERT INTO Internationalization (id, fk_language, label) VALUES (25, 2, "Copier le Fichier Sysprep");
INSERT INTO Internationalization (id, fk_language, label) VALUES (26, 2, "Changer le SID et le Nom");
INSERT INTO Internationalization (id, fk_language, label) VALUES (27, 2, "Eteindre");
INSERT INTO Internationalization (id, fk_language, label) VALUES (28, 2, "Invite de Commande de Débogage");
INSERT INTO Internationalization (id, fk_language, label) VALUES (29, 2, "Extension d'une partition unique");
INSERT INTO Internationalization (id, fk_language, label) VALUES (30, 2, "Déployer les Agents Pulse");
INSERT INTO Internationalization (id, fk_language, label) VALUES (31, 2, "Synchronisation Chipset ICH5");
INSERT INTO Internationalization (id, fk_language, label) VALUES (32, 2, "Date");

UPDATE PostInstallScript SET fk_name = 25 WHERE id = 2;
UPDATE PostInstallScript SET fk_name = 26 WHERE id = 3;
UPDATE PostInstallScript SET fk_name = 27 WHERE id = 4;
UPDATE PostInstallScript SET fk_name = 28 WHERE id = 5;
UPDATE PostInstallScript SET fk_name = 29 WHERE id = 6;
UPDATE PostInstallScript SET fk_name = 30 WHERE id = 8;
UPDATE PostInstallScript SET fk_name = 31 WHERE id = 9;
UPDATE PostInstallScript SET fk_name = 32 WHERE id = 1;

UPDATE version set Number = 5;
