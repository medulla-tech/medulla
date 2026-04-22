--
-- (c) 2026, http://www.medulla-tech.io/
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
-- FILE contrib/xmppmaster/sql/schema-101.sql
-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;

-- Drop the existing primary key from the table `xmppmaster`.`up_packages_major_Lang_code`
ALTER TABLE `xmppmaster`.`up_packages_major_Lang_code` 
DROP PRIMARY KEY,
-- Add a new composite primary key consisting of `lang_code`, `major`, and `iso_filename`
ADD PRIMARY KEY (`lang_code`, `major`, `iso_filename`);



INSERT INTO `up_packages_major_Lang_code` VALUES
(11,'ar-SA','0401','Arabic',0,'Win11_24H2_Arabic_x64.iso','Win11upd_24H2_Arabicx64_pbqbowfj6h9l'),
(11,'bg-BG','0402','Bulgarian',0,'Win11_24H2_Bulgarian_x64.iso','Win11upd_24H2_Bulgarianx64_pbqbowfj6'),
(11,'cs-CZ','0405','Czech',0,'Win11_24H2_Czech_x64.iso','Win11upd_24H2_Czechx64_pbqbowfj6h9lo'),
(11,'da-DK','0406','Danish',0,'Win11_24H2_Danish_x64.iso','Win11upd_24H2_Danishx64_pbqbowfj6h9l'),
(11,'de-DE','0407','German',0,'Win11_24H2_German_x64.iso','Win11upd_24H2_Germanx64_pbqbowfj6h9l'),
(11,'el-GR','0408','Greek',0,'Win11_24H2_Greek_x64.iso','Win11upd_24H2_Greekx64_pbqbowfj6h9lo'),
(11,'en-GB','0809','English - United Kingdom',1,'Win11_24H2_English_x64.iso','Win11upd_24H2_Englishx64_pbqbowfj6h9'),
(11,'en-US','0409','English',1,'Win11_24H2_EnglishInternational_x64.iso','Win11upd_24H2_EnglishInternationalx6'),
(11,'es-ES','040A','Spanish',0,'Win11_24H2_Spanish_x64.iso','Win11upd_24H2_Spanishx64_pbqbowfj6h9'),
(11,'es-MX','080A','Spanish - Mexico',0,'Win11_24H2_Spanish_Mexico_x64.iso','Win11upd_24H2_Spanish_Mexicox64_pbqb'),
(11,'et-EE','0425','Estonian - Estonia',0,'Win11_24H2_Estonian_x64.iso','Win11upd_24H2_Estonianx64_pbqbowfj6h'),
(11,'fi-FI','040E','Finnish',0,'Win11_24H2_Finnish_x64.iso','Win11upd_24H2_Finnishx64_pbqbowfj6h9'),
(11,'fr-CA','0C0C','French - Canada',0,'Win11_24H2_FrenchCanadian_x64.iso','Win11upd_24H2_FrenchCanadianx64_pbqb'),
(11,'fr-FR','040C','French',1,'Win11_24H2_French_x64.iso','Win11upd_24H2_Frenchx64_pbqbowfj6h9l'),
(11,'he-IL','040D','Hebrew',0,'Win11_24H2_Hebrew_x64.iso','Win11upd_24H2_Hebrewx64_pbqbowfj6h9l'),
(11,'hi-IN','0439','Hindi',0,'Win11_24H2_Hindi_x64.iso','Win11upd_24H2_Hindix64_pbqbowfj6h9lo'),
(11,'hr-HR','041A','Croatian',0,'Win11_24H2_Croatian_x64.iso','Win11upd_24H2_Croatianx64_pbqbowfj6h'),
(11,'hu-HU','040E','Hungarian',0,'Win11_24H2_Hungarian_x64.iso','Win11upd_24H2_Hungarianx64_pbqbowfj6'),
(11,'it-IT','0410','Italian',0,'Win11_24H2_Italian_x64.iso','Win11upd_24H2_Italianx64_pbqbowfj6h9'),
(11,'ja-JP','0411','Japanese',0,'Win11_24H2_Japanese_x64.iso','Win11upd_24H2_Japanesex64_pbqbowfj6h'),
(11,'ko-KR','0412','Korean',0,'Win11_24H2_Korean_x64.iso','Win11upd_24H2_Koreanx64_pbqbowfj6h9l'),
(11,'lt-LT','0427','Lithuanian',0,'Win11_24H2_Lithuanian_x64.iso','Win11upd_24H2_Lithuanianx64_pbqbowfj'),
(11,'lv-LV','0426','Latvian',0,'Win11_24H2_Latvian_x64.iso','Win11upd_24H2_Latvianx64_pbqbowfj6h9'),
(11,'nb-NO','0414','Norwegian',0,'Win11_24H2_Norwegian_x64.iso','Win11upd_24H2_Norwegianx64_pbqbowfj6'),
(11,'nl-NL','0413','Dutch',0,'Win11_24H2_Dutch_x64.iso','Win11upd_24H2_Dutchx64_pbqbowfj6h9lo'),
(11,'pl-PL','0415','Polish',0,'Win11_24H2_Polish_x64.iso','Win11upd_24H2_Polishx64_pbqbowfj6h9l'),
(11,'pt-PT','0416','Portuguese - Portugal',0,'Win11_24H2_Portuguese_x64.iso','Win11upd_24H2_Portuguesex64_pbqbowfj'),
(11,'ru-RU','0419','Russian',0,'Win11_24H2_Russian_x64.iso','Win11upd_24H2_Russianx64_pbqbowfj6h9'),
(11,'sv-SE','041D','Swedish',0,'Win11_24H2_Swedish_x64.iso','Win11upd_24H2_Swedishx64_pbqbowfj6h9'),
(11,'th-TH','041E','Thai',0,'Win11_24H2_Thai_x64.iso','Win11upd_24H2_Thaix64_pbqbowfj6h9lom'),
(11,'tr-TR','041F','Turkish',0,'Win11_24H2_Turkish_x64.iso','Win11upd_24H2_Turkishx64_pbqbowfj6h9'),
(11,'uk-UA','0422','Ukrainian',0,'Win11_24H2_Ukrainian_x64.iso','Win11upd_24H2_Ukrainian_x64_pbqbowfj'),
(11,'zh-CHT','7C04','Chinese - Traditional',0,'Win11_24H2_Chinese_Traditional_x64.iso','Win11upd_24H2_Chinese_Traditionalx64'),
(11,'zh-CN','0804','Chinese (Simplified) - China',0,'Win11_24H2_Chinese_Simplified_x64.iso','Win11upd_24H2_Chinese_Simplifiedx64_');
--
-- Dumping data for table `up_packages_major_Lang_code` for windows 10
--
INSERT INTO up_packages_major_Lang_code (major, lang_code, num_code, country, enabled, iso_filename, package_uuid) VALUES
(10, 'ar-SA', '0401', 'Arabic', 0, 'Win10_22H2_Arabic_x64.iso', 'Win10upd_22H2_Arabicx64_pbqbowfj6h9l'),
(10, 'bg-BG', '0402', 'Bulgarian', 0, 'Win10_22H2_Bulgarian_x64.iso', 'Win10upd_22H2_Bulgarianx64_pbqbowfj6'),
(10, 'cs-CZ', '0405', 'Czech', 0, 'Win10_22H2_Czech_x64.iso', 'Win10upd_22H2_Czechx64_pbqbowfj6h9lo'),
(10, 'da-DK', '0406', 'Danish', 0, 'Win10_22H2_Danish_x64.iso', 'Win10upd_22H2_Danishx64_pbqbowfj6h9l'),
(10, 'de-DE', '0407', 'German', 0, 'Win10_22H2_German_x64.iso', 'Win10upd_22H2_Germanx64_pbqbowfj6h9l'),
(10, 'el-GR', '0408', 'Greek', 0, 'Win10_22H2_Greek_x64.iso', 'Win10upd_22H2_Greekx64_pbqbowfj6h9lo'),
(10, 'en-GB', '0809', 'English - United Kingdom', 1, 'Win10_22H2_English_x64.iso', 'Win10upd_22H2_Englishx64_pbqbowfj6h9'),
(10, 'en-US', '0409', 'English', 1, 'Win10_22H2_EnglishInternational_x64.iso', 'Win10upd_22H2_EnglishInternationalx6'),
(10, 'es-ES', '040A', 'Spanish', 0, 'Win10_22H2_Spanish_x64.iso', 'Win10upd_22H2_Spanishx64_pbqbowfj6h9'),
(10, 'es-MX', '080A', 'Spanish - Mexico', 0, 'Win10_22H2_Spanish_Mexico_x64.iso', 'Win10upd_22H2_Spanish_Mexicox64_pbqb'),
(10, 'et-EE', '0425', 'Estonian - Estonia', 0, 'Win10_22H2_Estonian_x64.iso', 'Win10upd_22H2_Estonianx64_pbqbowfj6h'),
(10, 'fi-FI', '040E', 'Finnish', 0, 'Win10_22H2_Finnish_x64.iso', 'Win10upd_22H2_Finnishx64_pbqbowfj6h9'),
(10, 'fr-CA', '0C0C', 'French - Canada', 0, 'Win10_22H2_FrenchCanadian_x64.iso', 'Win10upd_22H2_FrenchCanadianx64_pbqb'),
(10, 'fr-FR', '040C', 'French', 1, 'Win10_22H2_French_x64.iso', 'Win10upd_22H2_Frenchx64_pbqbowfj6h9l'),
(10, 'he-IL', '040D', 'Hebrew', 0, 'Win10_22H2_Hebrew_x64.iso', 'Win10upd_22H2_Hebrewx64_pbqbowfj6h9l'),
(10, 'hi-IN', '0439', 'Hindi', 0, 'Win10_22H2_Hindi_x64.iso', 'Win10upd_22H2_Hindix64_pbqbowfj6h9lo'),
(10, 'hr-HR', '041A', 'Croatian', 0, 'Win10_22H2_Croatian_x64.iso', 'Win10upd_22H2_Croatianx64_pbqbowfj6h'),
(10, 'hu-HU', '040E', 'Hungarian', 0, 'Win10_22H2_Hungarian_x64.iso', 'Win10upd_22H2_Hungarianx64_pbqbowfj6'),
(10, 'it-IT', '0410', 'Italian', 0, 'Win10_22H2_Italian_x64.iso', 'Win10upd_22H2_Italianx64_pbqbowfj6h9'),
(10, 'ja-JP', '0411', 'Japanese', 0, 'Win10_22H2_Japanese_x64.iso', 'Win10upd_22H2_Japanesex64_pbqbowfj6h'),
(10, 'ko-KR', '0412', 'Korean', 0, 'Win10_22H2_Korean_x64.iso', 'Win10upd_22H2_Koreanx64_pbqbowfj6h9l'),
(10, 'lt-LT', '0427', 'Lithuanian', 0, 'Win10_22H2_Lithuanian_x64.iso', 'Win10upd_22H2_Lithuanianx64_pbqbowfj'),
(10, 'lv-LV', '0426', 'Latvian', 0, 'Win10_22H2_Latvian_x64.iso', 'Win10upd_22H2_Latvianx64_pbqbowfj6h9'),
(10, 'nb-NO', '0414', 'Norwegian', 0, 'Win10_22H2_Norwegian_x64.iso', 'Win10upd_22H2_Norwegianx64_pbqbowfj6'),
(10, 'nl-NL', '0413', 'Dutch', 0, 'Win10_22H2_Dutch_x64.iso', 'Win10upd_22H2_Dutchx64_pbqbowfj6h9lo'),
(10, 'pl-PL', '0415', 'Polish', 0, 'Win10_22H2_Polish_x64.iso', 'Win10upd_22H2_Polishx64_pbqbowfj6h9l'),
(10, 'pt-PT', '0416', 'Portuguese - Portugal', 0, 'Win10_22H2_Portuguese_x64.iso', 'Win10upd_22H2_Portuguesex64_pbqbowfj'),
(10, 'ru-RU', '0419', 'Russian', 0, 'Win10_22H2_Russian_x64.iso', 'Win10upd_22H2_Russianx64_pbqbowfj6h9'),
(10, 'sv-SE', '041D', 'Swedish', 0, 'Win10_22H2_Swedish_x64.iso', 'Win10upd_22H2_Swedishx64_pbqbowfj6h9'),
(10, 'th-TH', '041E', 'Thai', 0, 'Win10_22H2_Thai_x64.iso', 'Win10upd_22H2_Thaix64_pbqbowfj6h9lom'),
(10, 'tr-TR', '041F', 'Turkish', 0, 'Win10_22H2_Turkish_x64.iso', 'Win10upd_22H2_Turkishx64_pbqbowfj6h9'),
(10, 'uk-UA', '0422', 'Ukrainian', 0, 'Win10_22H2_Ukrainian_x64.iso', 'Win10upd_22H2_Ukrainian_x64_pbqbowfj'),
(10, 'zh-CHT', '7C04', 'Chinese - Traditional', 0, 'Win10_22H2_Chinese_Traditional_x64.iso', 'Win10upd_22H2_Chinese_Traditionalx64'),
(10, 'zh-CN', '0804', 'Chinese (Simplified) - China', 0, 'Win10_22H2_Chinese_Simplified_x64.iso', 'Win10upd_22H2_Chinese_Simplifiedx64_');

INSERT INTO up_packages_major_Lang_code (major, lang_code, num_code, country, enabled, iso_filename, package_uuid) VALUES
('10', 'ar-SA', '0401', 'Arabic', 0, 'Win10_22H2_Arabic_x64.iso', 'Win10upd_22H2_Arabicx64_pbqbowfj6h9l'),
('10', 'bg-BG', '0402', 'Bulgarian', 0, 'Win10_22H2_Bulgarian_x64.iso', 'Win10upd_22H2_Bulgarianx64_pbqbowfj6'),
('10', 'cs-CZ', '0405', 'Czech', 0, 'Win10_22H2_Czech_x64.iso', 'Win10upd_22H2_Czechx64_pbqbowfj6h9lo'),
('10', 'da-DK', '0406', 'Danish', 0, 'Win10_22H2_Danish_x64.iso', 'Win10upd_22H2_Danishx64_pbqbowfj6h9l'),
('10', 'de-DE', '0407', 'German', 0, 'Win10_22H2_German_x64.iso', 'Win10upd_22H2_Germanx64_pbqbowfj6h9l'),
('10', 'el-GR', '0408', 'Greek', 0, 'Win10_22H2_Greek_x64.iso', 'Win10upd_22H2_Greekx64_pbqbowfj6h9lo'),
('10', 'en-GB', '0809', 'English - United Kingdom', 1, 'Win10_22H2_English_x64.iso', 'Win10upd_22H2_Englishx64_pbqbowfj6h9'),
('10', 'en-US', '0409', 'English', 1, 'Win10_22H2_EnglishInternational_x64.iso', 'Win10upd_22H2_EnglishInternationalx6'),
('10', 'es-ES', '040A', 'Spanish', 0, 'Win10_22H2_Spanish_x64.iso', 'Win10upd_22H2_Spanishx64_pbqbowfj6h9'),
('10', 'es-MX', '080A', 'Spanish - Mexico', 0, 'Win10_22H2_Spanish_Mexico_x64.iso', 'Win10upd_22H2_Spanish_Mexicox64_pbqb'),
('10', 'et-EE', '0425', 'Estonian - Estonia', 0, 'Win10_22H2_Estonian_x64.iso', 'Win10upd_22H2_Estonianx64_pbqbowfj6h'),
('10', 'fi-FI', '040E', 'Finnish', 0, 'Win10_22H2_Finnish_x64.iso', 'Win10upd_22H2_Finnishx64_pbqbowfj6h9'),
('10', 'fr-CA', '0C0C', 'French - Canada', 0, 'Win10_22H2_FrenchCanadian_x64.iso', 'Win10upd_22H2_FrenchCanadianx64_pbqb'),
('10', 'fr-FR', '040C', 'French', 1, 'Win10_22H2_French_x64.iso', 'Win10upd_22H2_Frenchx64_pbqbowfj6h9l'),
('10', 'he-IL', '040D', 'Hebrew', 0, 'Win10_22H2_Hebrew_x64.iso', 'Win10upd_22H2_Hebrewx64_pbqbowfj6h9l'),
('10', 'hi-IN', '0439', 'Hindi', 0, 'Win10_22H2_Hindi_x64.iso', 'Win10upd_22H2_Hindix64_pbqbowfj6h9lo'),
('10', 'hr-HR', '041A', 'Croatian', 0, 'Win10_22H2_Croatian_x64.iso', 'Win10upd_22H2_Croatianx64_pbqbowfj6h'),
('10', 'hu-HU', '040E', 'Hungarian', 0, 'Win10_22H2_Hungarian_x64.iso', 'Win10upd_22H2_Hungarianx64_pbqbowfj6'),
('10', 'it-IT', '0410', 'Italian', 0, 'Win10_22H2_Italian_x64.iso', 'Win10upd_22H2_Italianx64_pbqbowfj6h9'),
('10', 'ja-JP', '0411', 'Japanese', 0, 'Win10_22H2_Japanese_x64.iso', 'Win10upd_22H2_Japanesex64_pbqbowfj6h'),
('10', 'ko-KR', '0412', 'Korean', 0, 'Win10_22H2_Korean_x64.iso', 'Win10upd_22H2_Koreanx64_pbqbowfj6h9l'),
('10', 'lt-LT', '0427', 'Lithuanian', 0, 'Win10_22H2_Lithuanian_x64.iso', 'Win10upd_22H2_Lithuanianx64_pbqbowfj'),
('10', 'lv-LV', '0426', 'Latvian', 0, 'Win10_22H2_Latvian_x64.iso', 'Win10upd_22H2_Latvianx64_pbqbowfj6h9'),
('10', 'nb-NO', '0414', 'Norwegian', 0, 'Win10_22H2_Norwegian_x64.iso', 'Win10upd_22H2_Norwegianx64_pbqbowfj6'),
('10', 'nl-NL', '0413', 'Dutch', 0, 'Win10_22H2_Dutch_x64.iso', 'Win10upd_22H2_Dutchx64_pbqbowfj6h9lo'),
('10', 'pl-PL', '0415', 'Polish', 0, 'Win10_22H2_Polish_x64.iso', 'Win10upd_22H2_Polishx64_pbqbowfj6h9l'),
('10', 'pt-PT', '0416', 'Portuguese - Portugal', 0, 'Win10_22H2_Portuguese_x64.iso', 'Win10upd_22H2_Portuguesex64_pbqbowfj'),
('10', 'ru-RU', '0419', 'Russian', 0, 'Win10_22H2_Russian_x64.iso', 'Win10upd_22H2_Russianx64_pbqbowfj6h9'),
('10', 'sv-SE', '041D', 'Swedish', 0, 'Win10_22H2_Swedish_x64.iso', 'Win10upd_22H2_Swedishx64_pbqbowfj6h9'),
('10', 'th-TH', '041E', 'Thai', 0, 'Win10_22H2_Thai_x64.iso', 'Win10upd_22H2_Thaix64_pbqbowfj6h9lom'),
('10', 'tr-TR', '041F', 'Turkish', 0, 'Win10_22H2_Turkish_x64.iso', 'Win10upd_22H2_Turkishx64_pbqbowfj6h9'),
('10', 'uk-UA', '0422', 'Ukrainian', 0, 'Win10_22H2_Ukrainian_x64.iso', 'Win10upd_22H2_Ukrainian_x64_pbqbowfj'),
('10', 'zh-CHT', '7C04', 'Chinese - Traditional', 0, 'Win10_22H2_Chinese_Traditional_x64.iso', 'Win10upd_22H2_Chinese_Traditionalx64'),
('10', 'zh-CN', '0804', 'Chinese (Simplified) - China', 0, 'Win10_22H2_Chinese_Simplified_x64.iso', 'Win10upd_22H2_Chinese_Simplifiedx64_');

--
-- Dumping data for table `up_packages_major_Lang_code` for windows 11
--
INSERT INTO `up_packages_major_Lang_code` VALUES
('11','ar-SA','0401','Arabic',0,'Win11_24H2_Arabic_x64.iso','Win11upd_24H2_Arabicx64_pbqbowfj6h9l'),
('11','bg-BG','0402','Bulgarian',0,'Win11_24H2_Bulgarian_x64.iso','Win11upd_24H2_Bulgarianx64_pbqbowfj6'),
('11','cs-CZ','0405','Czech',0,'Win11_24H2_Czech_x64.iso','Win11upd_24H2_Czechx64_pbqbowfj6h9lo'),
('11','da-DK','0406','Danish',0,'Win11_24H2_Danish_x64.iso','Win11upd_24H2_Danishx64_pbqbowfj6h9l'),
('11','de-DE','0407','German',0,'Win11_24H2_German_x64.iso','Win11upd_24H2_Germanx64_pbqbowfj6h9l'),
('11','el-GR','0408','Greek',0,'Win11_24H2_Greek_x64.iso','Win11upd_24H2_Greekx64_pbqbowfj6h9lo'),
('11','en-GB','0809','English - United Kingdom',1,'Win11_24H2_English_x64.iso','Win11upd_24H2_Englishx64_pbqbowfj6h9'),
('11','en-US','0409','English',1,'Win11_24H2_EnglishInternational_x64.iso','Win11upd_24H2_EnglishInternationalx6'),
('11','es-ES','040A','Spanish',0,'Win11_24H2_Spanish_x64.iso','Win11upd_24H2_Spanishx64_pbqbowfj6h9'),
('11','es-MX','080A','Spanish - Mexico',0,'Win11_24H2_Spanish_Mexico_x64.iso','Win11upd_24H2_Spanish_Mexicox64_pbqb'),
('11','et-EE','0425','Estonian - Estonia',0,'Win11_24H2_Estonian_x64.iso','Win11upd_24H2_Estonianx64_pbqbowfj6h'),
('11','fi-FI','040E','Finnish',0,'Win11_24H2_Finnish_x64.iso','Win11upd_24H2_Finnishx64_pbqbowfj6h9'),
('11','fr-CA','0C0C','French - Canada',0,'Win11_24H2_FrenchCanadian_x64.iso','Win11upd_24H2_FrenchCanadianx64_pbqb'),
('11','fr-FR','040C','French',1,'Win11_24H2_French_x64.iso','Win11upd_24H2_Frenchx64_pbqbowfj6h9l'),
('11','he-IL','040D','Hebrew',0,'Win11_24H2_Hebrew_x64.iso','Win11upd_24H2_Hebrewx64_pbqbowfj6h9l'),
('11','hi-IN','0439','Hindi',0,'Win11_24H2_Hindi_x64.iso','Win11upd_24H2_Hindix64_pbqbowfj6h9lo'),
('11','hr-HR','041A','Croatian',0,'Win11_24H2_Croatian_x64.iso','Win11upd_24H2_Croatianx64_pbqbowfj6h'),
('11','hu-HU','040E','Hungarian',0,'Win11_24H2_Hungarian_x64.iso','Win11upd_24H2_Hungarianx64_pbqbowfj6'),
('11','it-IT','0410','Italian',0,'Win11_24H2_Italian_x64.iso','Win11upd_24H2_Italianx64_pbqbowfj6h9'),
('11','ja-JP','0411','Japanese',0,'Win11_24H2_Japanese_x64.iso','Win11upd_24H2_Japanesex64_pbqbowfj6h'),
('11','ko-KR','0412','Korean',0,'Win11_24H2_Korean_x64.iso','Win11upd_24H2_Koreanx64_pbqbowfj6h9l'),
('11','lt-LT','0427','Lithuanian',0,'Win11_24H2_Lithuanian_x64.iso','Win11upd_24H2_Lithuanianx64_pbqbowfj'),
('11','lv-LV','0426','Latvian',0,'Win11_24H2_Latvian_x64.iso','Win11upd_24H2_Latvianx64_pbqbowfj6h9'),
('11','nb-NO','0414','Norwegian',0,'Win11_24H2_Norwegian_x64.iso','Win11upd_24H2_Norwegianx64_pbqbowfj6'),
('11','nl-NL','0413','Dutch',0,'Win11_24H2_Dutch_x64.iso','Win11upd_24H2_Dutchx64_pbqbowfj6h9lo'),
('11','pl-PL','0415','Polish',0,'Win11_24H2_Polish_x64.iso','Win11upd_24H2_Polishx64_pbqbowfj6h9l'),
('11','pt-PT','0416','Portuguese - Portugal',0,'Win11_24H2_Portuguese_x64.iso','Win11upd_24H2_Portuguesex64_pbqbowfj'),
('11','ru-RU','0419','Russian',0,'Win11_24H2_Russian_x64.iso','Win11upd_24H2_Russianx64_pbqbowfj6h9'),
('11','sv-SE','041D','Swedish',0,'Win11_24H2_Swedish_x64.iso','Win11upd_24H2_Swedishx64_pbqbowfj6h9'),
('11','th-TH','041E','Thai',0,'Win11_24H2_Thai_x64.iso','Win11upd_24H2_Thaix64_pbqbowfj6h9lom'),
('11','tr-TR','041F','Turkish',0,'Win11_24H2_Turkish_x64.iso','Win11upd_24H2_Turkishx64_pbqbowfj6h9'),
('11','uk-UA','0422','Ukrainian',0,'Win11_24H2_Ukrainian_x64.iso','Win11upd_24H2_Ukrainian_x64_pbqbowfj'),
('11','zh-CHT','7C04','Chinese - Traditional',0,'Win11_24H2_Chinese_Traditional_x64.iso','Win11upd_24H2_Chinese_Traditionalx64'),
('11','zh-CN','0804','Chinese (Simplified) - China',0,'Win11_24H2_Chinese_Simplified_x64.iso','Win11upd_24H2_Chinese_Simplifiedx64_');


--
-- Dumping data for table `up_packages_major_Lang_code` for windows server 2025
--

INSERT INTO up_packages_major_Lang_code (major, lang_code, num_code, country, enabled, iso_filename, package_uuid) VALUES
('MSO25', 'ar-SA', '0401', 'Arabic', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Arabic_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Arabicx64_pbqbowfj6h9l'),
('MSO25', 'bg-BG', '0402', 'Bulgarian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Bulgarian_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Bulgarianx64_pbqbowfj6'),
('MSO25', 'cs-CZ', '0405', 'Czech', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Czech_DC_STD_MLF_X23-81889.ISO', 'MSO25upd_24H2_Czechx64_pbqbowfj6h9lo'),
('MSO25', 'da-DK', '0406', 'Danish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Danish_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Danishx64_pbqbowfj6h9l'),
('MSO25', 'de-DE', '0407', 'German', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_German_DC_STD_MLF_X23-81893.ISO', 'MSO25upd_24H2_Germanx64_pbqbowfj6h9l'),
('MSO25', 'el-GR', '0408', 'Greek', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Greek_DC_STD_MLF_X23-81893.ISO', 'MSO25upd_24H2_Greekx64_pbqbowfj6h9lo'),
('MSO25', 'en-GB', '0809', 'English - United Kingdom', 1,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_English_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_Englishx64_pbqbowfj6h9'),
('MSO25', 'en-US', '0409', 'English', 1, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_English_DC_STD_MLF_X23-81891.ISO', 'MSO25upd_24H2_EnglishInternationalx6'),
('MSO25', 'es-ES', '040A', 'Spanish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Spanish_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Spanishx64_pbqbowfj6h9'),
('MSO25', 'es-MX', '080A', 'Spanish - Mexico', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Spanish_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Spanish_Mexicox64_pbqb'),
('MSO25', 'et-EE', '0425', 'Estonian - Estonia', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Estonian_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Estonianx64_pbqbowfj6h'),
('MSO25', 'fi-FI', '040E', 'Finnish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Finnish_DC_STD_MLF_X23-81901.ISO', 'MSO25upd_24H2_Finnishx64_pbqbowfj6h9'),
('MSO25', 'fr-CA', '0C0C', 'French - Canada', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_French_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_FrenchCanadianx64_pbqb'),
('MSO25', 'fr-FR', '040C', 'French', 1, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_French_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Frenchx64_pbqbowfj6h9l'),
('MSO25', 'he-IL', '040D', 'Hebrew', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Hebrew_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Hebrewx64_pbqbowfj6h9l'),
('MSO25', 'hi-IN', '0439', 'Hindi', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Hindi_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Hindix64_pbqbowfj6h9lo'),
('MSO25', 'hr-HR', '041A', 'Croatian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Croatian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Croatianx64_pbqbowfj6h'),
('MSO25', 'hu-HU', '040E', 'Hungarian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Hungarian_DC_STD_MLF_X23-81894.ISO', 'MSO25upd_24H2_Hungarianx64_pbqbowfj6'),
('MSO25', 'it-IT', '0410', 'Italian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Italian_DC_STD_MLF_X23-81895.ISO', 'MSO25upd_24H2_Italianx64_pbqbowfj6h9'),
('MSO25', 'ja-JP', '0411', 'Japanese', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Japanese_DC_STD_MLF_X23-81896.ISO', 'MSO25upd_24H2_Japanesex64_pbqbowfj6h'),
('MSO25', 'ko-KR', '0412', 'Korean', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Korean_DC_STD_MLF_X23-81897.ISO', 'MSO25upd_24H2_Koreanx64_pbqbowfj6h9l'),
('MSO25', 'lt-LT', '0427', 'Lithuanian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Lithuanian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Lithuanianx64_pbqbowfj'),
('MSO25', 'lv-LV', '0426', 'Latvian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Latvian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Latvianx64_pbqbowfj6h9'),
('MSO25', 'nb-NO', '0414', 'Norwegian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Norwegian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Norwegianx64_pbqbowfj6'),
('MSO25', 'nl-NL', '0413', 'Dutch', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Dutch_DC_STD_MLF_X23-81890.ISO', 'MSO25upd_24H2_Dutchx64_pbqbowfj6h9lo'),
('MSO25', 'pl-PL', '0415', 'Polish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Polish_DC_STD_MLF_X23-81898.ISO', 'MSO25upd_24H2_Polishx64_pbqbowfj6h9l'),
('MSO25', 'pt-PT', '0416', 'Portuguese - Portugal', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Portuguese_DC_STD_MLF_X23-81899.ISO', 'MSO25upd_24H2_Portuguesex64_pbqbowfj'),
('MSO25', 'pt-BR', '0416', 'Portuguese - Brazil', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Brazilian_DC_STD_MLF_X23-81886.ISO', 'MSO25upd_24H2_Brazilianx64_pbqbowfj6'),
('MSO25', 'ru-RU', '0419', 'Russian', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Russian_DC_STD_MLF_X23-81900.ISO', 'MSO25upd_24H2_Russianx64_pbqbowfj6h9'),
('MSO25', 'sv-SE', '041D', 'Swedish', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Swedish_DC_STD_MLF_X23-81902.ISO', 'MSO25upd_24H2_Swedishx64_pbqbowfj6h9'),
('MSO25', 'th-TH', '041E', 'Thai', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Thai_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Thaix64_pbqbowfj6h9lom'),
('MSO25', 'tr-TR', '041F', 'Turkish', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Turkish_DC_STD_MLF_X23-81903.ISO', 'MSO25upd_24H2_Turkishx64_pbqbowfj6h9'),
('MSO25', 'uk-UA', '0422', 'Ukrainian', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_Ukrainian_DC_STD_MLF_X23-81892.ISO', 'MSO25upd_24H2_Ukrainian_x64_pbqbowfj'),
('MSO25', 'zh-CHT','7C04', 'Chinese - Traditional', 0, 'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_ChnTrad_DC_STD_MLF_X23-81888.ISO', 'MSO25upd_24H2_Chinese_Traditionalx64'),
('MSO25', 'zh-CN', '0804', 'Chinese (Simplified) - China', 0,'SW_DVD9_Win_Server_STD_CORE_2025_24H2_64Bit_ChnSimp_DC_STD_MLF_X23-81887.ISO', 'MSO25upd_24H2_Chinese_Simplifiedx64_');


INSERT IGNORE INTO `up_packages_major_Lang_code` VALUES
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



-- PROCEDURE : up_init_packages_Windows_Security_platform
-- Description :
--   Cette procedure cree une table temporaire up_packages_Windows_Security_platform
--   filtrée pour Windows Security platform uniquement (titre et produit)

DELIMITER $$
USE `xmppmaster`$$
DROP PROCEDURE IF EXISTS `up_init_packages_Windows_Security_platform`$$
CREATE PROCEDURE `up_init_packages_Windows_Security_platform`()
BEGIN
DROP TABLE IF EXISTS up_packages_Windows_Security_platform;
CREATE TABLE up_packages_Windows_Security_platform AS
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
    JOIN
        xmppmaster.update_data bb ON bb.bundledby_revision = aa.revisionid
    WHERE
        (
            -- Cas 1 : Windows Security platform
            (aa.product LIKE '%Windows Security platform%' AND aa.title LIKE '%Windows Security platform%')
            OR
            -- Cas 2 : Microsoft Defender Antivirus
            (aa.product LIKE '%Microsoft Defender Antivirus%' AND aa.title LIKE '%Microsoft Defender Antivirus%' AND aa.updateclassification = 'Definition Updates')
            OR
            -- Cas 3 : System Center Endpoint Protection
            (aa.product LIKE '%System Center Endpoint Protection%' AND aa.title LIKE '%Security Intelligence Update%' AND aa.updateclassification = 'Definition Updates')
        );
END$$

DELIMITER ;


-- Enregistrement de la procédure dans up_list_produit
INSERT IGNORE INTO `xmppmaster`.`up_list_produit` (`name_procedure`) VALUES ('up_init_packages_Windows_Security_platform');

-- Enregistrement du produit dans applicationconfig (active par defaut)
INSERT IGNORE INTO `xmppmaster`.`applicationconfig` (
    `key`,
    `value`,
    `comment`,
    `context`,
    `module`,
    `enable`
) VALUES (
    'table produits',
    'up_packages_Windows_Security_platform',
    'Windows Security platform',
    'entity',
    'xmppmaster/update',
    1
);

-- Execution de la procédure centrale d'initialisation
-- La procédure up_create_product_tables (définie dans schema-095.sql)
-- parcourt automatiquement l'information_schema et exécute toutes les
-- procédures commençant par up_init_packages_*, y compris la nouvelle.
CALL `xmppmaster`.`up_create_product_tables`();



-- ----------------------------------------------------------------------
-- Database version update
-- ----------------------------------------------------------------------
-- Update the version number to 101 in the `version` table
UPDATE version SET Number = 101;

COMMIT;
