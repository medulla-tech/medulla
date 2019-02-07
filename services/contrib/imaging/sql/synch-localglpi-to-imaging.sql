USE `glpi`;

DELIMITER $$

DROP TRIGGER IF EXISTS `glpi`.`glpi_computers_AFTER_UPDATE`$$
USE `glpi`$$
CREATE DEFINER = CURRENT_USER TRIGGER `glpi`.`glpi_computers_AFTER_UPDATE` AFTER UPDATE ON `glpi_computers` FOR EACH ROW
BEGIN
    CALL update_Imaging_Target(NEW.`entities_id`, NEW.`id`);
END$$
DELIMITER ;


USE `glpi`;
DROP procedure IF EXISTS `update_Imaging_Target`;

DELIMITER $$
USE `glpi`$$
CREATE DEFINER = CURRENT_USER PROCEDURE `update_Imaging_Target`(IN `id_Entity` VARCHAR(20) , IN `id_machine` VARCHAR(20))
BEGIN
DECLARE uuid varchar(40) ;
DECLARE idtarget varchar(255) ;
set uuid =  CONCAT("UUID",id_machine);

SELECT
    MAX(id)
INTO idtarget FROM
    `imaging`.`Target`
WHERE
    `imaging`.`Target`.`uuid` = uuid;

    IF idtarget IS NOT NULL THEN
		UPDATE `imaging`.`Target` SET `imaging`.`Target`.`fk_entity` = id_Entity WHERE `id` = idtarget;
    END IF;
END$$

DELIMITER ;
