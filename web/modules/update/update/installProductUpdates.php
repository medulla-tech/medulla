<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2013 Mandriva, http://www.mandriva.com
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php

require_once("modules/update/includes/xmlrpc.inc.php");
require_once("modules/update/includes/html.inc.php");
require_once("graph/navbar.inc.php");

installProductUpdates();

// ============================================================

$MMCApp = & MMCApp::getInstance();

$p = new PageGenerator(_T("Installing updates ...", 'update'));
$p->display();

?>
<div id="update_status"></div>
<script type="text/javascript">
    var update_status = function(){
	jQuery('#update_status').load('<?php print urlStrRedirect("update/update/ajaxInstallProductUpdates"); ?>');
	setTimeout(update_status, 500);
    };
    update_status();
    
</script>