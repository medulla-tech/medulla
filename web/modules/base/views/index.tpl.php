<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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


<form name="userForm" id="userForm" action="#" onsubmit="return false;">

    <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

    <div id="searchSpan" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" /> <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearchUser(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onclick="jQuery('#param').val(''); pushSearchUser(); return false;" />
    </span>
    </div>

    <script type="text/javascript">
        jQuery('#param').focus();
    </script>
</form>

<h2><?php echo  _("User list"); ?></h2>

<div class="fixheight"></div>
<div id="userContainer">

<?php

if ($error)
{
  echo $error;
}


$arrUser = array();
$arrSnUser = array();
$homeDirArr = array();

/*for ($idx = $start;
     ($idx < count($users)) && ($idx <= $end);
     $idx++)*/

$css = array();

for ($idx = 0; $idx < count($users); $idx++)
 {
    if ($users[$idx]["enabled"]) {
        $css[$idx] = "userName";
    }  else $css[$idx] = "userNameDisabled";
    $arrUser[]=$users[$idx]['uid'];
    $arrSnUser[]=$users[$idx]['givenName'].' '.$users[$idx]['sn'];
    $homeDirArr[]=$users[$idx]['homeDirectory'];
}


// $arrUser is the list of all Users
$n = new UserInfos($arrUser,_("Login"));

$n->setCssClass("userName");

$n->css = $css;

$n->addExtraInfo($arrSnUser,_("Name"));

//add a list with all homeDir
$n->addExtraInfo($homeDirArr,_("Home directory"));

$n->addActionItem(new ActionItem(_("Edit"),"edit","edit","user") );
//
$n->addActionItem(new ActionItem(_("MMC rights"),"editacl","editacl","user") );
$n->addActionItem(new ActionPopupItem(_("Delete"),"delete","delete","user") );
$n->addActionItem(new ActionPopupItem(_("Backup"),"backup","backup","user") );

$n->setName(_("Users"));
$n->display();

?>

</div>
