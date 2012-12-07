<?

/*
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

include('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

$item_uuid = $_GET['itemid'];
$location = getCurrentLocation();
$label = urldecode($_GET['itemlabel']);

if ($_POST) {
    $menu_item_id = $_POST['menu_item_id'];
    $ret = xmlrpc_delImageToLocation($menu_item_id, $location);
    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Image <strong>%s</strong> removed from default boot menu.", "imaging"), $label);
        new NotifyWidgetSuccess($str);
        // Synchronize boot menu
        $ret = xmlrpc_synchroLocation($location);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for package server: %s", "imaging"), implode(', ', $ret[1])));
        }
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    } elseif ($ret[0]) {
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    } else {
        new NotifyWidgetFailure($ret[1]);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    }
}

list($count, $masters) = xmlrpc_getLocationImages($location);
$menu_item_id = '';

foreach ($masters as $master) {
    if ($master['imaging_uuid'] == $item_uuid) {
        $menu_item_id = $master['menu_item']['id'];
        break;
    }
}

?>
<h2><?php echo  _T("Remove master", "imaging") ?></h2>
<form action="<?php echo urlStr("imaging/manage/master_remove") ?>" method="post">
    <p><?php printf(_T("Are you sure you want to remove <b>%s</b> master ?", "imaging"), $label); ?></p>
    <input name='menu_item_id' type='hidden' value="<?php echo  $menu_item_id ?>" />
    <input name='valid' type="submit" class="btnPrimary" value="<?php echo  _T("Remove", "imaging"); ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo  _T("Cancel", "imaging"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>
