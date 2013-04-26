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

-- Add German translation

INSERT INTO Language (id, label) VALUES (4, "Deutsch");

INSERT INTO Internationalization (id, fk_language, label) VALUES (22, 4, "Standard Bootmenü");
INSERT INTO Internationalization (id, fk_language, label) VALUES (12, 4, "Boot Menu registrieren");

INSERT INTO Internationalization (id, fk_language, label) VALUES (32, 4, "Datum");
INSERT INTO Internationalization (id, fk_language, label) VALUES (13, 4, "Das aktuelle Datum auf die Systemplatte in eine date.txt-Datei schreiben");
INSERT INTO Internationalization (id, fk_language, label) VALUES (25, 4, "Sysprepdatei kopieren");
INSERT INTO Internationalization (id, fk_language, label) VALUES (14, 4, "Kopieren von sysprep.inf oder unattended.xml auf die Systemplatte");
INSERT INTO Internationalization (id, fk_language, label) VALUES (26, 4, "SID und Name ändern");
INSERT INTO Internationalization (id, fk_language, label) VALUES (15, 4, "Sowohl SID und Netbiosname änder");
INSERT INTO Internationalization (id, fk_language, label) VALUES (27, 4, "Shutdown");
INSERT INTO Internationalization (id, fk_language, label) VALUES (16, 4, "Client nach Aktionen anhalten");
INSERT INTO Internationalization (id, fk_language, label) VALUES (28, 4, "Debug Shell");
INSERT INTO Internationalization (id, fk_language, label) VALUES (17, 4, "Eine Shell zum Debuggen starten");
INSERT INTO Internationalization (id, fk_language, label) VALUES (29, 4, "Einzelne Partition erweitern");
INSERT INTO Internationalization (id, fk_language, label) VALUES (18, 4, "Die erste Partition (und einzige) wird über die ganze Platte ausgedehnt");
INSERT INTO Internationalization (id, fk_language, label) VALUES (30, 4, "Pulse-Agents verteilen");
INSERT INTO Internationalization (id, fk_language, label) VALUES (20, 4, "Verteilen von Pulse-Agents (SSH, OCS, VNC) beim nächsten Neustart");
INSERT INTO Internationalization (id, fk_language, label) VALUES (31, 4, "ICH5 Sync");
INSERT INTO Internationalization (id, fk_language, label) VALUES (21, 4, "RAID1 Synchronisation für ICH5-Chipsätze, Duplizierung der ersten Platte auf die zweite");

INSERT INTO Internationalization (id, fk_language, label) VALUES (2, 4, "Gewohnten Start fortsetzen");
INSERT INTO Internationalization (id, fk_language, label) VALUES (3, 4, "Wie gewohnt starten");
INSERT INTO Internationalization (id, fk_language, label) VALUES (4, 4, "Als Pulse-Client registrieren");
INSERT INTO Internationalization (id, fk_language, label) VALUES (5, 4, "Diesen Rechner in einem Pulse-Server registrieren");
INSERT INTO Internationalization (id, fk_language, label) VALUES (6, 4, "Sicherung erstellen");
INSERT INTO Internationalization (id, fk_language, label) VALUES (7, 4, "Eine Sicherung dieses Rechners erstellen");
INSERT INTO Internationalization (id, fk_language, label) VALUES (8, 4, "Plattenloses Booten");
INSERT INTO Internationalization (id, fk_language, label) VALUES (9, 4, "Plattenlose Umgebung laden und Eingabeaufforderung erhalten");
INSERT INTO Internationalization (id, fk_language, label) VALUES (10, 4, "Speichertest");
INSERT INTO Internationalization (id, fk_language, label) VALUES (11, 4, "Einen vollständigen Speichertest starten");
INSERT INTO Internationalization (id, fk_language, label) VALUES (23, 4, "Platten und Daten löschen");
INSERT INTO Internationalization (id, fk_language, label) VALUES (24, 4, "Sicher die Platte durch Überschreiben mit pseudozufälligen Zahlen löschen");

UPDATE version set Number = 6;
