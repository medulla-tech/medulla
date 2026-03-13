--
-- (c) 2025, http://www.medulla-tech.io/
--
--
-- This file is part of Pulse 2, http://www.medulla-tech.io/
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
-- FILE contrib/xmppmaster/sql/schema-096.sql
-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;
USE `xmppmaster`;



USE `xmppmaster`;
DROP PROCEDURE IF EXISTS `xmppmaster`.`up_init_packages_Win11_X64_25H2`;

DELIMITER $$

CREATE PROCEDURE `up_init_packages_Win11_X64_25H2`()
BEGIN
    -- Supprime la table si elle existe (sans SQL dynamique)
    DROP TABLE IF EXISTS up_packages_Win11_X64_25H2;
    -- Création de la table avec jointure pour payloadfiles et updateid_package
    CREATE TABLE up_packages_Win11_X64_25H2 AS
         SELECT
            aa.updateid,
            bb.updateid AS updateid_package,
            aa.revisionid,
            aa.creationdate,
            aa.compagny,
            aa.product,
            aa.productfamily,
            aa.updateclassification,
            aa.prerequisite,
            aa.title,
            aa.description,
            aa.msrcseverity,
            aa.msrcnumber,
            aa.kb,
            aa.languages,
            aa.category,
            aa.supersededby,
            aa.supersedes,
            bb.payloadfiles,
            aa.revisionnumber,
            aa.bundledby_revision,
            aa.isleaf,
            aa.issoftware,
            aa.deploymentaction,
            aa.title_short
         FROM
            xmppmaster.update_data aa
            JOIN xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
         WHERE
            aa.title LIKE '%Windows 11, version 25H2%'
            AND aa.product LIKE '%Windows 11%'
            AND aa.title NOT LIKE '%ARM64%'
            AND aa.title NOT LIKE '%X86%';

END$$

DELIMITER ;


INSERT INTO `xmppmaster`.`applicationconfig` (`key`, `value`, `comment`, `context`, `module`, `enable`) VALUES ('table produits', 'up_packages_Win11_X64_25H2', 'Microsoft Windows 11 [ fin support 2027/10 ]', 'entity', 'xmppmaster/update', '1');


INSERT INTO `up_packages_major_Lang_code` VALUES
(11,'ar-SA','0401','Arabic',0,'Win11_25H2_Arabic_x64.iso','Win11upd_25H2_Arabic_x64_pbqbowfj6h9lom'),
(11,'bg-BG','0402','Bulgarian',0,'Win11_25H2_Bulgarian_x64.iso','Win11upd_25H2_Bulgarian_x64_pbqbowfj6h9lom'),
(11,'cs-CZ','0405','Czech',0,'Win11_25H2_Czech_x64.iso','Win11upd_25H2_Czech_x64_pbqbowfj6h9lom'),
(11,'da-DK','0406','Danish',0,'Win11_25H2_Danish_x64.iso','Win11upd_25H2_Danish_x64_pbqbowfj6h9lom'),
(11,'de-DE','0407','German',0,'Win11_25H2_German_x64.iso','Win11upd_25H2_German_x64_pbqbowfj6h9lom'),
(11,'el-GR','0408','Greek',0,'Win11_25H2_Greek_x64.iso','Win11upd_25H2_Greek_x64_pbqbowfj6h9lom'),
(11,'en-GB','0809','English - United Kingdom',1,'Win11_25H2_English_UK_x64.iso','Win11upd_25H2_English_UK_x64_pbqbowfj6h9lom'),
(11,'en-US','0409','English - United States',1,'Win11_25H2_English_US_x64.iso','Win11upd_25H2_English_US_x64_pbqbowfj6h9lom'),
(11,'es-ES','040A','Spanish - Spain',0,'Win11_25H2_Spanish_x64.iso','Win11upd_25H2_Spanish_x64_pbqbowfj6h9lom'),
(11,'es-MX','080A','Spanish - Mexico',0,'Win11_25H2_Spanish_Mexico_x64.iso','Win11upd_25H2_Spanish_Mexico_x64_pbqbowfj6h9lom'),
(11,'et-EE','0425','Estonian',0,'Win11_25H2_Estonian_x64.iso','Win11upd_25H2_Estonian_x64_pbqbowfj6h9lom'),
(11,'fi-FI','040E','Finnish',0,'Win11_25H2_Finnish_x64.iso','Win11upd_25H2_Finnish_x64_pbqbowfj6h9lom'),
(11,'fr-CA','0C0C','French - Canada',0,'Win11_25H2_French_Canadian_x64.iso','Win11upd_25H2_French_Canadian_x64_pbqbowfj6h9lom'),
(11,'fr-FR','040C','French',1,'Win11_25H2_French_x64.iso','Win11upd_25H2_French_x64_pbqbowfj6h9lom'),
(11,'he-IL','040D','Hebrew',0,'Win11_25H2_Hebrew_x64.iso','Win11upd_25H2_Hebrew_x64_pbqbowfj6h9lom'),
(11,'hi-IN','0439','Hindi',0,'Win11_25H2_Hindi_x64.iso','Win11upd_25H2_Hindi_x64_pbqbowfj6h9lom'),
(11,'hr-HR','041A','Croatian',0,'Win11_25H2_Croatian_x64.iso','Win11upd_25H2_Croatian_x64_pbqbowfj6h9lom'),
(11,'hu-HU','040E','Hungarian',0,'Win11_25H2_Hungarian_x64.iso','Win11upd_25H2_Hungarian_x64_pbqbowfj6h9lom'),
(11,'it-IT','0410','Italian',0,'Win11_25H2_Italian_x64.iso','Win11upd_25H2_Italian_x64_pbqbowfj6h9lom'),
(11,'ja-JP','0411','Japanese',0,'Win11_25H2_Japanese_x64.iso','Win11upd_25H2_Japanese_x64_pbqbowfj6h9lom'),
(11,'ko-KR','0412','Korean',0,'Win11_25H2_Korean_x64.iso','Win11upd_25H2_Korean_x64_pbqbowfj6h9lom'),
(11,'lt-LT','0427','Lithuanian',0,'Win11_25H2_Lithuanian_x64.iso','Win11upd_25H2_Lithuanian_x64_pbqbowfj6h9lom'),
(11,'lv-LV','0426','Latvian',0,'Win11_25H2_Latvian_x64.iso','Win11upd_25H2_Latvian_x64_pbqbowfj6h9lom'),
(11,'nb-NO','0414','Norwegian',0,'Win11_25H2_Norwegian_x64.iso','Win11upd_25H2_Norwegian_x64_pbqbowfj6h9lom'),
(11,'nl-NL','0413','Dutch',0,'Win11_25H2_Dutch_x64.iso','Win11upd_25H2_Dutch_x64_pbqbowfj6h9lom'),
(11,'pl-PL','0415','Polish',0,'Win11_25H2_Polish_x64.iso','Win11upd_25H2_Polish_x64_pbqbowfj6h9lom'),
(11,'pt-PT','0816','Portuguese - Portugal',0,'Win11_25H2_Portuguese_Portugal_x64.iso','Win11upd_25H2_Portuguese_Portugal_x64_pbqbowfj6h9lom'),
(11,'pt-BR','0416','Portuguese - Brazil',0,'Win11_25H2_Portuguese_Brazil_x64.iso','Win11upd_25H2_Portuguese_Brazil_x64_pbqbowfj6h9lom'),
(11,'ru-RU','0419','Russian',0,'Win11_25H2_Russian_x64.iso','Win11upd_25H2_Russian_x64_pbqbowfj6h9lom'),
(11,'sv-SE','041D','Swedish',0,'Win11_25H2_Swedish_x64.iso','Win11upd_25H2_Swedish_x64_pbqbowfj6h9lom'),
(11,'th-TH','041E','Thai',0,'Win11_25H2_Thai_x64.iso','Win11upd_25H2_Thai_x64_pbqbowfj6h9lom'),
(11,'tr-TR','041F','Turkish',0,'Win11_25H2_Turkish_x64.iso','Win11upd_25H2_Turkish_x64_pbqbowfj6h9lom'),
(11,'uk-UA','0422','Ukrainian',0,'Win11_25H2_Ukrainian_x64.iso','Win11upd_25H2_Ukrainian_x64_pbqbowfj6h9lom'),
(11,'zh-CN','0804','Chinese - Simplified',0,'Win11_25H2_Chinese_Simplified_x64.iso','Win11upd_25H2_Chinese_Simplified_x64_pbqbowfj6h9lom'),
(11,'zh-TW','0404','Chinese - Traditional',0,'Win11_25H2_Chinese_Traditional_x64.iso','Win11upd_25H2_Chinese_Traditional_x64');

/*
INSERT INTO `up_packages_major_Lang_code` VALUES
(11,'ar-SA','0401','Arabic',0,'Win11_25H2_Arabic_ARM64.iso','Win11upd_25H2_Arabic_ARM64_pbqbowfj6h'),
(11,'bg-BG','0402','Bulgarian',0,'Win11_25H2_Bulgarian_ARM64.iso','Win11upd_25H2_Bulgarian_ARM64_pbqbow'),
(11,'cs-CZ','0405','Czech',0,'Win11_25H2_Czech_ARM64.iso','Win11upd_25H2_Czech_ARM64_pbqbowfj6h9'),
(11,'da-DK','0406','Danish',0,'Win11_25H2_Danish_ARM64.iso','Win11upd_25H2_Danish_ARM64_pbqbowfj6h9'),
(11,'de-DE','0407','German',0,'Win11_25H2_German_ARM64.iso','Win11upd_25H2_German_ARM64_pbqbowfj6h9'),
(11,'el-GR','0408','Greek',0,'Win11_25H2_Greek_ARM64.iso','Win11upd_25H2_Greek_ARM64_pbqbowfj6h9l'),
(11,'en-GB','0809','English - United Kingdom',1,'Win11_25H2_English_UK_ARM64.iso','Win11upd_25H2_English_UK_ARM64_pbqbo'),
(11,'en-US','0409','English - United States',1,'Win11_25H2_English_US_ARM64.iso','Win11upd_25H2_English_US_ARM64_pbqbo'),
(11,'es-ES','040A','Spanish - Spain',0,'Win11_25H2_Spanish_ARM64.iso','Win11upd_25H2_Spanish_ARM64_pbqbowfj6'),
(11,'es-MX','080A','Spanish - Mexico',0,'Win11_25H2_Spanish_Mexico_ARM64.iso','Win11upd_25H2_Spanish_Mexico_ARM64'),
(11,'et-EE','0425','Estonian',0,'Win11_25H2_Estonian_ARM64.iso','Win11upd_25H2_Estonian_ARM64_pbqbowfj'),
(11,'fi-FI','040B','Finnish',0,'Win11_25H2_Finnish_ARM64.iso','Win11upd_25H2_Finnish_ARM64_pbqbowfj6'),
(11,'fr-CA','0C0C','French - Canada',0,'Win11_25H2_French_Canadian_ARM64.iso','Win11upd_25H2_French_Canadian_ARM64'),
(11,'fr-FR','040C','French',1,'Win11_25H2_French_ARM64.iso','Win11upd_25H2_French_ARM64_pbqbowfj6h'),
(11,'he-IL','040D','Hebrew',0,'Win11_25H2_Hebrew_ARM64.iso','Win11upd_25H2_Hebrew_ARM64_pbqbowfj6h'),
(11,'hi-IN','0439','Hindi',0,'Win11_25H2_Hindi_ARM64.iso','Win11upd_25H2_Hindi_ARM64_pbqbowfj6h9'),
(11,'hr-HR','041A','Croatian',0,'Win11_25H2_Croatian_ARM64.iso','Win11upd_25H2_Croatian_ARM64_pbqbowfj'),
(11,'hu-HU','040E','Hungarian',0,'Win11_25H2_Hungarian_ARM64.iso','Win11upd_25H2_Hungarian_ARM64_pbqbowf'),
(11,'it-IT','0410','Italian',0,'Win11_25H2_Italian_ARM64.iso','Win11upd_25H2_Italian_ARM64_pbqbowfj6'),
(11,'ja-JP','0411','Japanese',0,'Win11_25H2_Japanese_ARM64.iso','Win11upd_25H2_Japanese_ARM64_pbqbowfj'),
(11,'ko-KR','0412','Korean',0,'Win11_25H2_Korean_ARM64.iso','Win11upd_25H2_Korean_ARM64_pbqbowfj6h'),
(11,'lt-LT','0427','Lithuanian',0,'Win11_25H2_Lithuanian_ARM64.iso','Win11upd_25H2_Lithuanian_ARM64_pbqbow'),
(11,'lv-LV','0426','Latvian',0,'Win11_25H2_Latvian_ARM64.iso','Win11upd_25H2_Latvian_ARM64_pbqbowfj6'),
(11,'nb-NO','0414','Norwegian',0,'Win11_25H2_Norwegian_ARM64.iso','Win11upd_25H2_Norwegian_ARM64_pbqbowf'),
(11,'nl-NL','0413','Dutch',0,'Win11_25H2_Dutch_ARM64.iso','Win11upd_25H2_Dutch_ARM64_pbqbowfj6h'),
(11,'pl-PL','0415','Polish',0,'Win11_25H2_Polish_ARM64.iso','Win11upd_25H2_Polish_ARM64_pbqbowfj6h'),
(11,'pt-PT','0816','Portuguese - Portugal',0,'Win11_25H2_Portuguese_Portugal_ARM64.iso','Win11upd_25H2_Portuguese_Portugal_ARM64'),
(11,'pt-BR','0416','Portuguese - Brazil',0,'Win11_25H2_Portuguese_Brazil_ARM64.iso','Win11upd_25H2_Portuguese_Brazil_ARM64'),
(11,'ru-RU','0419','Russian',0,'Win11_25H2_Russian_ARM64.iso','Win11upd_25H2_Russian_ARM64_pbqbowfj6'),
(11,'sv-SE','041D','Swedish',0,'Win11_25H2_Swedish_ARM64.iso','Win11upd_25H2_Swedish_ARM64_pbqbowfj6'),
(11,'th-TH','041E','Thai',0,'Win11_25H2_Thai_ARM64.iso','Win11upd_25H2_Thai_ARM64_pbqbowfj6h9'),
(11,'tr-TR','041F','Turkish',0,'Win11_25H2_Turkish_ARM64.iso','Win11upd_25H2_Turkish_ARM64_pbqbowfj6'),
(11,'uk-UA','0422','Ukrainian',0,'Win11_25H2_Ukrainian_ARM64.iso','Win11upd_25H2_Ukrainian_ARM64_pbqbowf'),
(11,'zh-CN','0804','Chinese - Simplified',0,'Win11_25H2_Chinese_Simplified_ARM64.iso','Win11upd_25H2_Chinese_Simplified_ARM64'),
(11,'zh-TW','0404','Chinese - Traditional',0,'Win11_25H2_Chinese_Traditional_ARM64.iso','Win11upd_25H2_Chinese_Traditional_ARM64');
*/

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 98;


commit;
