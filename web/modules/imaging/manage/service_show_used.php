<?php

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

require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require_once('modules/imaging/includes/web_def.inc.php');

$location = getCurrentLocation();

/**********************
 * Remove boot services
 **********************/

if (isset($_POST['removeServices'])) {
    $bootServicesToDelFromTarget = array(); // Boot Services who will be removed from a computer
    $bootServicesToDelFromLocation = array(); // Boot Services who will be removed from a imaging server

    foreach ($_POST as $key => $value) {
        if (substr($key, 0, 14) == 'computer_uuid_') {
            $target_uuid = substr($key, 14);
            if (isset($_POST['computer_checkbox_' . $target_uuid]) and $_POST['computer_checkbox_' . $target_uuid] == 'on') {
                $bootServicesToDelFromTarget[] = array(
                    'bs_uuid' => $_POST['computer_uuid_' . $target_uuid],
                    'target_uuid' => $target_uuid,
                    'type' => $_POST['type_uuid_' . $target_uuid],
                );
            }
        }
        if (substr($key, 0, 13) == 'imaging_uuid_') {
            $location = substr($key, 13);
            $target_uuid = substr($key, 13);
            if (isset($_POST['imaging_checkbox_' . $location]) and $_POST['imaging_checkbox_' . $location] == 'on') {
                $bootServicesToDelFromLocation[] = array(
                    'bs_uuid' => $_POST['imaging_uuid_' . $target_uuid],
                    'location' => $location,
                );
            }
        }
    }

    foreach ($bootServicesToDelFromTarget as $boot_service) {
        $ret = xmlrpc_delServiceToTarget($boot_service['bs_uuid'], $boot_service['target_uuid'], $boot_service['type']);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Removal of boot service failed", "imaging")));
        }

        // Synchronize boot menu
        $ret = xmlrpc_synchroComputer($boot_service['target_uuid']);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for computer: %s", "imaging"), implode(', ', $ret[1])));
        }
    }
    foreach ($bootServicesToDelFromLocation as $boot_service) {
        $ret = xmlrpc_delServiceToLocation($boot_service['bs_uuid'], $boot_service['location']);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Removal of boot service failed", "imaging")));
        }

        // Synchronize boot menu
        $ret = xmlrpc_synchroLocation($boot_service['location']);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for package server: %s", "imaging"), implode(', ', $ret[1])));
        }
    }
    if (isset($_POST['uuid']) and isset($_POST['hostname'])) {
        // Come from a computer page
        $params = array(
            'uuid' => $_POST['uuid'],
            'hostname' => $_POST['hostname'],
        );
        header("Location: " . urlStrRedirect("base/computers/".$type."imgtabs/".$type."tabservices", $params));
        exit;
    }
    else {
        // Come from an imaging server page
        header("Location: " . urlStrRedirect("imaging/manage/service"));
        exit;
    }
}

$params = getParams();
$item_uuid = $_GET['itemid'];
$label = urldecode($_GET['itemlabel']);

$targets = xmlrpc_isServiceUsed($item_uuid);

?>
<form name="showTarget" action="<?php echo urlStr("imaging/manage/service_show_used",$params) ?>" method="post">
    <p><?php printf(_T("Show all targets that use that image in their boot menu", "imaging")); ?></p>
<?php

foreach ($targets as $target) {
    if ($target['type'] == -1) { // This is an imaging server
        // Boot Service linked to an imaging server
        $params['location'] = $target['uuid'];
        $url = urlStrRedirect("imaging/manage/service", $params);
        printf('<p><input title="' . _T("Remove this boot service from imaging server %s", "imaging") . '" type="checkbox" name="imaging_checkbox_%s"/>', $target['name'], $target['uuid']);
        printf("<a href='".$url."'>"._T("Imaging server", 'imaging')." : ".$target['name']."</a></p>");
        printf('<input type="hidden" name="imaging_uuid_%s" value="%s"/>', $target['uuid'], $item_uuid);
    }
    else { // Target is a computer
        // boot service linked to a computer
        $params['uuid'] = $target['uuid'];
        $params['hostname'] = $target['name'];
        $url = urlStrRedirect("base/computers/imgtabs/".$type."tabservices", $params);
        printf('<p><input title="' . _T("Remove this master from computer %s", "imaging") . '" type="checkbox" name="computer_checkbox_%s"/>', $target['name'], $target['uuid']);
        printf("<a href='".$url."'>".($target['type']==2?_T('Imaging group', 'imaging'): _T('Computer', 'imaging'))." : ".$target['name']."</a></p>");
        printf('<input type="hidden" name="computer_uuid_%s" value="%s"/>', $target['uuid'], $item_uuid);
        printf('<input type="hidden" name="type_uuid_%s" value="%s"/>', $target['uuid'], $target['type']);
    }
}

if (isset($_GET['from'])) {
    // Come from a computer target page
    printf('<input type="hidden" name="uuid" value="%s"/>', $_GET['target_uuid']);
    printf('<input type="hidden" name="hostname" value="%s"/>', $_GET['hostname']);
}
else {
    // Come from an imaging server page
}
?>
    <hr />
    <p><?php printf(_T("If you want to remove this boot service from one or more targets, check these targets and click on the remove button", "imaging")); ?></p>
    <p><a onclick="checkAll('imaging_checkbox_',1);checkAll('computer_checkbox_',1);" href="javascript:void(0);"><?php printf(_T("Select all", "imaging")); ?></a> 
    / <a onclick="checkAll('imaging_checkbox_',0);checkAll('computer_checkbox_',0);" href="javascript:void(0);"><?php printf(_T("Unselect all", "imaging")); ?></a></p>
    <input name='removeServices' type="submit" class="btnPrimary" value="<?php echo  _T("Remove", "imaging"); ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo  _T("Cancel", "imaging"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>
