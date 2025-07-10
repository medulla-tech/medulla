SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

-- Update parameters for clonezilla in Entity table
UPDATE PostInstallScript
SET default_desc = 'Medulla postinstall script with debug'
WHERE default_desc = 'SIVEO postinstall script with debug';

UPDATE version set Number = 29;