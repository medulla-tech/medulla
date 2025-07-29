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

require("modules/base/includes/groups.inc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");

$action = isset($_GET["action"]) ? $_GET["action"] : "add";
$groupname = "";
$groupdesc = "";
$detailArr = array();

if ($action === "edit" && isset($_GET["group"])) {
    $groupname = $_GET["group"];
    $detailArr = get_detailed_group($groupname);

    if (
        isset($detailArr["description"][0]) &&
        is_object($detailArr["description"][0]) &&
        isset($detailArr["description"][0]->scalar)
    ) {
        $groupdesc = trim($detailArr["description"][0]->scalar);
        if ($groupdesc === '' || strtolower($groupdesc) === 'none' || is_null($groupdesc)) {
            $groupdesc = '';
        }
        $groupdesc = htmlspecialchars($groupdesc);
    } else {
        $groupdesc = '';
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $groupname = isset($_POST["groupname"]) ? $_POST["groupname"] : $groupname;
    $groupdesc = isset($_POST["groupdesc"]) ? stripslashes($_POST["groupdesc"]) : $groupdesc;
    if ($groupdesc === null || strtolower($groupdesc) === "none") {
        $groupdesc = "";
    }
}

if (isset($_POST["badd"])) {
    $result = create_group($error, $groupname);
    change_group_desc($groupname, $groupdesc ?? "");
    if (!isXMLRPCError()) {
        new NotifyWidgetSuccess(sprintf(_("Group %s successfully added"), $groupname));
        redirectTo(urlStrRedirect("base/groups/index"));
    }
} elseif (isset($_POST["bmodify"])) {
    change_group_desc($groupname, $groupdesc ?? "");
    $error = false;
    $ret = callPluginFunction("changeGroup", array($_POST));
    foreach($ret as $plugin => $result) {
        if ($result === false) {
            $error = true;
            break;
        }
    }
    if (!$error && !isXMLRPCError()) {
        new NotifyWidgetSuccess(sprintf(_("Group %s successfully modified"), $groupname));
        header("Location: " . urlStrRedirect("base/groups/index"));
        exit;
    }
    redirectTo(urlStrRedirect("base/groups/edit", array("group" => $groupname)));
}

$title = ($action === "add") ? _("Add group") : _("Edit group");

$p = new PageGenerator($title);
if ($action === "edit") {
    $sidemenu->forceActiveItem("index");
}
$p->setSideMenu($sidemenu);
$p->display();
?>

<?php if ($action === "add") { ?>
<p>
    <?php echo _("The group name can only contain letters and numeric, and must begin with a letter"); ?>
</p>
<?php } ?>

<form id="Form" name="groupform" method="post" onsubmit="return validateForm('Form');">
<table cellspacing="0">
<?php
if ($action === "add") {
    $formElt = new InputTpl("groupname", "/^[a-zA-Z][0-9_a-zA-Z-]*$/");
} else {
    $formElt = new HiddenTpl("groupname");
}

$tr = new TrFormElement(_("Group name"), $formElt);
$tr->display(array("value" => $groupname, "required" => true));

$descValue = (is_null($groupdesc) || strtolower($groupdesc) === "none") ? "" : $groupdesc;
$tr = new TrFormElement(_("Description"), new InputTpl("groupdesc"));
$tr->display(array("value" => $descValue));
?>
</table>

<?php callPluginFunction("baseGroupEdit", array($detailArr, $_POST)); ?>

<?php if ($action === "add") { ?>
<input name="badd" type="submit" class="btnPrimary" value="<?php echo _("Create"); ?>" />
<?php } else { ?>
<input name="groupname" type="hidden" value="<?php echo $groupname; ?>" />
<input name="bmodify" type="submit" class="btnPrimary" value="<?php echo _("Confirm"); ?>" />
<?php } ?>
</form>

<script type="text/javascript">
jQuery(document).ready(function() {
    jQuery('input[name=groupname]').focus();
});
</script>