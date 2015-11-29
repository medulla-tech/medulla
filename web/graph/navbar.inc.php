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

$root = $conf["global"]["root"];
?>
</head>
<body>

<div id="wrapper">

<div id="header">



<!--navbar-->
<div id="navbar">
<?php
if (getMMCLogo()) {
?>
<a href="https://www.mandriva.com/pulse2/">
	<img src="<?=getMMCLogo()?>" alt="Mandriva" id="logo" />
</a>
<?php
}
?>

<ul>
<?php

autoGenerateNavbar(); //auto generation of navbar for new modules;

if ($_SESSION["login"]=='root') {
    $favact = "_disabled";
} else {
    $favact = "";
}

?>
</ul>
</div>
<!--navbar-->



<!--menuTopRight-->
<div id="menuTopRight">

  <ul>

<?php
if (isExpertMode()) {
    $mode = _("standard mode");
} else {
    $mode = _("expert mode");
}

?>

    <li id="expertmode"><a href="<?php echo $root   ?>includes/switchmode.php"><?php echo _("Click to switch to") . "&nbsp;" . $mode; ?></a></li>
    <?php echo "<li id=\"disconnect\"><a title=\""._("logout")."\" href=\"".$root."logout/index.php\"";
        echo " onclick=\"showPopup(event,'".$root."logout/index.php'); event.returnValue=false; return false;\">";
        echo _("Logout").'&nbsp;'.$_SESSION['login'];
        echo "</a></li>";
    ?>

  </ul>
</div>
<!--menuTopRight-->




</div>





<!--path-->
<p class="path">
<?php
/* Path automatic creation */
print '<span>' . $_SESSION["XMLRPC_server_description"] . '</span>&nbsp;:&nbsp;';
if ($_GET["submod"] != "main" && $_GET["action"] != "default")
    print '<a href="' . urlStr("base/main/default"). '">' . _("Home") . '</a> &gt; ';
$MMCApp =&MMCApp::getInstance();
$mod = $MMCApp->_modules[$_GET['module']];
$submod = $mod->_submod[$_GET['submod']];
list($m, $s, $a) = split('/',$submod->_defaultpage,3);
print '<a href="'. urlStr("$m/$s/$a") .'">' . $submod->getDescription() . '</a>';
$action = $submod->_pages[$_GET["action"]];
if (is_object($action)) {
    print ' &gt; ';
    print '<span>' . $action->getDescription() . "</span>";
}
?>
</p>
<!--path-->




<div id="overlay" class="overlay" style="display: none"></div>
<div id="popup" class="popup" style="display: none;">
    <div style="float:right"><a href="#" class="popup_close_btn"><img src="img/common/icn_close.png" alt ="[x]"/></a></div>
    <div id="__popup_container"><?php echo  _("If this phrase does not change, you browser is not supported by the MMC application"); ?></div>
</div>

<div id="content">
    <div id="section">
