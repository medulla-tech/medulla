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

include('modules/imaging/includes/includes.php');
include('modules/imaging/includes/xmlrpc.inc.php');

/* * ***************
 * Remove masters
 * ************** */

if (isset($_POST['removeMasters'])) {
    $imagesToDelFromTarget = array(); // Masters who will be removed from a computer
    $imagesToDelFromLocation = array(); // Masters who will be removed from a imaging server

    foreach ($_POST as $key => $value) {
        if (substr($key, 0, 14) == 'computer_uuid_') {
            $target_uuid = substr($key, 14);
            if (isset($_POST['computer_checkbox_' . $target_uuid]) and $_POST['computer_checkbox_' . $target_uuid] == 'on') {
                $imagesToDelFromTarget[] = array(
                    'uuid' => $_POST['computer_uuid_' . $target_uuid],
                    'target_uuid' => $target_uuid,
                    'type' => $_POST['type_uuid_' . $target_uuid],
                );
            }
        }
        if (substr($key, 0, 13) == 'imaging_uuid_') {
            $location = substr($key, 13);
            if (isset($_POST['imaging_checkbox_' . $location]) and $_POST['imaging_checkbox_' . $location] == 'on') {

                list($count, $masters) = xmlrpc_getLocationImages($location);
                $menu_item_id = '';

                foreach ($masters as $master) {
                    if ($master['imaging_uuid'] == $_POST['imaging_uuid_' . $location]) {
                        $menu_item_id = $master['menu_item']['id'];
                        break;
                    }
                }

                $imagesToDelFromLocation[] = array(
                    'menu_item_id' => $menu_item_id,
                    'location' => $location,
                );
            }
        }
    }

    foreach ($imagesToDelFromTarget as $image) {
        $ret = xmlrpc_delImageToTarget($image['uuid'], $image['target_uuid'], $image['type']);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Removal of master failed", "imaging")));
        }

        // Synchronize boot menu
        $ret = xmlrpc_synchroComputer($image['target_uuid']);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Boot menu generation failed for computer: %s", "imaging"), implode(', ', $ret[1])));
        }
    }
    foreach ($imagesToDelFromLocation as $image) {
        $ret = xmlrpc_delImageToLocation($image['menu_item_id'], $image['location']);
        if (isXMLRPCError()) {
            new NotifyWidgetFailure(sprintf(_T("Removal of master failed", "imaging")));
        }

        // Synchronize boot menu
        $ret = xmlrpc_synchroLocation($image['location']);
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
        header("Location: " . urlStrRedirect("base/computers/" . $type . "imgtabs/" . $type . "tabimages", $params));
        exit;
    } else {
        // Come from an imaging server page
        header("Location: " . urlStrRedirect("imaging/manage/master"));
        exit;
    }
}

$params = getParams();
$id = $_GET['itemid'];
$tid = $_GET['target_uuid'];
$label = urldecode($_GET['itemlabel']);

if (isset($_GET['gid'])) {
    $type = 'group';
} else {
    $type = '';
}

$ret = xmlrpc_areImagesUsed(array(array($id, $tid, $type)));
$ret = $ret[$id];
?>
<form name="showTarget" action="<?php echo urlStr("base/computers/showtarget", $params) ?>" method="post">
    <p><?php printf(_T("Show all targets that use that image in their boot menu", "imaging")); ?></p>
<?php
foreach ($ret as $target) {
    /*
     * $target = array(
     *      [0] => UUID of the target
     *      [1] => 1 or -1 // if -1: target is an imaging server else it is a computer
     *      [2] => target name
     *  );
     */

    if ($target[1] == -1) { # this is an imaging server
        // Masters linked to an imaging server
        $params['location'] = $target[0];
        $url = urlStrRedirect("imaging/manage/master", $params);
        printf('<p><input title="' . _T("Remove this master from imaging server %s", "imaging") . '" type="checkbox" name="imaging_checkbox_%s"/>', $target[2], $target[0]);
        printf("<a href='" . $url . "'>" . _T("Imaging server", 'imaging') . " : " . $target[2] . "</a></p>");
        printf('<input type="hidden" name="imaging_uuid_%s" value="%s"/>', $target[0], $id);
    } else {
        // Masters linked to a computer
        $params['uuid'] = $target[0];
        $params['hostname'] = $target[2];
        $url = urlStrRedirect("base/computers/imgtabs/" . $type . "tabimages", $params);
        printf('<p><input title="' . _T("Remove this master from computer %s", "imaging") . '" type="checkbox" name="computer_checkbox_%s"/>', $target[2], $target[0]);
        printf("<a href='" . $url . "'>" . ($target[1] == 2 ? _T('Imaging group', 'imaging') : _T('Computer', 'imaging')) . " : " . $target[2] . "</a></p>");
        printf('<input type="hidden" name="computer_uuid_%s" value="%s"/>', $target[0], $id);
        printf('<input type="hidden" name="type_uuid_%s" value="%s"/>', $target[0], $target[1]);
    }
}

if (isset($_GET['from'])) {
    // Come from a computer target page
    printf('<input type="hidden" name="uuid" value="%s"/>', $_GET['target_uuid']);
    printf('<input type="hidden" name="hostname" value="%s"/>', $_GET['hostname']);
} else {
    // Come from an imaging server page
}
?>
    <hr />
    <p><?php printf(_T("If you want to remove this master from one or more targets, check these targets and click on the remove button", "imaging")); ?></p>
    <p><a onclick="checkAll('imaging_checkbox_', 1);
            checkAll('computer_checkbox_', 1);" href="javascript:void(0);"><?php printf(_T("Select all", "imaging")); ?></a>
        / <a onclick="checkAll('imaging_checkbox_', 0);
            checkAll('computer_checkbox_', 0);" href="javascript:void(0);"><?php printf(_T("Unselect all", "imaging")); ?></a></p>
    <input name='removeMasters' type="submit" class="btnPrimary" value="<?php echo _T("Remove", "imaging"); ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo _T("Cancel", "imaging"); ?>" onClick="closePopup();
            return false;"/>
</form>
