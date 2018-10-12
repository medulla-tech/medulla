

ALTER TABLE `backuppc`.`hosts`
ADD COLUMN `reverse_port` INT NULL AFTER `post_restore_script`;

UPDATE version SET number=5;
