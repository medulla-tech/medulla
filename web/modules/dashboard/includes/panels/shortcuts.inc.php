<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

include_once("modules/dashboard/includes/panel.class.php");

$options = array(
    "class" => "ShortcutsPanel",
    "id" => "shortcuts",
    "title" => _T("Shortcuts", "dashboard"),
);

class ShortcutsPanel extends Panel {

    function display_content() {
        $this->display_links("base", "users", array("add", "passwd"));
        $this->display_links("base", "groups", array("add"));
        $this->display_links("samba", "shares", array("add", "index"));
        $this->display_links("network", "network", array("index", "subnetindex"));
    }

    function display_links($module, $submod, $pages) {
        $MMCApp =& MMCApp::getInstance();
        $moduleObj = $MMCApp->getModule($module);
        if ($moduleObj) {
            $submodObj = $moduleObj->getSubmod($submod);
            if ($submodObj) {
                $submodPages = $submodObj->getPages();
                $hasPages = false;
                $links = "<ul>";
                foreach($pages as $page) {
                    if (isset($submodPages[$page])) {
                        $pageObj = $submodPages[$page];
                        $links .= '<li><a href="'. urlStrRedirect("$module/$submod/$page") .'">' . $pageObj->getDescription() . '</a></li>';
                        $hasPages = true;
                    }
                }
                $links .= "</ul>";

                if ($hasPages) {
                    echo <<< SUBPANEL
                    <div class="subpanel">
                        <h4>{$submodObj->getDescription()}</h4>
                        $links
                    </div>
SUBPANEL;
                }
            }
        }
    }
}


?>
