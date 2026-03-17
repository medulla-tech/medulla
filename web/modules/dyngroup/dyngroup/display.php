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
 * file: display.php
 */

?><style>
    #loaderLocation {
        display: flex;
        align-items: center;
        margin-right: 10px;
        gap: 8px;
    }
</style>
<?php

require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/includes.php");
require_once("modules/medulla_server/includes/utilities.php");

$computerpresence = $_GET['computerpresence'] ?? ($_SESSION['computerpresence'] ?? "all_computer");
$_SESSION['computerpresence'] = $computerpresence;

$gid = quickGet('gid');
if (!$gid) {
    require("modules/base/computers/localSidebar.php");
    $request = quickGet('request');
    if ($request == 'stored_in_session') {
        $request = $_SESSION['request'];
        unset($_SESSION['request']);
    }
    $r = new Request();
    $r->parse($request);
    $result = new Result($r, $group->getBool());
    $result->replyToRequest();
    $result->displayResListInfos();
} else {
    $group = getPGobject($gid, true);
    if ($group->type == 0) {
        require("modules/base/computers/localSidebar.php");
    } else {
        require("modules/imaging/manage/localSidebar.php");
    }
    $group = getPGobject($gid, true);
    $item = $items[$gid] ?? null;
    $headerText = $group->type == 0 ? _T("Group '%s' content", "dyngroup") : _T("Imaging group '%s' content", "dyngroup");
    __my_header(sprintf($headerText, clean_xss($group->getName())), $sidemenu, $item, $group);

    if ($group->type == 0) {
        $paramArray = ['id' => $gid, 'gid' => $gid, 'groupname' => $group->getName(), 'type' => $group->type];
        display_group_actions($group, $paramArray);

?>
<?php }

    $group->prettyDisplay();
}

function __my_header($label, $sidemenu, $item, $group)
{
    $p = new PageGenerator($label);
    if (!empty($item)) {
        $sidemenu->forceActiveItem($item->action);
    } else {
        $sidemenu->forceActiveItem($group->type == 0 ? 'list' : 'list_profiles');
    }
    $p->setSideMenu($sidemenu);
    $p->display();
    return $p;
}

function display_group_actions($group, $paramArray)
{
    $actions = [];
    $is_gp = ($group->type == 1);

    if (!$is_gp) {
        $actions['displayGroup'] = new ActionItem(_T("Display this group's content", 'dyngroup'), "display", "displaygroup", "id", "base", "computers");
        $actions['edit'] = new ActionItem(_T("Edit this group", 'dyngroup'), "computersgroupedit", "edit", "id", "base", "computers");
        $actions['share'] = new ActionItem(_T("Share this group", 'dyngroup'), "edit_share", "groupshare", "id", "base", "computers");
        if (in_array("msc", $_SESSION["supportModList"])) {
            $actions['deploy'] = new ActionItem(_T("Software deployment on this group", "dyngroup"), "groupmsctabs", "install", "computer", "base", "computers");
        }
        if (in_array("update", $_SESSION["supportModList"])) {
            $actions['update'] = new ActionItem(_T("Update on this group", "dyngroup"), "view_updates", "reload", "id", "base", "computers");
        }
    } else {
        $actions['displayGroup'] = new ActionItem(_T("Display this imaging group's content", 'dyngroup'), "display", "displaygroup", "id", "imaging", "manage");
        $actions['edit'] = new ActionItem(_T("Edit this imaging group", 'dyngroup'), "computersgroupedit", "edit", "id", "imaging", "manage");
        $actions['share'] = new ActionItem(_T("Share this imaging group", 'dyngroup'), "edit_share", "groupshare", "id", "imaging", "manage");
    }

    if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        $quick = new ActionPopupItem(_("Group Quick action"), "deployquickgroup", "quick", "computer", "xmppmaster", "xmppmaster");
        $quick->setWidth(600);
        $actions['quick'] = $quick;
    }

    $actions['csv'] = new ActionItem(_T("Csv export", "dyngroup"), "csv", "csv", "computer", "base", "computers");

    echo "<ul class='action'>";
    foreach ($actions as $action) {
        $paramArray['mod'] = $action->mod;
        echo "<li class=\"{$action->classCss}\" style=\"list-style-type: none; border: none; float:left;\">";
        $urlChunk = $action->buildUrlChunk($paramArray);
        if ($action instanceof ActionPopupItem)
            echo '<a title="' . $action->desc . '" onclick="PopupWindow(event, \'' . urlStr($action->path) . $urlChunk . '\'); return false;" href="#">&nbsp;</a>';
        else
            echo '<a title="' . $action->desc . '" href="' . urlStr($action->path) . $urlChunk . '">&nbsp;</a>';
        echo "</li>";
    }
    echo "</ul>";
}
?>
<?php
if (in_array("medulla_server", $_SESSION["modulesList"])) {
    $presenceSelectHtml = '<span class="searchfield"><select id="computerpresence" class="searchfieldreal noborder">';
    $presenceOptions = array(
        'all_computer' => _T('All computers', 'base'),
        'presence' => _T('Online computers', 'base'),
        'no_presence' => _T('Offline computers', 'base')
    );
    foreach ($presenceOptions as $value => $label) {
        $selected = ($computerpresence == $value) ? 'selected' : '';
        $presenceSelectHtml .= '<option value="' . $value . '" ' . $selected . '>' . $label . '</option>';
    }
    $presenceSelectHtml .= '</select></span>';
?>
<script type="text/javascript">
jQuery(function() {
    jQuery('#searchBest').prepend(<?php echo json_encode($presenceSelectHtml); ?>);

    jQuery('#computerpresence').on('change', function() {
        var url = new URL(window.location.href);
        url.searchParams.set("computerpresence", this.value);
        window.location.href = url.toString();
    });
});
</script>
<?php } ?>
