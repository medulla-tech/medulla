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


-- ----------------------------------------------------------------------
-- trigger TABLE up_gray_list
-- suppression recopier sur up_gray_list_flop
-- ----------------------------------------------------------------------
DROP TRIGGER IF EXISTS `xmppmaster`.`up_gray_list_AFTER_DELETE`;

DELIMITER $$
USE `xmppmaster`$$
CREATE TRIGGER `xmppmaster`.`up_gray_list_AFTER_DELETE` AFTER DELETE ON `up_gray_list` FOR EACH ROW
BEGIN
-- regle si 1 certain temps le package na pas etait utiliser il passe dans les updates historique
	-- si son etat etait a 1 alors le package est supprimer
	-- remarque que sa soit 1 remise en flip flop ou 1 suppression reelle le package est supprimer
	-- lance script -s pour supprimer
	set @cmd = concat( "/usr/sbin/medulla-mariadb-move-update-package.py ", old.updateid, " -s");
    INSERT IGNORE INTO `xmppmaster`.`up_action_update_packages` (`action`, `packages`, `option`)
            VALUES (@cmd, old.updateid,"-c" );
	set @resulttxt = concat( "resultat command ", @result);
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
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 78;

COMMIT;
