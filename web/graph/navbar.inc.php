<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
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
/* $Id$ */

require_once("navbartools.inc.php");

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
        $mode=_("Expert mode");
      } else { $mode = _("Standard mode"); }

    ?>

    <li id="expertmode"><a href="<?php echo $root   ?>includes/switchmode.php"><?php echo $mode; ?></a></li>
    <?php echo "<li id=\"disconnect\"><a title=\""._("logout")."\" href=\"".$root."logout/index.php\"";
        echo " onclick=\"showPopup(event,'".$root."logout/index.php'); return false;\">";
        echo _("Logout ").'&nbsp;'.$_SESSION['login'];
        echo "</a></li>";
    ?>

  </ul>
</div>

<p class="path">
<?php
//new path automatic creation
if ($_GET["module"]) {//if not main page
        print '<a href="main.php">'._("Home").'</a>';
        $LMCApp =&LMCApp::getInstance();
        $mod = $LMCApp->_modules[$_GET['module']];
        $submod = $mod->_submod[$_GET['submod']];
        print ' &gt; ';
        if (($_GET["module"]."/".$_GET["submod"]."/".$_GET["action"])==$submod->_defaultpage) {
            print $submod->getDescription();
        } else {
            list($m,$s,$a) = split('/',$submod->_defaultpage,3);
            print '<a href="main.php?module='.$m.'&amp;submod='.$s.'&amp;action='.$a.'">'.$submod->getDescription().'</a>';
            print ' &gt; ';
            $action = $submod->_pages[$_GET["action"]];

            if (is_object($action)) {
                print $action->getDescription();
            }
        }
} else {
        print _("Home");
}
?>
</p>
</div>


<div id="navbar">
<img src="<?php echo $root; ?>img/common/logoLinbox_navbar.gif" alt="Linbox" id="logo" style= "float: right;" width="180" height="44" />
<ul>
<?php


global $conf;


autoGenerateNavbar(); //auto generation of navbar for new modules;

includeNavbarModule(fetchModulesList($conf["global"]["rootfsmodules"]));

if ($_SESSION["login"]=='root') {
    $favact = "_disabled";
} else {
    $favact = "";
}

?>
</ul>

<style type="text/css">
#navbar ul li#fav { 				width: 70px; }
                #navbar ul li#fav a {         background: url("img/navbar/fav<?= $favact?>.png") no-repeat transparent;
                                        background-position: 50% 10px;}
                #navbar ul li#fav a:hover {   background: url("img/navbar/fav<?= $favact?>.png") no-repeat transparent;
                                        background-position: 50% 10px	}

</style>
</div>

<div id="content">


<div id="popup" class="popup" style="display: none;">
    <div style="float:right"><a href="#" onclick="getStyleObject('popup').display='none'; return false;"><img src="img/common/icn_close.png" alt ="[x]"/></a></div>
    <div id="__popup_container">
        <?= _("If this phrase does not change, you browser is not supported by the LMC application"); ?>
    </div>

</div>

<?php //<div id="activeTab"></div>
?>

<div id="sectionContainer">

<?php
if (isset($sidebar))
{
  require("sidebar.inc.php");
}
?>

<div id="sectionTopRight">
<?php
if (isset($topLeft))
{
echo "<div id=\"sectionTopLeft\">";
}
?>
<img src="<?php echo $root; ?>img/common/spacer.gif" alt="" />
</div>
<?php
if (isset($topLeft))
{
echo "</div>";
}
?>

<div id="section">

<?php
unset($sidebar);
?>
