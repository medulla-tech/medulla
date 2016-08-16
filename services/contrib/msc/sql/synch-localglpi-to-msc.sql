USE `glpi`;

DELIMITER $$

DROP TRIGGER IF EXISTS glpi.glpi_ipaddresses_AFTER_UPDATE$$
USE `glpi`$$
CREATE DEFINER=`root`@`localhost` TRIGGER `glpi`.`glpi_ipaddresses_AFTER_UPDATE` AFTER UPDATE ON `glpi_ipaddresses` FOR EACH ROW
BEGIN

    CALL update_MSC_Ips(NEW.`mainitems_id`);
END$$
DELIMITER ;

USE `glpi`;
DROP procedure IF EXISTS `update_MSC_Ips`;

DELIMITER $$
USE `glpi`$$
CREATE DEFINER=`root`@`localhost` PROCEDURE `update_MSC_Ips`(IN id_machine VARCHAR(20))
BEGIN
DECLARE uuid varchar(40) ;
DECLARE ret varchar(255) ;
DECLARE idtarget varchar(255) ;
set uuid =  CONCAT("UUID",id_machine);

    SELECT MAX(id) INTO idtarget FROM
         `msc`.`target`
    WHERE
        target_uuid = uuid;
    IF idtarget IS NOT NULL THEN
        SELECT
            GROUP_CONCAT(`name`    SEPARATOR '||')
        INTO ret FROM
            glpi.glpi_ipaddresses
        WHERE
            mainitems_id = id_machine;
    END IF;
    IF ret IS NOT NULL THEN
        UPDATE `msc`.`target` SET `target_ipaddr`= ret WHERE `id` = idtarget;
    END IF;
END$$

DELIMITER ;
