<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id: add.php 10 2006-09-05 09:19:30Z cedric $
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

require("modules/base/includes/groups.inc.php");
require("localSidebar.php");
require("graph/navbar.inc.php");

if (isset($_POST["badd"])) {
    $groupname = $_POST["groupname"];
    $groupdesc = stripslashes($_POST["groupdesc"]);
    $result = create_group($error, $groupname);
    change_group_desc($groupname, $groupdesc);
    if (!isXMLRPCError()) {
        new NotifyWidgetSuccess(sprintf(_("Group %s successfully added"), $groupname));
        header("Location: " . urlStrRedirect("base/groups/index"));
        exit;
    }
} else if (isset($_POST["bmodify"])) {
    $groupname = $_POST["groupname"];
    $groupdesc = stripslashes($_POST["groupdesc"]);
    change_group_desc($groupname, $groupdesc);
    callPluginFunction("changeGroup", array($_POST));
    if (!isXMLRPCError()) new NotifyWidgetSuccess(sprintf(_("Group %s successfully modified"), $groupname));
}


if ($_GET["action"] == "add") {
    $title = _("Add group");
    $groupname = "";
    $groupdesc = "";
    $detailArr = array();
} else {
    $title = _("Edit group");
    $groupname = $_GET["group"];
    $detailArr = get_detailed_group($groupname);
    if (isset($detailArr["description"])) $groupdesc = htmlspecialchars($detailArr["description"][0]);
    else $groupdesc = "";
}

$p = new PageGenerator($title);
if ($_GET["action"] == "edit") {
    $sidemenu->forceActiveItem("index");
}
$p->setSideMenu($sidemenu);
$p->display();

?>

<?php if ($_GET["action"] == "add") { ?>

<p>
<?php echo  _("The group name can only contain letters and numeric, and must begin with a letter"); ?>
</p>

<?php
}
?>

<form name="groupform" method="post" onsubmit="return validateForm();">
<table cellspacing="0">

<?php
if ($_GET["action"]=="add") {
    $formElt = new InputTpl("groupname", "/^[a-zA-Z][0-9_a-zA-Z-]*$/");
} else {
    $formElt = new HiddenTpl("groupname");
}

$tr = new TrFormElement(_("Group name"), $formElt);
$tr->display(array("value" => $groupname, "required" => True));

$tr = new TrFormElement(_("Description"), new InputTpl("groupdesc"));
$tr->display(array("value" => $groupdesc));

?>

</table>

<?php
callPluginFunction("baseGroupEdit", array($detailArr, $_POST));
?>

<?php if ($_GET["action"] == "add")  { ?>
<input name="badd" type="submit" class="btnPrimary" value="<?php echo  _("Create"); ?>" />
<?php } else { ?>
<input name="groupname" type="hidden" value="<?php echo  $groupname; ?>" />
<input name="bmodify" type="submit" class="btnPrimary" value="<?php echo  _("Confirm"); ?>" />
<?php
}

?>
</form>

<script type="text/javascript">
jQuery(document).ready(function() {
    jQuery('input[name=groupname]').focus();
});
</script>
