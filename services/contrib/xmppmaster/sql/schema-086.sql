--
-- (c) 2021 Siveo, http://www.siveo.net/
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

-- ----------------------------------------------------------------------
-- Database xmppmaster
-- ----------------------------------------------------------------------

START TRANSACTION;
USE `xmppmaster`;


-- ----------------------------------------------------------------------
-- up_search_kb_update stored procedure
-- ----------------------------------------------------------------------
USE `xmppmaster`;
DROP procedure IF EXISTS `up_search_kb_update`;

DELIMITER $$
CREATE PROCEDURE `up_search_kb_update`(in tablesearch varchar(1024), in KB_LIST varchar(2048) )
BEGIN
	  DECLARE result VARCHAR(50);
      CASE 
      WHEN tablesearch IN ( 'up_packages_Win10_X64_21H1',
							'up_packages_Win10_X64_21H2',
						    'up_packages_Win10_X64_22H2',
						    'up_packages_Win11_X64', 
                            'up_packages_Win10_X64_1903') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				",tablesearch," vv
					INNER JOIN
				(SELECT 
					*
				FROM
					",tablesearch,"
				WHERE
					supersededby = ''
				GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 9)
				ORDER BY revisionid DESC) ee ON ee.updateid = vv.updateid
			WHERE
				vv.KB NOT IN (",KB_LIST,");");
	WHEN  tablesearch IN ( 'up_packages_office_2003_64bit',
						   'up_packages_office_2007_64bit',
						   'up_packages_office_2010_64bit',
						   'up_packages_office_2013_64bit',
						   'up_packages_office_2016_64bit') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				",tablesearch," vv
					INNER JOIN
				(SELECT 
					*
				FROM
					",tablesearch,"
				WHERE
					supersededby = '' 
					and updateclassification like 'Security Updates' 
				   GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 31)
					ORDER BY revisionid DESC) ee ON ee.updateid = vv.updateid
					where  
					vv.updateclassification like 'Security Updates'
                    AND vv.KB NOT IN (",KB_LIST,");");

    
	WHEN  tablesearch IN ( 'up_packages_Vstudio_2005',
						   'up_packages_Vstudio_2008',
                           'up_packages_Vstudio_2010',
                           'up_packages_Vstudio_2012',
                           'up_packages_Vstudio_2013',
                           'up_packages_Vstudio_2015',
                           'up_packages_Vstudio_2017',
                           'up_packages_Vstudio_2019',
                           'up_packages_Vstudio_2022') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				",tablesearch," vv
					INNER JOIN
				(SELECT 
					*
				FROM
					",tablesearch,"
				WHERE
					supersededby = '' 
					and updateclassification like 'Security Updates' 
				   GROUP BY SUBSTRING(SUBSTRING_INDEX(title, '(', 1), 38)
					ORDER BY revisionid DESC) ee ON ee.updateid = vv.updateid
					where  
					vv.updateclassification like 'Security Updates'
                    AND vv.KB NOT IN (",KB_LIST,");");
	WHEN  tablesearch IN ( 'up_packages_Win_Malicious_X64') THEN
		SET @query = concat("
			SELECT 
				*
			FROM
				xmppmaster.up_packages_Win_Malicious_X64
			WHERE 
				KB NOT IN (",KB_LIST,")
			ORDER BY revisionid DESC
			LIMIT 1;");
	ELSE
		SET @query = concat("SELECT * FROM xmppmaster.update_data");
	END CASE;   
 PREPARE stmt FROM @query;
 EXECUTE stmt ;
END$$

DELIMITER ;
;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 86;

COMMIT;
