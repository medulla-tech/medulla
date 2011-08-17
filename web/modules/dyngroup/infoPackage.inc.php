<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/dyngroup/includes/includes.php");
require_once("modules/pulse2/version.php");

$mod = new Module("dyngroup");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Dyngroup", "dyngroup"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(700);


$MMCApp =& MMCApp::getInstance();

/* Get the base module instance */
$base = &$MMCApp->getModule('base');

/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

if (!empty($submod)) {

    /* Dynamic groups */

    if (isDynamicEnable()) {
        if (isProfilesEnable()) {
            $page = new Page("computersprofilecreator",_T("Computers Profile Creator","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/tab.php");

            $tab = new Tab("tabdyn", _T("Profile creation's tab from dynamic request", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabsta", _T("Profile creation's tab from machine list", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabfromfile", _T("Profile creation's tab from file import", "dyngroup"));
            $page->addTab($tab);
            $submod->addPage($page);

            $page = new Page("computersprofilecreatesubedit",_T("Computers Profile Creator Sub Request Editor","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/tab.php");
            $page->setOptions(array("visible"=>False));

            $tab = new Tab("tabdyn", _T("Profile creation's tab from dynamic request", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabsta", _T("Profile creation's tab from machine list", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabfromfile", _T("Profile creation's tab from file import", "dyngroup"));
            $page->addTab($tab);
            $submod->addPage($page);

            $page = new Page("computersprofilecreatesubdel",_T("Computers Profile Creator Sub Request Delete","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/tab.php");
            $page->setOptions(array("visible"=>False));

            $tab = new Tab("tabdyn", _T("Profile creation's tab from dynamic request", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabsta", _T("Profile creation's tab from machine list", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabfromfile", _T("Profile creation's tab from file import", "dyngroup"));
            $page->addTab($tab);
            $submod->addPage($page);

            $page = new Page("computersprofileedit",_T("Computers Profile Editor","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/edithead.php");
            $page->setOptions(array("visible"=>False));
            $submod->addPage($page);

            $page = new Page("computersprofilesubedit",_T("Computers Profile Sub Request Editor","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/edithead.php");
            $page->setOptions(array("visible"=>False, "noACL"=>True));
            $submod->addPage($page);

            $page = new Page("computersprofilesubdel",_T("Computers Profile Sub Request Delete","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/edithead.php");
            $page->setOptions(array("visible"=>False, "noACL"=>True));
            $submod->addPage($page);

            $page = new Page("list_profiles",_T("List all profiles of computers","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/list_profiles.php");
            $submod->addPage($page);
        }
        $page = new Page("computersgroupcreator",_T("Computers Group Creator","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/tab.php");

        $tab = new Tab("tabdyn", _T("Dynamic group creation's tab", "dyngroup"));
        $page->addTab($tab);

        $tab = new Tab("tabsta", _T("Static group creation's tab", "dyngroup"));
        $page->addTab($tab);

        $tab = new Tab("tabfromfile", _T("Static group creation from import's tab", "dyngroup"));
        $page->addTab($tab);
        $submod->addPage($page);

        $page = new Page("computersgroupcreatesubedit",_T("Computers Group Creator Sub Request Editor","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/tab.php");
        $page->setOptions(array("visible"=>False));

        $tab = new Tab("tabdyn", _T("Dynamic group creation's tab", "dyngroup"));
        $page->addTab($tab);

        $tab = new Tab("tabsta", _T("Static group creation's tab", "dyngroup"));
        $page->addTab($tab);

        $tab = new Tab("tabfromfile", _T("Static group creation from import's tab", "dyngroup"));
        $page->addTab($tab);
        $submod->addPage($page);

        $page = new Page("computersgroupcreatesubdel",_T("Computers Group Creator Sub Request Delete","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/tab.php");
        $page->setOptions(array("visible"=>False));

        $tab = new Tab("tabdyn", _T("Dynamic group creation's tab", "dyngroup"));
        $page->addTab($tab);

        $tab = new Tab("tabsta", _T("Static group creation's tab", "dyngroup"));
        $page->addTab($tab);

        $tab = new Tab("tabfromfile", _T("Static group creation from import's tab", "dyngroup"));
        $page->addTab($tab);
        $submod->addPage($page);

        $page = new Page("computersgroupedit",_T("Computers Group Editor","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/edithead.php");
        $page->setOptions(array("visible"=>False));
        $submod->addPage($page);

        $page = new Page("computersgroupsubedit",_T("Computers Group Sub Request Editor","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/edithead.php");
        $page->setOptions(array("visible"=>False, "noACL"=>True));
        $submod->addPage($page);

        $page = new Page("computersgroupsubdel",_T("Computers Group Sub Request Delete","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/edithead.php");
        $page->setOptions(array("visible"=>False, "noACL"=>True));
        $submod->addPage($page);

        $page = new Page("tmpdisplay",_T("Temporary result display","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/tmpdisplay.php");
        $page->setOptions(array("visible"=>False));
        $submod->addPage($page);
    } else {
        if (isProfilesEnable()) {
            $page = new Page("computersprofilecreator",_T("Computers Profile Creator","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
            $submod->addPage($page);

            $page = new Page("computersprofileedit",_T("Computers Profile Editor","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
            $page->setOptions(array("visible"=>False));
            $submod->addPage($page);

            $page = new Page("list_profiles",_T("List all profiles of computers","dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/list_profiles.php");
            $submod->addPage($page);
        }
        $page = new Page("computersgroupcreator",_T("Computers Group Creator","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
        $submod->addPage($page);

        $page = new Page("computersgroupedit",_T("Computers Group Editor","dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
        $page->setOptions(array("visible"=>False));
        $submod->addPage($page);
    }

    $page = new Page("display",_T("Display a groups of computers","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/display.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);

    $page = new Page("edit_share",_T("Share a group of computers","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/edit_share.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);

    $page = new Page("creator_step2",_T("Second page of result/request group creator","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/save.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);

    $page = new Page("save",_T("Save a group of computers","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/save.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);

    $page = new Page("save_detail",_T("Detailed page of save a group of computers","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/save_detail.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);

    $page = new Page("list",_T("List all groups of computers","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/list.php");
    $submod->addPage($page);

    $page = new Page("ajaxListGroups",_T("List all groups of computers","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/ajaxListGroups.php");
    $page->setOptions(array("visible"=>False, "AJAX" =>True));
    $submod->addPage($page);

    $page = new Page("delete_group",_T("Delete a group of computers","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/delete_group.php");
    $page->setOptions(array("visible"=>False, "noHeader" =>True));
    $submod->addPage($page);

    $page = new Page("details",_T("Group of computers details","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/details.php");
    $page->setOptions(array("visible"=>False, "AJAX" =>True));
    $submod->addPage($page);

    $page = new Page("remove_machine",_T("Remove a computer from a computers group","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/remove_machine.php");
    $page->setOptions(array("visible"=>False, "noHeader" =>True));
    $submod->addPage($page);

    $page = new Page("ajaxAutocompleteSearch");
    $page->setFile("modules/dyngroup/dyngroup/ajaxAutocompleteSearch.php");
    $page->setOptions(array("visible"=>False, "AJAX" =>True));
    $submod->addPage($page);

    $page = new Page("ajaxAutocompleteSearchWhere");
    $page->setFile("modules/dyngroup/dyngroup/ajaxAutocompleteSearchWhere.php");
    $page->setOptions(array("visible"=>False, "AJAX" =>True));
    $submod->addPage($page);

    $page = new Page("csv",_T("Csv's export", "dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/csv.php");
    $page->setOptions(array("visible"=>False, "noHeader"=>True));
    $submod->addPage($page);

    $page = new Page("updateMachineCache",_T("Update machine cache","dyngroup"));
    $page->setFile("modules/dyngroup/dyngroup/update.php");
    $page->setOptions(array("visible"=>False));
    $submod->addPage($page);

}

unset($submod);
/* groupes dynamiques end */
?>
