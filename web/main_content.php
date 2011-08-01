
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

/* bord haut gauche arrondi */
$topLeft = 1;

global $acl_error;
if ($acl_error) {
  print "<div id=\"errorCode\">$acl_error</div>";
}

/* inclusion header HTML */
require("graph/navbar.inc.php");
?>

<!-- Définition de styles locaux à cette page -->
<style type="text/css">
<!--

#section, #sectionTopRight, #sectionBottomLeft {
        margin: 0 0 0 17px;
}

#sectionTopRight {
        border-left: none;
}

#sectionTopLeft {
    height: 9px;
        padding: 0;
        margin: 0;
        background: url("<?php echo $root; ?>img/common/sectionTopLeft.gif") no-repeat top left transparent;
}

div.membarfree {
        border-right: 1px solid #27537C;
        height: 12px;
        background: url("<?php echo $root; ?>img/main/bg_status_blue.gif") repeat-x left top transparent;
        padding: 0;
        margin: 0;
}

div.membarused {
        border: none;
        background: red;
        height: 12px;
        background: url("<?php echo $root; ?>img/main/bg_status_orange.gif") repeat-x right top transparent;
        overflow: hidden;
        float: left;
        padding: 0;
        display: inline;
}

div.membarcache {
        height: 12px;
        background: url("<?php echo $root; ?>img/main/bg_status_green.gif") repeat-x right top transparent;
        float: left;
        padding: 0;
        margin: 0;
}

*html div.membarused { margin: 0 -4px 0 0; } /* pour IE/PC */
*html div.membarcache { margin: 0 -4px 0 0; } /* pour IE/PC */

div.left {
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        float: right;
        width: 400px;
        padding: 10px;
        display: block;
        margin: 0;
        position: relative;
}

div.right {
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        margin-right: 445px;
        padding: 10px;
        display: block;
        position: relative;
}

#accueilPad {
        overflow: auto;
}

#accueilPad h2,
#statusPad h2,
#accueilPad td {
        text-align: center;
}

#accueilPad h2,
#statusPad h2 {
	font-size: 14px;
}

#accueilPad table {
	color: #666;
	border: none;
	border-width: 0px;
	width: auto;
}

#accueilPad td {
	border: none;
	border-width: none;
	padding: 0px;
}

form { padding-top: 10px; }


.submod {
    background-color: #E5E5E5;
    margin: 0.7em;
    padding: 0.7em;
    -moz-border-radius: 5px;
}

.module {
    float: left;
    background-color: #EEE;
    margin: 0.7em;
    padding: 0.7em;
    -moz-border-radius: 10px;
    width: 180px;
}

ul {
    margin: 0.5em;
    padding: 0.5em;
}

-->
</style>




<h2><?php echo  _("Home") ?></h2>

<div class="fixheight"></div>
<?php


function display_page($page,$submod,$mod) {
    if ($page->getDescription() && $page->isVisible()) {
        $url = urlStr($mod->getName()."/".$submod->getName()."/".$page->_action);
        if (hasCorrectAcl($mod->getName(),$submod->getName(),$page->_action)) {
            echo "<li><a href=\"$url\">".$page->getDescription()."</a></li>";
        } else {
            echo "<li style=\"color: #BBB;\">".$page->getDescription()."</li>";
        }
    }
}

function display_submod($submod,$mod) {
    if (!$submod->hasVisible()) {
        return;
    }
    echo '<div class="submod">';
    ?> <img src="<?php echo  $submod->_img ?>_select.png" alt="" style="float:right;" /><?php
    /*if (!$submod->_visibility) { //if submod not visible
        return;
    }*/
    echo '<h3>';
    $url = urlStr($submod->_defaultpage);
    echo "<a style=\"text-decoration: none;\" href=\"$url\">".$submod->getDescription()."</a><br/>";
    echo "</h3>";
    print "<ul>";
    foreach ($submod->getPages() as $page) {
        display_page($page,$submod,$mod);
    }
    print "</ul>";
    echo '</div>';
}

function display_mod($mod) {
    if (!$mod->hasVisible()) {
        return;
    }

?>
    <div class="module">
        <h2><?php echo  $mod->getDescription(); ?></h2>
        <?php foreach (getSorted($mod->getSubmodules()) as $submod) {
            display_submod($submod,$mod);
        }
        ?>
    </div>
<?php
}

        $MMCApp =& MMCApp::getInstance();

        foreach(getSorted($MMCApp->getModules()) as $key => $mod) {
            display_mod($mod);
        }

?>
<div style="clear: both;">
</div>
</div>
