--
-- (c) 2013 Mandriva, http://www.mandriva.com/
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

-- new phases lock_reboot an unlock_reboot added.


ALTER TABLE `commands_history` \
      MODIFY phase ENUM('wol',
	                'pre_menu',
			'post_menu',
			'upload',
			'execute',
			'delete',
			'inventory',
			'reboot',
			'halt',
			'wu_parse',
			'pause',
			'unlock_reboot',
			'lock_reboot',
			'done') DEFAULT NULL;


UPDATE version SET Number = 28;
