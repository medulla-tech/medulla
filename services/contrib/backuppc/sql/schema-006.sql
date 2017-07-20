USE backuppc;

-- User file requests save only user's Documents
-- Whole drive requests save Program file, Windows and user's Documents


-- Excluded files for Windows 8/8.1 backup (User files)
UPDATE backup_profiles SET excludes =
"/All Users
/Default
/Default User
/Public
/*/AppData
/*/Application Data
/*/Contacts
/*/Cookies
/*/Desktop
/*/Downloads
/*/Favorites
/*/Links
/*/Local Settings
/*/Music
/*/OneDrive
/*/Pictures
/*/Saved Games
/*/Searches
/*/Videos
/*/Recent
/*/SendTo
/*/NetHood
/*/PrintHood
/*/NTUSER.DAT*
/*/ntuser.dat*", id=9
WHERE profilename= "Windows 8/8.1 (User files)";

-- Excluded files for Windows 8/8.1 backup (Whole C: Drive)
UPDATE backup_profiles SET excludes =
"/Users/All Users
/Users/Default
/Users/Default User
/Users/Public
/Users/*/AppData
/Users/*/Application Data
/Users/*/Contacts
/Users/*/Cookies
/Users/*/Desktop
/Users/*/Downloads
/Users/*/Favorites
/Users/*/Links
/Users/*/Local Settings
/Users/*/Music
/Users/*/OneDrive
/Users/*/Pictures
/Users/*/Saved Games
/Users/*/Recent
/Users/*/Searches
/Users/*/SendTo
/Users/*/Videos
/Users/*/NetHood
/Users/*/PrintHood
/Users/*/NTUSER.DAT*
/Users/*/ntuser.dat*
/MSOCache
/PerfLogs
/ProgramData
/Windows/SoftwareDistribution/Download
/Windows/Temp", id=10
WHERE profilename= "Windows 8/8.1 (Whole drive)";

-- Excluded files for Windows 10 backup (User files)
UPDATE backup_profiles SET excludes =
"/All Users
/Default
/Default User
/defaultuser0
/Public
/*/AppData
/*/Application Data
/*/Contacts
/*/Cookies
/*/Desktop
/*/Downloads
/*/Favorites
/*/Links
/*/Local Settings
/*/Music
/*/OneDrive
/*/Pictures
/*/Saved Games
/*/Searches
/*/Videos
/*/Recent
/*/SendTo
/*/NetHood
/*/PrintHood
/*/NTUSER.DAT*
/*/ntuser.dat*", id=11
WHERE profilename= "Windows 10 (User files)";

-- Excluded files for Windows 10 backup (Whole drive)
UPDATE backup_profiles SET excludes =
"/Users/All Users
/Users/Default
/Users/Default User
/Users/defaultuser0
/Users/Public
/Users/*/AppData
/Users/*/Application Data
/Users/*/Contacts
/Users/*/Cookies
/Users/*/Desktop
/Users/*/Downloads
/Users/*/Favorites
/Users/*/Links
/Users/*/Local Settings
/Users/*/Music
/Users/*/OneDrive
/Users/*/Pictures
/Users/*/Saved Games
/Users/*/Recent
/Users/*/Searches
/Users/*/SendTo
/Users/*/Videos
/Users/*/NetHood
/Users/*/PrintHood
/Users/*/NTUSER.DAT*
/Users/*/ntuser.dat*
/MSOCache
/PerfLogs
/ProgramData
/Windows/SoftwareDistribution/Download
/Windows/Temp", id=12
WHERE profilename= "Windows 10 (Whole drive)";

UPDATE version SET number=6;
