<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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
?>
<?php
require("modules/base/includes/groups.inc.php");
?>

<style type="text/css">
<!--

<?php
require("modules/base/graph/groups/index.css");

$root = $conf["global"]["root"];
$maxperpage = $conf["global"]["maxperpage"];
?>

-->
</style>

<?php
require("localSidebar.php");
require("graph/navbar.inc.php");

if (!isset($_GET["items"])) {
  $groups = get_groups($error);
  $start = 0;

  if (count($groups) > 0) {
      $end = $conf["global"]["maxperpage"] - 1;
  } else {
      $end = 0;
  }
} else {
  $groups = unserialize(base64_decode(urldecode($_GET["items"])));
}
if (isset($_GET["start"])) {
    $start = $_GET["start"];
    $end = $_GET["end"];
}

?>




<form name="groupForm" id="groupForm" action="#" onSubmit="return false;">

    <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

    <div id="searchSpan" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" /> <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onKeyUp="pushSearchGroup(); return false;">
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onClick="document.getElementById('param').value =''; pushSearchGroup(); return false;">
    </span>
    </div>

    <script>
        document.getElementById('param').focus();
    </script>





</form>


<h2><?= _("Group list"); ?></h2>

<div class="fixheight"></div>

<div id="groupContainer">

<?php


$arrGroup = array();
$arrComment = array();
$arrNb = array();

for ($idx = 0; $idx < count($groups); $idx++) {
    $arrGroup[]=$groups[$idx][0];
    $arrComment[] = $groups[$idx][1];
    $arrNb[] = '<span style="font-weight: normal;">('.$groups[$idx][2].')</span>';
}


$n = new ListInfos($arrGroup,_("Groups"));

$n->setCssClass("groupName");

$n->addExtraInfo($arrComment,_("Comments"));
$n->setAdditionalInfo($arrNb);


$n->addActionItem(new ActionItem(_("Edit members"),"members","afficher","group") );
$n->addActionItem(new ActionItem(_("Edit group"),"edit", "edit","group") );
$n->addActionItem(new ActionPopupItem(_("Delete"),"delete","supprimer","group") );


$n->setName(_("Group list"));
$n->display();





?>
</div>
