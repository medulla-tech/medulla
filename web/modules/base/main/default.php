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

require("graph/navbar.inc.php");

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

$i = 1;

function display_mod($mod) {
    if (!$mod->hasVisible()) {
        return;
    }

    global $i;
?>
    <div class="column" id="col<?php echo $i; ?>" style="width:250px;">
                <div id="<?php echo $mod->getName(); ?>" class="portlet">
                    <div class="portlet-header"><?php echo $mod->getDescription(); ?></div>
                    <div class="portlet-content">
    <?php foreach (getSorted($mod->getSubmodules()) as $submod) {
    ?>

                    <?php display_submod($submod,$mod); $i++; ?>
    <?php
    }
    ?>
            </div>
        </div>
    </div>
<?php
}

$MMCApp =& MMCApp::getInstance();
$modules = getSorted($MMCApp->getModules());
$nb_modules = count($modules);

$p = new PageGenerator(_("Home"));
$p->display();

?>
    <div id="home">
        <?php
        foreach($modules as $key => $mod) {
            display_mod($mod);
        }
        ?>
    </div>
    <div class="clearer"></div>
</div>

<script type="text/javascript" src="jsframework/portlet.js"></script>
