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

require_once("modules/pulse2/includes/utilities.php"); # for quickGet method
require("modules/imaging/manage/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/dyngroup/includes/dyngroup.php");

global $type;
if ($_GET['action'] == 'computersprofilecreator') { $type = 1; } else { $type = 0; }

if ($type == 0) {
    $p = new TabbedPageGenerator();
    $p->setSideMenu($sidemenu);
    $p->addTop(sprintf(_T("Group creation", "dyngroup"), $_GET['name']), "modules/dyngroup/dyngroup/header.php");
    $p->addTab("tabdyn", _T("Dynamic group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/creator.php", array('type'=>$type));
    $p->addTab("tabsta", _T("Static group creation", "dyngroup"), "", "modules/dyngroup/dyngroup/add_groups.php", array('type'=>$type));
    $p->addTab("tabfromfile", _T("Static group creation from import", "dyngroup"), "", "modules/dyngroup/dyngroup/import_from_file.php", array('type'=>$type));
    $p->display();
} else {
    $assoc = False;
    $gid = quickGet('id');
    $imaging_server = quickGet('imaging_server');
    if (isset($gid) && $gid != '') {
        $assoc = xmlrpc_isProfileAssociatedToImagingServer($gid);
        if ($assoc) {
            $imaging_server = xmlrpc_get_profile_imaging_server($gid);
        }
    }

    if ($assoc || (isset($imaging_server) && $imaging_server != '')) {
        $params = array('type'=>$type);
        $params['imaging_server'] = $imaging_server;
        $p = new TabbedPageGenerator();
        $p->setSideMenu($sidemenu);
        $p->addTop(sprintf(_T("Profile creation", "dyngroup"), $_GET['name']), "modules/dyngroup/dyngroup/header.php");
        $p->addTab("tabdyn", _T("Result profile creation", "dyngroup"), "", "modules/dyngroup/dyngroup/creator.php", $params);
        $p->addTab("tabsta", _T("Static profile creation", "dyngroup"), "", "modules/dyngroup/dyngroup/add_groups.php", $params);
        $p->addTab("tabfromfile", _T("Static profile creation from import", "dyngroup"), "", "modules/dyngroup/dyngroup/import_from_file.php", $params);
        $p->display();
    } else {
        $p = new PageGenerator(_T('Select this profile\'s Imaging Server', 'dyngroup'));
        $p->setSideMenu($sidemenu);

        require_once("modules/pulse2/includes/profiles_xmlrpc.inc.php");

        $f = new ValidatingForm();
        $f->add(new HiddenTpl("id"), array("value" => $gid, "hide" => True));
        $f->push(new Table());

        $imss = xmlrpc_getAllImagingServersForProfiles(true);
        $elt = array();
        $elt_values = array();
        foreach ($imss as $uuid => $imaging_server) {
            $elt[$uuid] = $imaging_server['name'];
            $elt_values[$uuid] = $uuid;
        }
        $imss = new SelectItem("imaging_server");
        $imss->setElements($elt);
        $imss->setElementsVal($elt_values);

        $f->add(
            new TrFormElement(_T("Select the imaging server for this profile.", "dyngroup"), $imss)
        );

        $f->pop();
        $f->addValidateButton("bvalid");

        $p->display();
        $f->display();
    }
}

?>

