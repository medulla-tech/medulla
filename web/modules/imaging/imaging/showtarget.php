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

/*****************
 * Remove masters
 ****************/

if (isset($_POST['removeMasters'])) {
    $imagesToDesassociate = array();

    #print "<pre>";
    #print_r($_POST);
    #print "</pre>";
    foreach ($_POST as $key => $value) {
        if (substr($key, 0, 18) == 'computer_itemuuid_') {
            $target_uuid = substr($key, 18);
            if (isset($_POST['computer_checkbox_' . $target_uuid]) and $_POST['computer_checkbox_' . $target_uuid] == 'on') {
                $imagesToDesassociateFromComputers[] = array(
                    'im_uuid' => $_POST['computer_itemuuid_' . $target_uuid],
                    'target_uuid' => $target_uuid,
                );
            }
        }
        if (substr($key, 0, 17) == 'imaging_itemuuid_') {
            $target_uuid = substr($key, 17);
            if (isset($_POST['imaging_checkbox_' . $target_uuid]) and $_POST['imaging_checkbox_' . $target_uuid] == 'on') {

                list($count, $masters) = xmlrpc_getLocationImages($target_uuid);
                $menu_item_id = '';

                foreach ($masters as $master) {
                    if ($master['imaging_uuid'] == $_POST['imaging_itemuuid_' . $target_uuid]) {
                        $menu_item_id = $master['menu_item']['id'];
                        break;
                    }
                }

                $imagesToDesassociateFromImaging[] = array(
                    'item_uuid' => $menu_item_id,
                    'location' => $target_uuid,
                );
            }
        }
    }
    #print "<pre>";
    #print_r($imagesToDesassociateFromComputers);
    #print_r($imagesToDesassociateFromImaging);
    #print "</pre>";
    $type = '';
    foreach ($imagesToDesassociateFromComputers as $image) {
        $ret = xmlrpc_delImageToTarget($image['im_uuid'], $image['target_uuid'], $type);
    }
    foreach ($imagesToDesassociateFromImaging as $image) {
        $ret = xmlrpc_delImageToLocation($image['item_uuid'], $image['location']);
    }
    $params = array(
        'uuid' => $_POST['uuid'],
        'hostname' => $_POST['hostname'],
    );
    header("Location: " . urlStrRedirect("base/computers/".$type."imgtabs", $params));
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
<form action="<?php echo urlStr("base/computers/showtarget",$params) ?>" method="post">
    <p><?php printf(_T("Show all targets that use that image in their boot menu", "imaging")); ?></p>
<?php
foreach ($ret as $target) {
    if ($target[1]==-1) { # this is an imaging server
        // Masters linked to an imaging server
        $params['location'] = $target[0];
        $url = urlStrRedirect("imaging/manage/master", $params);
        printf("<h2><a href='".$url."'>"._T("Imaging server", 'imaging')." : ".$target[2]."</a></h2>");
        printf('<input type="checkbox" name="imaging_checkbox_%s"/>', $target[0]);
        printf('<input type="hidden" name="imaging_itemuuid_%s" value="%s"/>', $target[0], $id);
    } else {
        // Masters linked to a computer
        $params['uuid'] = $target[0];
        $params['hostname'] = $target[2];
        $url = urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params);
        printf("<h2><a href='".$url."'>".($target[1]==2?_T('Profile', 'imaging'): _T('Computer', 'imaging'))." : ".$target[2]."</a></h2>");
        printf('<input type="checkbox" name="computer_checkbox_%s"/>', $target[0]);
        printf('<input type="hidden" name="computer_itemuuid_%s" value="%s"/>', $target[0], $id);
    }
}

printf('<input type="hidden" name="uuid" value="%s"/>', $target[0]);
printf('<input type="hidden" name="hostname" value="%s"/>', $target[2]);
?>
    <input name='removeMasters' type="submit" class="btnPrimary" value="<?php echo  _T("Remove", "imaging"); ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo  _T("Cancel", "imaging"); ?>" onClick="new Effect.Fade('popup'); return false;"/>
</form>
