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
 *
 */

?><style>
    /* Style of the action bar */
    .flex-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 1em;
    }

    .flex-toolbar .filters,
    .flex-toolbar .actions {
        display: flex;
        gap: 10px;
        align-items: center;
    }

    .flex-toolbar .filters label {
        display: flex;
        align-items: center;
        gap: 4px;
        font-weight: normal;
    }

    .flex-toolbar .filters input[type="radio"] {
        margin: 0;
    }

    /* Search bar container AjaxFilter */
    .searchbox {
        display: flex;
        justify-content: flex-end;
        align-items: center;
    }

    #searchBest {
        display: flex;
        align-items: center;
        gap: 6px;
        border: 1px solid #ccc;
        border-radius: 6px;
        background-color: #fff;
        padding: 2px 8px;
        height: 30px;
        min-width: 260px;
        line-height: 1;
    }

    #searchBest * {
        vertical-align: middle;
        line-height: 1;
        margin: 0;
        padding: 0;
    }

    #searchBest input.searchfieldreal {
        border: none !important;
        outline: none !important;
        font-size: 13px !important;
        height: 22px !important;
        line-height: 22px !important;
        padding: 0 4px !important;
        background: transparent !important;
        max-height: none !important;
    }

    #searchBest img {
        height: 16px;
        width: 16px;
        display: inline-block;
    }

    /* croix */
    #searchBest img.searchfield {
        cursor: pointer !important;
        height: 16px !important;
        width: 16px !important;
        opacity: 0.6 !important;
        transition: opacity 0.2s !important;
        position: static !important;
        margin: 0 !important;
        display: inline-block !important;
    }

    /* loader */
    #searchBest img.loader {
        height: 16px !important;
        width: 16px !important;
        margin-right: 4px !important;
        opacity: 0.8 !important;
    }

    #searchBest button {
        padding: 4px 10px;
        font-size: 13px;
        background-color: #f3f3f3;
        border: 1px solid #ccc;
        border-radius: 4px;
        cursor: pointer;
    }

    #searchBest button:hover {
        background-color: #e0e0e0;
    }

    #loaderLocation {
        display: flex;
        align-items: center;
        margin-right: 10px;
    }

    #loaderLocation img,
    .loader-container img.loader {
        height: 18px;
        width: 18px;
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
        echo '<div class="flex-toolbar">';

        if (in_array("medulla_server", $_SESSION["modulesList"])) {
            echo '<div class="filters">';
            echo '<label><input type="radio" name="namepresence" value="all_computer"' . ($computerpresence == "all_computer" ? " checked" : "") . '> ' . _T('All computers', 'base') . '</label>';
            echo '<label><input type="radio" name="namepresence" value="presence"' . ($computerpresence == "presence" ? " checked" : "") . '> ' . _T('Online computers', 'base') . '</label>';
            echo '<label><input type="radio" name="namepresence" value="no_presence"' . ($computerpresence == "no_presence" ? " checked" : "") . '> ' . _T('Offline computers', 'base') . '</label>';
            echo '</div>';
        }

        echo '<div class="actions">';
        display_group_actions($group, $paramArray);
        echo '</div></div>';

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
        $actions['displayGroup'] = new ActionItem(_T("Display2 this group's content", 'dyngroup'), "display", "displaygroup", "id", "base", "computers");
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
<script type="text/javascript">
    function getQuerystringDef(key, default_) {
        if (default_ == null) default_ = "";
        key = key.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
        var regex = new RegExp("[\\?&]" + key + "=([^&#]*)");
        var qs = regex.exec(window.location.href);
        return qs == null ? default_ : qs[1];
    }

    jQuery('input[type=radio][name=namepresence]').change(function() {
        var valselect = this.value;
        var url = window.location.href;
        if (!getQuerystringDef("computerpresence", false)) {
            window.location = url + "&computerpresence=" + valselect;
        } else {
            var array_url = url.split("?");
            var adress = array_url[0];
            var parameters = array_url[1];
            var parameterlist = parameters.split("&");
            parameterlist.pop();
            var parameterstring = parameterlist.join('&');
            window.location = adress + "?" + parameterstring + "&computerpresence=" + valselect;
        }
    });
</script>
