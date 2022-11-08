-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------


--
-- Table structure for table `version`
--

CREATE TABLE if not exists `version` (
  `Number` tinyint(4) unsigned NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for profils
--

CREATE TABLE IF NOT EXISTS `tests` (
        `id` int NOT NULL AUTO_INCREMENT, PRIMARY KEY(`id`),
        `name` varchar(50) NOT NULL,
        `message` varchar(255) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `version` VALUES (1);
