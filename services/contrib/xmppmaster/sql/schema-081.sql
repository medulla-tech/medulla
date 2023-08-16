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
-- Trigger up_gray_list_AFTER_UPDATE
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_gray_list_AFTER_UPDATE` AFTER UPDATE ON `up_gray_list` FOR EACH ROW
BEGIN

END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_gray_list_AFTER_DELETE
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_gray_list_AFTER_DELETE` AFTER DELETE ON `up_gray_list` FOR EACH ROW
BEGIN
    set @updatidpackage = false;
	set @cmd = concat( "/usr/sbin/medulla_mysql_exec_update.sh  ", old.updateid, " s");
    select true into @updatidpackage FROM `xmppmaster`.`up_white_list` where updateid = old.updateid;
    if @updatidpackage = false then
		INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` (`action`, `packages`, `option`)
            VALUES (@cmd, old.updateid, "-c" );
		set @logtext = concat("Creation command : ", @cmd );
		INSERT IGNORE INTO `xmppmaster`.`logs` (`type`,
									`module`,
									`text`,
									`fromuser`,
									`touser`,
									`action`,
									`sessionname`,
									`how`,
									`why`,
									`priority`,
									`who`)
		VALUES ('automate_Maria',
				'update',
				@logtext,
				'up_gray_list_AFTER_DELETE',
				'medulla',
				'delete',
				old.updateid,
				'auto',
				'mariadb',
				'-1',
				'system');
	end if;
	IF LENGTH(OLD.updateid) = 36 THEN
		set @logtext = concat("replace dans la table up_gray_list_flop package  : ", old.updateid );
		INSERT IGNORE INTO `xmppmaster`.`logs` (`type`,
										`module`,
										`text`,
										`fromuser`,
										`touser`,
										`action`,
										`sessionname`,
										`how`,
										`why`,
										`priority`,
										`who`)
		VALUES ('automate_Maria',
				'update',
				@logtext,
				'up_gray_list_AFTER_DELETE',
				'medulla',
				'delete',
				old.updateid,
				'auto',
				'mariadb',
				'-1',
				'system');
		INSERT IGNORE INTO `xmppmaster`.`up_gray_list_flop` (`updateid`,
															 `kb`,
															 `revisionid`,
															 `title`,
															 `description`,
															 `updateid_package`,
															 `payloadfiles`,
															 `supersededby`,
															 `creationdate`,
															 `title_short`,
															 `valided`,
															 `validity_date`) VALUES (old.updateid,
															 old.kb,
															 old.revisionid,
															 old.title,
															 old.description,
															 old.updateid_package,
															 old.payloadfiles,
															 old.supersededby,
															 old.creationdate,
															 old.title_short,
															 old.valided,
															 old.validity_date);
	else
		set @logtext = concat("Suppression definitive package  : ", old.updateid );
		INSERT INTO `xmppmaster`.`logs` (`type`,
										`module`,
										`text`,
										`fromuser`,
										`touser`,
										`action`,
										`sessionname`,
										`how`,
										`why`,
										`priority`,
										`who`)
		VALUES ('automate_Maria',
				'update',
				@logtext,
				'up_gray_list_AFTER_DELETE',
				'medulla',
				'delete',
				old.updateid,
				'auto',
				'mariadb',
				'-1',
				'system');
	END IF;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_gray_list_AFTER_INSERT
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_gray_list_AFTER_INSERT` AFTER INSERT ON `up_gray_list` FOR EACH ROW
BEGIN
looptrigger:LOOP
	-- if  new.valided = 0 then
	--	LEAVE looptrigger;
	-- end if;
	-- if new.valided = 1 then
		set @cmd = concat( "/usr/sbin/medulla_mysql_exec_update.sh ", new.updateid, " c");
        INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` (`action`, `packages`, `option`)
			VALUES (@cmd, new.updateid,"-c" );
		set @logtext = concat("Creation command : ", @cmd );
		INSERT INTO `xmppmaster`.`logs` (`type`,
										`module`,
										`text`,
										`fromuser`,
										`touser`,
										`action`,
										`sessionname`,
										`how`,
										`why`,
										`priority`,
										`who`)
		VALUES ('automate_Maria',
				'update',
				@logtext,
				'up_gray_list_AFTER_INSERT',
				'medulla',
				'creation',
				new.updateid,
				'auto',
				'mariadb',
				'-1',
				'system');
		LEAVE looptrigger;
	-- end if;
END LOOP;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_action_update_packages_AFTER_INSERT
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_action_update_packages_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_action_update_packages_AFTER_INSERT` AFTER INSERT ON `up_action_update_packages` FOR EACH ROW
BEGIN
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_gray_list_flop_AFTER_DELETE
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_flop_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_gray_list_flop_AFTER_DELETE` AFTER DELETE ON `up_gray_list_flop` FOR EACH ROW
BEGIN
	IF LENGTH(OLD.updateid) = 36 THEN
        set @logtext = concat("replace dans la table up_gray_list update : ", old.updateid  );
		INSERT INTO `xmppmaster`.`logs` (`type`,
									`module`,
									`text`,
									`fromuser`,
									`touser`,
									`action`,
									`sessionname`,
									`how`,
									`why`,
									`priority`,
									`who`)
	VALUES ('automate_Maria',
			'update',
            @logtext,
            'up_gray_list_flop_AFTER_DELETE',
            'medulla',
            'delete',
            old.updateid,
            'auto',
            'mariadb',
            '-1',
            'system');
		INSERT IGNORE INTO `xmppmaster`.`up_gray_list` (`updateid`,
		 `kb`,
		 `revisionid`,
		 `title`,
		 `description`,
		 `updateid_package`,
		 `payloadfiles`,
		 `supersededby`,
		 `creationdate`,
		 `title_short`,
		 `valided`,
		 `validity_date`) VALUES (	old.updateid,
									old.kb,
									old.revisionid,
									old.title,
									old.description,
									old.updateid_package,
									old.payloadfiles,
									old.supersededby,
									old.creationdate,
									old.title_short,
									old.valided,
									now() + INTERVAL 10 day)
		ON DUPLICATE KEY UPDATE validity_date = now() + INTERVAL 10 day;
	else
		set @logtext = concat("supprime definitivement de la table up_gray_list_flop update : ", old.updateid  );
		INSERT INTO `xmppmaster`.`logs` (`type`,
									`module`,
									`text`,
									`fromuser`,
									`touser`,
									`action`,
									`sessionname`,
									`how`,
									`why`,
									`priority`,
									`who`)
	VALUES ('automate_Maria',
			'update',
            @logtext,
            'up_gray_list_flop_AFTER_DELETE',
            'medulla',
            'delete',
            old.updateid,
            'auto',
            'mariadb',
            '-1',
            'system');
	END IF;

END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_black_list_AFTER_INSERT
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_black_list_AFTER_INSERT` AFTER INSERT ON `up_black_list` FOR EACH ROW
BEGIN
	DELETE FROM `xmppmaster`.`up_gray_list`
	WHERE
		`updateid` IN (SELECT
			updateid_or_kb
		FROM
			xmppmaster.up_black_list
		WHERE
			userjid_regexp = '.*'
			AND type_rule = 'id');
	UPDATE `xmppmaster`.`up_gray_list_flop`
	SET
		`updateid` = LEFT(UUID(), 8),
		`kb` = 'bidon'
	WHERE
		`updateid` IN (SELECT
				updateid_or_kb
			FROM
				xmppmaster.up_black_list
			WHERE
				userjid_regexp = '.*'
					AND type_rule = 'id');

	DELETE FROM `xmppmaster`.`up_gray_list`
	WHERE
		`kb` IN (SELECT
			updateid_or_kb
		FROM
			xmppmaster.up_black_list

		WHERE
			userjid_regexp = '.*'
			AND type_rule = 'kb');
	UPDATE `xmppmaster`.`up_gray_list_flop`
	SET
		`kb` = 'bidon'
	WHERE
		`updateid` IN (SELECT
				updateid_or_kb
			FROM
				xmppmaster.up_black_list
			WHERE
				userjid_regexp = '.*'
					AND type_rule = 'kb');
	DELETE FROM `xmppmaster`.`up_gray_list_flop`
	WHERE
		(`kb` = 'bidon');

   DELETE FROM `xmppmaster`.`up_white_list` WHERE (`updateid` = new.updateid_or_kb or `kb` = new.updateid_or_kb );

END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_black_list_AFTER_UPDATE
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_black_list_AFTER_UPDATE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_black_list_AFTER_UPDATE` AFTER UPDATE ON `up_black_list` FOR EACH ROW
BEGIN
	DELETE FROM `xmppmaster`.`up_gray_list`
	WHERE
		`updateid` IN (SELECT
			updateid_or_kb
		FROM
			xmppmaster.up_black_list
		WHERE
			userjid_regexp = '.*'
			AND type_rule = 'id');
	UPDATE `xmppmaster`.`up_gray_list_flop`
	SET
		`updateid` = LEFT(UUID(), 8),
		`kb` = 'bidon'
	WHERE
		`updateid` IN (SELECT
				updateid_or_kb
			FROM
				xmppmaster.up_black_list
			WHERE
				userjid_regexp = '.*'
					AND type_rule = 'id');

	DELETE FROM `xmppmaster`.`up_gray_list`
	WHERE
		`kb` IN (SELECT
			updateid_or_kb
		FROM
			xmppmaster.up_black_list

		WHERE
			userjid_regexp = '.*'
			AND type_rule = 'kb');

	UPDATE `xmppmaster`.`up_gray_list_flop`
	SET
		`kb` = 'bidon'
	WHERE
		`updateid` IN (SELECT
				updateid_or_kb
			FROM
				xmppmaster.up_black_list
			WHERE
				userjid_regexp = '.*'
					AND type_rule = 'kb');
	DELETE FROM `xmppmaster`.`up_gray_list_flop`
	WHERE
		(`kb` = 'bidon');
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_white_list_AFTER_INSERT
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_white_list_AFTER_INSERT`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_white_list_AFTER_INSERT` AFTER INSERT ON `up_white_list` FOR EACH ROW
BEGIN
	delete from xmppmaster.up_gray_list where updateid = new.updateid;
END$$
DELIMITER ;

-- ----------------------------------------------------------------------
-- Trigger up_white_list_AFTER_DELETE
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_white_list_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_white_list_AFTER_DELETE` AFTER DELETE ON `up_white_list` FOR EACH ROW
BEGIN
	delete from up_gray_list_flop where up_gray_list_flop.updateid = old.updateid;

END$$
DELIMITER ;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 81;

COMMIT;
