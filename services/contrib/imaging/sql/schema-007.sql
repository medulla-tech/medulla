--
-- (c) 2012 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Medulla 2, http://medulla.mandriva.org
--
-- Medulla 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Medulla 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Medulla 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

SET SESSION character_set_server=UTF8;
SET NAMES 'utf8';

-- Add custom_menu field
ALTER TABLE  `Menu` ADD  `custom_menu` TINYINT NOT NULL DEFAULT  '0' AFTER  `hidden_menu`;

-- Add pxe_password and pxe_keymap to Entity table
ALTER TABLE  `Entity` ADD  `pxe_password` VARCHAR( 255 ) NOT NULL DEFAULT  '',
                      ADD  `pxe_keymap` VARCHAR( 10 ) NOT NULL DEFAULT  'C';

-- Adding keymap field for languages (and setting it for existing records)
ALTER TABLE  `Language` ADD  `keymap` VARCHAR( 10 ) NOT NULL;
UPDATE  `Language` SET  `keymap` =  'C' WHERE  `id` =1;
UPDATE  `Language` SET  `keymap` =  'fr_FR' WHERE  `id` =2;
UPDATE  `Language` SET  `keymap` =  'pt_BR' WHERE  `id` =3;
UPDATE  `Language` SET  `keymap` =  'de_DE' WHERE  `id` =4;

UPDATE version set Number = 7;
