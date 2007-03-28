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
    if (!preg_match("/^[a-zA-Z][0-9\-_a-zA-Z ]*$/", $_POST["groupname"]))  {
        $error = _("Invalid group name");
        $n = new NotifyWidget();
        $n->flush();
        $n->add("<div id=\"errorCode\">$error</div>");
        $n->setLevel(4);
        $n->setSize(600);    
    } else {
        $groupname = $_POST["groupname"];
        $groupdesc = $_POST["groupdesc"];
        $result = create_group($error, $groupname);
        change_group_desc($groupname, $groupdesc);
	if (!isXMLRPCError()) {
	    $n = new NotifyWidget();
	    $n->add(sprintf("Group %s successfully added", $groupname));
	    header("Location: " . urlStrRedirect("base/groups/index"));
	}
    }
} else if (isset($_POST["bmodify"])) {
    $groupname = $_POST["groupname"];
    $groupdesc = $_POST["groupdesc"];    
    change_group_desc($groupname, $groupdesc);
    callPluginFunction("changeGroup", array($_POST));
    if (!isXMLRPCError()) {
        $n = new NotifyWidget();
        $n->add(sprintf("Group %s successfully modified", $groupname));
    }
}


if ($_GET["action"] == "add") {
    $title = _T("Add group");
    $groupname = "";
    $groupdesc = "";
} else {
    $title = _T("Edit group");
    $groupname = $_GET["group"];
    $detailArr = get_detailed_group($groupname);
    if (isset($detailArr["description"])) $groupdesc = $detailArr["description"][0];
    else $groupdesc = "";
}

?>

<h2><?= $title ?> </h2>

<div class="fixheight"></div>

<? if ($_GET["action"] == "add") { ?>

<p>
<?= _("The group name can only contains letters and numeric, and must begin with a letter"); ?>
</p>

<?
}
?>

<form name="groupform" method="post" action="<? echo $PHP_SELF; ?>">
<table cellspacing="0">
<tr>
<td style="text-align:right; width:40%"><?= _("Group name")?></td>
    <td>
<? if ($_GET["action"] == "add")  { ?>
    <input id="groupname" name="groupname" type="text" class="textfield" size="23" value="<?= $groupname; ?>" />
<? } else {
    echo $groupname;
} ?>
    </td>
</tr>
<tr>
<td style="text-align:right; width:40%"><?= _("Description")?></td>
    <td><input id="groupdesc" name="groupdesc" type="text" class="textfield" size="23" value="<?= $groupdesc; ?>" /></td>

</tr>
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
