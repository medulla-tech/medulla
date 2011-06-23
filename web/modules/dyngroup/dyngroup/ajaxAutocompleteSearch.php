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

require_once("modules/dyngroup/includes/xmlrpc.php");
require_once("modules/dyngroup/includes/utilities.php");
ob_end_clean();

$module = quickGet("modulename");
$criterion = quickGet("criterion");
$search = quickGet("value");
if (!$search) { $search = '' ; }

$value1 = quickGet("value1");
$res = array();
if (strlen($search) > 2) {
    if (strlen($value1)) {
        $res = getPossiblesValuesForCriterionInModuleFuzzyWhere($module, $criterion, $value1, $search);
    } else {
        $res = getPossiblesValuesForCriterionInModuleFuzzy($module, $criterion, $search);
    }
}

print '<ul>';
foreach($res as $items) {
    ?> <li><?php echo  $items?></li> <?php 
}
print '</ul>';

?>
