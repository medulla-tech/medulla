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
 * file: index.tpl.php
 */
?>


<form name="userForm" id="userForm" action="#" onsubmit="return false;">

    <div id="searchSpan" class="searchbox">
    <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearchUser(); return false;" />
    <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'base'); ?>"
    onclick="jQuery('#param').val(''); pushSearchUser(); return false;"></button>
    </span>
    <span class="loader" aria-hidden="true"></span>
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
     ($idx < safeCount($users)) && ($idx <= $end);
     $idx++)*/

$css = array();

for ($idx = 0; $idx < safeCount($users); $idx++)
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
