<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: searchbar.php
 */

require_once("logging-xmlrpc.inc.php");
require_once("includes/auditCodesManager.php");
$auditManager = new AuditCodesManager();

if($_GET["filtertype"] == "object" or $_GET["filtertype"] == "user"){
?>

    <span class="searchfield"><input type="text" class="searchfieldreal" style="width : 100px;" name="param" id="param" onkeyup="pushSearch(); return false;" />
    <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'base'); ?>"
    onclick="document.getElementById('param').value =''; pushSearch(); return false;"></button>
    </span>

<?php
}
else {
    $lst=array();
    if($_GET["filtertype"]=="action") {
        $lst=get_action_type(1,0);
    }
    else if($_GET["filtertype"]=="type") {
        $lst=get_action_type(0,1);
    }
?>
    <select style="width:100px; vertical-align: middle;" name="param" id="param" onChange="pushSearch(); return false;">
<?php
    foreach ($lst as $key => $item){
        print "\t<option value=\"".$lst[$key]."\" >".$auditManager->getCode($item)."</option>\n";
    }
?>
    </select>
<?php
}
