<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id: add.php 10 2006-09-05 09:19:30Z cedric $
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php


require("modules/base/includes/groups.inc.php");

?>

<style type="text/css">
<!--

<?php
require("modules/base/graph/groups/add.css");
?>

-->
</style>

<?php
$path = array(array("name" => _("Home"),
                    "link" => "main.php"),
              array("name" => _("Groups"),
                    "link" => "main.php?module=base&submod=groups&action=index"),
              array("name" => _("Add group")));

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
} else {
    $title = _("Edit group");
    $groupname = $_GET["group"];
    $detailArr = get_detailed_group($groupname);
    if (isset($detailArr["description"])) $groupdesc = htmlspecialchars($detailArr["description"][0]);
    else $groupdesc = "";
}

?>

<h2><?= $title ?> </h2>

<div class="fixheight"></div>

<? if ($_GET["action"] == "add") { ?>

<p>
<?= _("The group name can only contain letters and numeric, and must begin with a letter"); ?>
</p>

<?
}
?>

<form name="groupform" method="post" action="<? echo $PHP_SELF; ?>" onsubmit="return validateForm();">
<table cellspacing="0">

<?
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

<?
callPluginFunction("baseGroupEdit", array($detailArr, $_POST));
?>

<? if ($_GET["action"] == "add")  { ?>
<input name="badd" type="submit" class="btnPrimary" value="<?= _("Create"); ?>" />
<? } else { ?>
<input name="groupname" type="hidden" value="<?= $groupname; ?>" />
<input name="bmodify" type="submit" class="btnPrimary" value="<?= _T("Confirm");?>" /> 
<?php
}

?>
</form>

<script type="text/javascript">
document.body.onLoad = document.groupform.groupname.focus();
</script>
