<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php

require("../../../includes/config.inc.php");



require("../../../includes/i18n.inc.php");
require("../../../modules/base/includes/edit.inc.php");
require("../../../includes/acl.inc.php");
require("../../../includes/session.inc.php");
//require("../../../includes/CheckBoxGroup.php");


require("../../../modules/base/includes/users.inc.php");
require("../../../modules/base/includes/groups.inc.php");


$value = $_POST["value"];

print '<ul>';
//print '<li>coin</li>';
foreach(search_groups($value) as $items) {

//foreach($_POST as $key =>$value) {
   ?> <li><?= $items[0]?><span class="informal"><br><?= $items[1]?></span></li>
   <?php
}
print '</ul>';
?>
