USE backuppc;

-- User file requests save only user's Documents
-- Whole drive requests save Program file, Windows and user's Documents


-- Excluded files for Windows 7/Vista backup (User files)
UPDATE backup_profiles SET excludes =
"/All Users
/Default
/Default User
/Public
/*/AppData
/*/Application Data
/*/Desktop
/*/Contacts
/*/Cookies
/*/Favorites
/*/Links
/*/Local Settings
/*/Music
/*/Start Menu
/*/Pictures
/*/Videos
/*/Templates
/*/Saved Games
/*/Recent
/*/Searches
/*/SendTo
/*/Downloads
/*/NetHood
/*/PrintHood
/*/NTUSER.DAT*
/*/ntuser.dat*"
WHERE profilename= "Windows 7/Vista (User files)";

-- Excluded files for Windows 7/Vista backup (Whole C: Drive)
UPDATE backup_profiles SET excludes =
"/Users/All Users
/Users/Default
/Users/Default User
/Users/Public
/Users/*/AppData
/Users/*/Application Data
/Users/*/Desktop
/Users/*/Contacts
/Users/*/Cookies
/Users/*/Favorites
/Users/*/Favorites
/Users/*/Links
/Users/*/Local Settings
/Users/*/Music
/Users/*/Start Menu
/Users/*/Pictures
/Users/*/Videos
/Users/*/Templates
/Users/*/Saved Games
/Users/*/Recent
/Users/*/Searches
/Users/*/SendTo
/Users/*/Downloads
/Users/*/NetHood
/Users/*/PrintHood
/Users/*/NTUSER.DAT*
/Users/*/ntuser.dat*
/$Recycle.Bin
/Documents and Settings
/PerfLogs
/ProgramData
/System Volume Information
/MSOCache
/hiberfil.sys
/pagefile.sys
"
WHERE profilename= "Windows 7/Vista (Whole C: Drive)";

-- Excluded files for Windows 8/8.1 backup (User files)
INSERT INTO backup_profiles VALUES(null, 'Windows 8/8.1 (User files)', '/cygdrive/c/Users/',
	"/Default
	/Public
	/*/AppData
	/*/Contacts
	/*/Desktop
	/*/Downloads
	/*/Favorites
	/*/Links
	/*/Music
	/*/OneDrive
	/*/Pictures
	/*/Saved Games
	/*/Searches
	/*/Videos
	/*/NTUSER.DAT", 'utf8');

-- Excluded files for Windows 8/8.1 backup (whole drive)
INSERT INTO backup_profiles VALUES(null, 'Windows 8/8.1 (Whole drive)', '/cygdrive/c/',
	"/Users/Default
	/Users/Public
	/Users/*/AppData
	/Users/*/Contacts
	/Users/*/Desktop
	/Users/*/Downloads
	/Users/*/Favorites
	/Users/*/Links
	/Users/*/Music
	/Users/*/OneDrive
	/Users/*/Pictures
	/Users/*/Saved Games
	/Users/*/Searches
	/Users/*/Videos
	/Users/*/NTUSER.DAT
	/MSOCache
	/PerfLogs
	/ProgramData
	/Windows/SoftwareDistribution/Download
	/Windows/Temp", 'utf8');

-- Excluded files for Windows 10 backup (User files)
INSERT INTO backup_profiles VALUES(null, 'Windows 10 (User files)', '/cygdrive/c/Users/',
	"/Default
	/defaultuser0
	/Public
	/*/AppData
	/*/Contacts
	/*/Desktop
	/*/Downloads
	/*/Favorites
	/*/Links
	/*/Music
	/*/OneDrive
	/*/Pictures
	/*/Saved Games
	/*/Searches
	/*/Videos
	/*/NTUSER.DAT", 'utf8');

-- Excluded files for Windows 10 backup (Whole drive)
INSERT INTO backup_profiles VALUES(null, 'Windows 10 (Whole drive)', '/cygdrive/c/Users/',
	"/Users/Default
	/Users/defaultuser0
	/Users/Public
	/Users/*/AppData
	/Users/*/Contacts
	/Users/*/Desktop
	/Users/*/Downloads
	/Users/*/Favorites
	/Users/*/Links
	/Users/*/Music
	/Users/*/OneDrive
	/Users/*/Pictures
	/Users/*/Saved Games
	/Users/*/Searches
	/Users/*/Videos
	/Users/*/NTUSER.DAT
	/PrefLogs
	/ProgramData
	/Windows/SoftwareDistribution/Download
	/Windows/Temp", 'utf8');

UPDATE version SET number=4;

