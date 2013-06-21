--
-- (c) 2010 Mandriva, http://www.mandriva.com/
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

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------

SET storage_engine=INNODB;
SET GLOBAL character_set_server=UTF8;
SET SESSION character_set_server=UTF8;

CREATE TABLE IF NOT EXISTS `backup_profiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profilename` varchar(50) NOT NULL,
  `sharenames` text NOT NULL,
  `excludes` text NOT NULL,
  `encoding` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;


INSERT INTO `backup_profiles` (`id`, `profilename`, `sharenames`, `excludes`, `encoding`) VALUES
(1, 'Windows XP (User files)', '/cygdrive/c/Documents and Settings/', '/*/Cookies\n/*/Local Settings/Temporary Internet Files\n/*/Local Settings/Temp\n/*/NTUSER.DAT*\n/*/ntuser.dat*\n/*/Local Settings/Application Data/Microsoft/Windows/UsrClass.dat*\n/*/Local Settings/Application Data/Mozilla/Firefox/Profiles/*/Cache\n/*/Local Settings/Application Data/Mozilla/Firefox/Profiles/*/OfflineCache\n/*/Recent', 'cp1252'),
(2, 'Windows XP (Whole C: Drive)', '/cygdrive/c/', '/Documents and Settings/*/Cookies\n/Documents and Settings/*/Local Settings/Temporary Internet Files\n/Documents and Settings/*/Local Settings/Temp\n/Documents and Settings/*/NTUSER.DAT*\n/Documents and Settings/*/ntuser.dat*\n/Documents and Settings/*/Local Settings/Application Data/Microsoft/Windows/UsrClass.dat*\n/Documents and Settings/*/Local Settings/Application Data/Mozilla/Firefox/Profiles/*/Cache\n/Documents and Settings/*/Local Settings/Application Data/Mozilla/Firefox/Profiles/*/OfflineCache\n/Documents and Settings/*/Recent\n/RECYCLER\n/MSOCache\n/System Volume Information\n/hiberfil.sys\n/pagefile.sys', 'cp1252'),
(7, 'Mac OS X (User files)', '/Users', '', 'utf8'),
(3, 'Windows 7/Vista (User files)', '/cygdrive/c/Users/', '/All Users\n/Users/Default User\n/Users/All Users/Application Data\n/Users/All Users/Desktop\n/All Users/Documents\n/All Users/Favorites\n/All Users/Start Menu\n/All Users/Templates\n/*/Application Data\n/*/Cookies\n/*/Local Settings\n/*/My Documents\n/*/NetHood\n/*/PrintHood\n/*/Recent\n/*/SendTo\n/*/Start Menu\n/*/Templates\n/*/AppData/Local/Application Data\n/*/AppData/Local/History\n/*/AppData/Local/Temporary Internet Files\n/*/Documents/My Music\n/*/Documents/My Pictures\n/*/Documents/My Videos\n/*/AppData/Local/Microsoft/Windows/Temporary Internet Files\n/*/AppData/Local/Temp\n/*/NTUSER.DAT*\n/*/ntuser.dat*\n/*/AppData/Local/Microsoft/Windows/UsrClass.dat*\n/*/AppData/Local/Microsoft/Windows Defender/FileTracker\n/*/AppData/Local/Microsoft/Windows/Explorer/thumbcache_*.db\n/*/AppData/Local/Microsoft/Windows/WER\n/*/AppData/Local/Mozilla/Firefox/Profiles/*/Cache\n/*/AppData/Local/Mozilla/Firefox/Profiles/*/OfflineCache\n/*/AppData/Roaming/Microsoft/Windows/Cookies\n/*/AppData/Roaming/Microsoft/Windows/Recent', 'cp1252'),
(4, 'Windows 7/Vista (Whole C: Drive)', '/cygdrive/c/', '/Documents and Settings\n/ProgramData/Application Data\n/ProgramData/Desktop\n/ProgramData/Documents\n/ProgramData/Favorites\n/ProgramData/Start Menu\n/ProgramData/Templates\n/Users/All Users\n/Users/Users/Default User\n/Users/Users/All Users/Application Data\n/Users/Users/All Users/Desktop\n/Users/All Users/Documents\n/Users/All Users/Favorites\n/Users/All Users/Start Menu\n/Users/All Users/Templates\n/Users/*/Application Data\n/Users/*/Cookies\n/Users/*/Local Settings\n/Users/*/My Documents\n/Users/*/NetHood\n/Users/*/PrintHood\n/Users/*/Recent\n/Users/*/SendTo\n/Users/*/Start Menu\n/Users/*/Templates\n/Users/*/AppData/Local/Application Data\n/Users/*/AppData/Local/History\n/Users/*/AppData/Local/Temporary Internet Files\n/Users/*/Documents/My Music\n/Users/*/Documents/My Pictures\n/Users/*/Documents/My Videos\n/Users/*/AppData/Local/Microsoft/Windows/Temporary Internet Files\n/Users/*/AppData/Local/Temp\n/Users/*/NTUSER.DAT*\n/Users/*/ntuser.dat*\n/Users/*/AppData/Local/Microsoft/Windows/UsrClass.dat*\n/Users/*/AppData/Local/Microsoft/Windows Defender/FileTracker\n/Users/*/AppData/Local/Microsoft/Windows/Explorer/thumbcache_*.db\n/Users/*/AppData/Local/Microsoft/Windows/WER\n/Users/*/AppData/Local/Mozilla/Firefox/Profiles/*/Cache\n/Users/*/AppData/Local/Mozilla/Firefox/Profiles/*/OfflineCache\n/Users/*/AppData/Roaming/Microsoft/Windows/Cookies\n/Users/*/AppData/Roaming/Microsoft/Windows/Recent\n/MSOCache\n/System Volume Information\n/$Recycle.Bin\n/hiberfil.sys\n/pagefile.sys', 'cp1252'),
(5, 'Linux (User files)', '/home', '', 'utf8'),
(6, 'Linux (Whole / drive)', '/', '/proc/*\n/sys/*\n/dev/*\n/tmp/*\n/var/tmp/*\n/media/*\n/mnt/*', 'utf8'),
(8, 'Mac OS X (Whole / drive)', '/', '/cores/*\n/dev/*\n/net/*\n/private/tmp/*\n/Volumes/*', 'utf8');


CREATE TABLE IF NOT EXISTS `backup_servers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entity_uuid` varchar(50) NOT NULL,
  `backupserver_url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `entity_uuid` (`entity_uuid`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `hosts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(50) NOT NULL,
  `backup_profile` int(11) NOT NULL,
  `period_profile` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1;

CREATE TABLE IF NOT EXISTS `period_profiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `profilename` varchar(255) NOT NULL,
  `full` float NOT NULL,
  `incr` float NOT NULL,
  `exclude_periods` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3;

INSERT INTO `period_profiles` (`id`, `profilename`, `full`, `incr`, `exclude_periods`) VALUES
(1, 'Nightly', 7, 1, '7.00=>20.00:1,2,3,4,5,6,7'),
(2, 'Daytime', 7, 1, '19.00=>9.00:1,2,3,4,5,6,7');

CREATE TABLE IF NOT EXISTS `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `version` (`Number`) VALUES(1);

COMMIT;
