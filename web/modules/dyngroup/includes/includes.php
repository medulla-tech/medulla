<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/base/includes/computers.inc.php");
require_once("modules/base/includes/computers_list.inc.php");

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require_once("modules/dyngroup/includes/utilities.php");
require_once("modules/dyngroup/includes/querymanager_xmlrpc.php");
require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/request.php");
require_once("modules/dyngroup/includes/dyngroup.php");

?>
