<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id: infoPackage.inc.php 8 2006-11-13 11:08:22Z cedric $
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

global $table, $label, $filter;

require("localSidebar.php");
require("graph/navbar.inc.php");

/**
 * provide navigation in ajax for user
 */

?>

<form name="inventoryForm" id="inventoryForm" action="#">

	<div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

	<div id="searchSpan" class="searchbox" style="float: right;">
		<img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" /> 
		<span class="searchfield">
			<input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearchMachine('<?php echo "$table', '$label', '$filter"; ?>'); return false;" />
			<img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;" onclick="document.getElementById('param').value =''; pushSearch(); return false;" />
		</span>
	</div>

<?php

$p = new PageGenerator($label._T(" list"));
$p->setSideMenu($sidemenu);
$p->display(); 

?>
<a href='<?= urlStr("inventory/inventory/csv", array('table'=>$table)) ?>'><img src='modules/inventory/graph/csv.png' alt='export csv'/></a>
<?php

require("javascript.php");

?>

<script type="text/javascript">
<?php
	echo "pushSearchMachine('$table', '$label', '$filter');";
?>
</script>
</form>

<div id="inventoryContainer">
</div>


