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
$location = "";

// --- Bulk deletion mode (AJAX POST with gid[] array) ---
if (isset($_POST['gid']) && is_array($_POST['gid'])) {
    header('Content-Type: application/json');

    verifyCSRFToken($_POST);

    $gids = $_POST['gid'];
    $type = isset($_POST['type']) ? intval($_POST['type']) : 0;
    $stype = ($type == 1) ? '_profiles' : '';

    if (empty($gids)) {
        echo json_encode(['success' => false]);
        exit;
    }

    $successNames = [];
    $errors = [];
    $blocked = [];

    $forbiddenDetail = function ($errorMessage) {
        preg_match("/Deletion forbidden for Group:(.*?)\)/", $errorMessage, $matches);
        return $matches[1] ?? null;
    };

    $cleanupDeletedGroup = function ($gid, $location) use ($type) {
        // Cleanup xmppmaster data
        if (in_array("xmppmaster", $_SESSION["modulesList"])) {
            xmlrpc_delDeploybygroup($gid);
            $array_command_id = get_commands_by_group($gid);
            foreach ($array_command_id as $commandeid) {
                delete_command($commandeid);
            }
        }

        // For imaging groups, sync location
        if ($type == 1 && in_array("imaging", $_SESSION["modulesList"])) {
            if (isset($location)) {
                xmlrpc_synchroLocation($location);
            }
        }
    };

    foreach ($gids as $gid) {
        $gid = clean_xss($gid);
        $location = null;
        $group = new Group($gid, false);
        $groupName = $group->getName();

        // Check ownership
        if (!$group->is_owner && ($_SESSION['login'] ?? '') !== 'root') {
            $errors[] = sprintf(_T("Permission denied for group %s", "dyngroup"), $groupName);
            continue;
        }

        // For imaging groups, check multicast
        if ($type == 1 && in_array("imaging", $_SESSION["modulesList"])) {
            $location = xmlrpc_getProfileLocation($gid);
            $objprocess = [
                'location' => $location,
                'process' => '/tmp/multicast.sh'
            ];
            if (xmlrpc_check_process_multicast($objprocess)) {
                $errors[] = sprintf(_T("Group %s cannot be deleted: multicast deployment in progress.", "dyngroup"), $groupName);
                continue;
            }
        }

        $result = $group->delete();

        if (!isset($result[0]) || $result[0] == 0) {
            $errorMessage = $result[1] ?? '';
            if ($forbiddenDetail($errorMessage) !== null) {
                $blocked[] = [
                    'gid' => $gid,
                    'group' => $group,
                    'name' => $groupName,
                    'location' => $location,
                    'message' => $errorMessage,
                ];
            } else {
                $errors[] = sprintf(_T("Failed to delete group %s", "dyngroup"), $groupName);
            }
            continue;
        }

        $cleanupDeletedGroup($gid, $location);

        $successNames[] = $groupName;
    }

    $maxPasses = count($blocked);
    for ($pass = 0; $pass < $maxPasses && !empty($blocked); $pass++) {
        $stillBlocked = [];
        foreach ($blocked as $item) {
            $result = $item['group']->delete();
            if (!isset($result[0]) || $result[0] == 0) {
                $item['message'] = $result[1] ?? '';
                $stillBlocked[] = $item;
                continue;
            }
            $cleanupDeletedGroup($item['gid'], $item['location']);
            $successNames[] = $item['name'];
        }
        $progressed = count($stillBlocked) < count($blocked);
        $blocked = $stillBlocked;
        if (!$progressed) {
            break;
        }
    }

    foreach ($blocked as $item) {
        $detail = $forbiddenDetail($item['message']);
        if ($detail !== null) {
            $msg = _T("Deletion forbidden for Group:", "dyngroup");
            $detail = str_replace("Delete before the groups:", _T("Delete before the groups:", "dyngroup"), trim($detail, " '\n\r"));
            $errors[] = $msg . ' ' . $detail;
        } else {
            $errors[] = sprintf(_T("Failed to delete group %s", "dyngroup"), $item['name']);
        }
    }

    // NotifyWidget messages
    if (!empty($successNames)) {
        new NotifyWidgetSuccess(sprintf(
            _T("%d group(s) successfully deleted", "dyngroup"),
            count($successNames)
        ));
    }
    foreach ($errors as $err) {
        new NotifyWidgetFailure(htmlspecialchars($err, ENT_QUOTES, 'UTF-8'));
    }

    echo json_encode(['success' => empty($errors), 'errors' => $errors]);
    exit;
}

// --- Single deletion mode (popup form) ---
$gid = quickGet('gid');
$group = new Group($gid, False);
$type = quickGet('type');
if ($type == 1) { // Imaging group
    $stype = "_profiles";
    $ltype = 'profile';
    $title = _T("Delete imaging group", "dyngroup");
    $popup = _T("Delete the imaging group <b>%s</b>?", "dyngroup");
    $delete = _T("Delete imaging group", "dyngroup");
} else { // Simple group
    $stype = '';
    $ltype = 'group';
    $title = _T("Delete group", "dyngroup");
    $popup = _T("Delete the group <b>%s</b>?", "dyngroup");
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
    verifyCSRFToken($_POST);

    $result = $group->delete();
    if (!isset($result[0]) || $result[0] ==0) {
        $errorMessage = $result[1];
        preg_match("/Deletion forbidden for Group:(.*?)\)/",
                $errorMessage, $matches);
        $msg  = _T("Deletion forbidden for Group:", "dyngroup");
        $msg1 = _T("Delete before the groups:", "dyngroup");
        echo "<pre>";
        echo htmlspecialchars($matches[1] ?? '', ENT_QUOTES, 'UTF-8');
        echo "</pre>";
        if (isset($matches[1])) {
            $extractedMessage = htmlspecialchars(trim($matches[1], " '\n\r"), ENT_QUOTES, 'UTF-8');
            if ($type == 0) { // simple group
            $strpart = sprintf("%s %s", $msg, $extractedMessage);
            $msgnew = str_replace("Delete before the groups:" , $msg1 , $strpart);

            header("Location: " . urlStrRedirect("base/computers/list$stype"));
            new NotifyWidgetFailure(sprintf($msgnew, htmlspecialchars($group->getName(), ENT_QUOTES, 'UTF-8')));
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
        new NotifyWidgetSuccess(sprintf(_T("Imaging group %s was successfully deleted", "imaging"), htmlspecialchars($group->getName(), ENT_QUOTES, 'UTF-8')));
    } else { // simple group
        header("Location: " . urlStrRedirect("base/computers/list$stype"));
        new NotifyWidgetSuccess(sprintf(_T("Group %s was successfully deleted", "imaging"), htmlspecialchars($group->getName(), ENT_QUOTES, 'UTF-8')));
    }
    exit;
}

$convergenceWarning = "";
$convergences = xmlrpc_getConvergenceStatus($gid);
$activePackages = [];
foreach (($convergences[0]['/package_api_get1'] ?? []) as $packageUuid => $active) {
    if ($active) {
        $activePackages[] = $packageUuid;
    }
}
if ($activePackages) {
    $names = [];
    if (in_array("pkgs", $_SESSION["modulesList"])) {
        require_once("modules/pkgs/includes/xmlrpc.php");
        $packageNames = get_pkg_name_from_uuid($activePackages);
        foreach ($activePackages as $packageUuid) {
            if (!empty($packageNames[$packageUuid])) {
                $names[] = htmlspecialchars($packageNames[$packageUuid], ENT_QUOTES, 'UTF-8');
            }
        }
    }
    if (count($names) == 1) {
        $convergenceWarning = sprintf(_T("Convergence deleted along with the group: %s", "dyngroup"), $names[0]);
    } elseif ($names) {
        $maxShownNames = 3;
        $shownNames = implode(", ", array_slice($names, 0, $maxShownNames));
        $hiddenCount = count($names) - $maxShownNames;
        if ($hiddenCount == 1) {
            $shownNames = sprintf(_T("%s and 1 other", "dyngroup"), $shownNames);
        } elseif ($hiddenCount > 1) {
            $shownNames = sprintf(_T("%s and %d others", "dyngroup"), $shownNames, $hiddenCount);
        }
        $convergenceWarning = sprintf(_T("Convergences deleted along with the group: %s", "dyngroup"), $shownNames);
    } elseif (count($activePackages) == 1) {
        $convergenceWarning = _T("1 active convergence will be deleted along with the group.", "dyngroup");
    } else {
        $convergenceWarning = sprintf(_T("%d active convergences will be deleted along with the group.", "dyngroup"), count($activePackages));
    }
}
?>

<h2 class="popup-title-danger"><?php echo $title ?></h2>

<form action="<?php echo urlStr("base/computers/delete_group", array('gid' => $gid, 'type' => $type)) ?>" method="post">
<input type="hidden" name="auth_token" value="<?php echo htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8'); ?>">
    <p>

<?php
printf($popup, htmlspecialchars($_GET["groupname"] ?? '', ENT_QUOTES, 'UTF-8'));
?>
    </p>
<?php if ($convergenceWarning) { ?>
    <p><?php echo $convergenceWarning; ?></p>
<?php } ?>
    <input name='valid' type="submit" class="btnDanger" value="<?php echo $delete ?>" />
    <input name="bback" type="submit" class="btnSecondary" value="<?php echo _T("Cancel", "dyngroup"); ?>" onClick="closePopup();
            return false;"/>
</form>
