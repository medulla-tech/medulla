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

<p class="path">
<?php
/* Path automatic creation */
print '<span>' . $_SESSION["XMLRPC_server_description"] . '</span>&nbsp;:&nbsp;';
print '<a href="main.php">' . _("Home") . '</a>';
if (!empty($_GET["module"])) { /* if not main page */
    $MMCApp =&MMCApp::getInstance();
    $mod = $MMCApp->_modules[$_GET['module']];
    $submod = $mod->_submod[$_GET['submod']];
    print ' &gt; ';
    list($m, $s, $a) = split('/',$submod->_defaultpage,3);
    print '<a href="'. urlStr("$m/$s/$a") .'">' . $submod->getDescription() . '</a>';
    $action = $submod->_pages[$_GET["action"]];
    if (is_object($action)) {
        print ' &gt; ';
        print '<span>' . $action->getDescription() . "</span>";
    }
}
?>
</p>
</div>

<div id="navbar">
<img src="<?=getMMCLogo()?>" alt="Mandriva" id="logo" />
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

<div id="content">
    <div id="section">
