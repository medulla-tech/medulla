<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
require("graph/navbar.inc.php");
require("localSidebar.php");

/*
 * Display right top shortcuts menu
 */
right_top_shortcuts_display();

$p = new PageGenerator(_T("Browse files", 'backuppc') . ' (' . $_GET['cn'] . ')');
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/backuppc/includes/xmlrpc.php");

$params = array('host' => $_GET['host'], 'sharename' => $_GET['sharename'], 'backupnum' => $_GET['backupnum']);

$ajax = new AjaxFilterLocation(urlStrRedirect("backuppc/backuppc/ajaxBrowseFiles"), 'container', 'location', $params);

$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();


// Downloaded files table
include("modules/backuppc/backuppc/ajaxDownloadsTable.php");
?>

<div id="restoreDiv"></div>

<script type="text/javascript">
    function BrowseDir(dir) {
        jQuery('#<?php echo $ajax->divid; ?>').load('<?php echo $ajax->url; ?>folder=' + encodeURIComponent(dir) + '<?php echo $ajax->params ?>');
    }

    function RestoreFile(paramstr) {
        jQuery('#restoreDiv').load('<?php echo urlStrRedirect("backuppc/backuppc/ajaxRestoreFile"); ?>&' + paramstr);
        setTimeout("refresh();closePopup();", 4000);
    }

    function refresh() {
        jQuery('div#downloadTable').load("<?php echo 'main.php?module=backuppc&submod=backuppc&action=ajaxDownloadsTable&host=' . $_GET['host']; ?>");
    }



</script>
<!-- jQuery('#container').append('<div style="float:left;top: 0;left: 0;width:100%;height:100%;background:#fff;opacity:0.4;z-index:9999;">LOADING</div>'); -->

<style>
    .noborder { border:0px solid blue; }
</style>
