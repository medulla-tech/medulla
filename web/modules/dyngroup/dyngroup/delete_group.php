<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2017 siveo, http://www.siveo.net
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
 *
 * File delete_group.php
 */
require_once("modules/dyngroup/includes/includes.php");

if (in_array("xmppmaster", $_SESSION["modulesList"])) {
    require_once("modules/xmppmaster/includes/xmlrpc.php");
    require_once('modules/msc/includes/commands_xmlrpc.inc.php');
}
if (in_array("imaging", $_SESSION["modulesList"])) {
    // Get Current Location
    require_once('modules/imaging/includes/xmlrpc.inc.php');
}
$location ="";
$gid = quickGet('gid');
$group = new Group($gid, False);
$type = quickGet('type');
if ($type == 1) { // Imaging group
    $stype = "_profiles";
    $ltype = 'profile';
    $title = _T("Delete imaging group", "dyngroup");
    $popup = _T("Are you sure you want to delete imaging group <b>%s</b>?<br/>", "dyngroup");
    $delete = _T("Delete imaging group", "dyngroup");
} else { // Simple group
    $stype = '';
    $ltype = 'group';
    $title = _T("Delete group", "dyngroup");
    $popup = _T("Are you sure you want to delete group <b>%s</b>?<br/> (it can be used in an other group).", "dyngroup");
    $delete = _T("Delete group", "dyngroup");
}

    if ($type == 1) { // Imaging group
        if (in_array("imaging", $_SESSION["modulesList"])) {
            // Get Current Location
            require_once('modules/imaging/includes/xmlrpc.inc.php');
            $location = xmlrpc_getProfileLocation($gid);
            $objprocess=array();
            $scriptmulticast = 'multicast.sh';
            $path="/tmp/";
            $objprocess['location']=$location;
            $objprocess['process'] = $path.$scriptmulticast;
            if (xmlrpc_check_process_multicast($objprocess)){
                $msg = _T("The group cannot be deleted as a multicast deployment is currently running.", "imaging");
                echo' <form action="'.urlStr("imaging/manage/list$stype").'" method="post">
                <p>'.$msg.'</p>
                    <input name="bback" type="submit" class="btnSecondary" value="'._T("Cancel", "dyngroup").'" onClick="closePopup();return true;"/>
                </form>';
                    exit;
            }
        }
    }

if (quickGet('valid')) {
    $result = $group->delete();
    if (!isset($result[0]) || $result[0] ==0) {
        $errorMessage = $result[1];
        preg_match("/Deletion forbidden for Group:(.*?)\)/",
                $errorMessage, $matches);
        $msg  = _T("Deletion forbidden for Group:", "dyngroup");
        $msg1 = _T("Delete before the groups:", "dyngroup");
        echo "<pre>";
        print_r($matches[1]);
        echo "</pre>";
        if (isset($matches[1])) {
            $extractedMessage = trim($matches[1], " '\n\r");
            if ($type == 0) { // simple group
            $strpart = sprintf("%s %s", $msg, $extractedMessage);
            $msgnew = str_replace("Delete before the groups:" , $msg1 , $strpart);

            header("Location: " . urlStrRedirect("base/computers/list$stype"));
            new NotifyWidgetFailure(sprintf($msgnew, $group->getName()));
                exit;
            }
        }
    }

    if (in_array("xmppmaster", $_SESSION["modulesList"])) {
        xmlrpc_delDeploybygroup($gid);
        $array_command_id = get_commands_by_group($gid);
        foreach ($array_command_id as $commandeid){
            echo "delete";
            echo $commandeid;
            //delete_command_on_host($commandeid);
            delete_command($commandeid);
        }
    }
    if ($type == 1) { // Imaging group
        if (in_array("imaging", $_SESSION["modulesList"])) {
            // Synchro Location
            xmlrpc_synchroLocation($location);
        }
        header("Location: " . urlStrRedirect("imaging/manage/list$stype"));
        new NotifyWidgetSuccess(sprintf(_T("Imaging group %s was successfully deleted", "imaging"), $group->getName()));
    } else { // simple group
        header("Location: " . urlStrRedirect("base/computers/list$stype"));
        new NotifyWidgetSuccess(sprintf(_T("Group %s was successfully deleted", "imaging"), $group->getName()));
    }
    exit;
}
?>

<h2><?php echo $title ?></h2>

<form action="<?php echo urlStr("base/computers/delete_group", array('gid' => $gid, 'type' => $type)) ?>" method="post">
    <p>

<?php
printf($popup, $_GET["groupname"]);
?>
    </p>
    <input name='valid' type="submit" class="btnPrimary" value="<?php echo $delete ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo _T("Cancel", "dyngroup"); ?>" onClick="closePopup();
            return false;"/>
</form>
