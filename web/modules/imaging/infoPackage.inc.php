<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com/
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
/**
 * module declaration
 */
require_once("modules/pulse2/version.php");

$mod = new Module("imaging");
$mod->setVersion(VERSION);
$mod->setRevision(REVISION);
$mod->setDescription(_T("Imaging service", "imaging"));
$mod->setAPIVersion("0:0:0");
$mod->setPriority(600);

$submod = new SubModule("manage");
$submod->setDescription(_T("Imaging", "manage"));
$submod->setImg("modules/imaging/img/imaging");
$submod->setDefaultPage("imaging/manage/index");

$page = new Page("index", _T("Server status", "imaging"));
$submod->addPage($page);

$page = new Page("master", _T("Manage masters", "imaging"));
$submod->addPage($page);
$page = new Page("master_remove", _T("Remove master", "imaging"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);
$page = new Page("master_delete", _T("Delete master", "imaging"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);
$page = new Page("master_edit", _T("Edit master", "imaging"));
$page->setOptions(array("visible" => False));
$submod->addPage($page);
$page = new Page("master_add", _T("Add master", "imaging"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);
$page = new Page("master_iso", _T("Create iso from master", "imaging"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("service", _T("Manage boot services", "imaging"));
$submod->addPage($page);
$page = new Page("service_edit", _T("Edit service", "imaging"));
$page->setOptions(array("visible" => False));
$submod->addPage($page);
$page = new Page("service_del", _T("Remove service", "imaging"));
$page->setOptions(array("noHeader" => True, "visible" => False));
$submod->addPage($page);
$page = new Page("service_add", _T("Add service", "imaging"));
$page->setOptions(array("noHeader" => True, "visible" => False));
$submod->addPage($page);
$page = new Page("service_remove", _T("Remove service", "imaging"));
$page->setOptions(array("noHeader" => True, "visible" => False));
$submod->addPage($page);
$page = new Page("service_show_used", _T("Show used services", "imaging"));
$page->setOptions(array("noHeader" => True, "visible" => False));
$submod->addPage($page);

$page = new Page("bootmenu", _T("Default boot menu", "imaging"));
$submod->addPage($page);
$page = new Page("bootmenu_up", _T("Up service", "imaging"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);
$page = new Page("bootmenu_down", _T("Down service", "imaging"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);
$page = new Page("bootmenu_edit", _T("Down service", "imaging"));
$page->setOptions(array("visible" => False));
$submod->addPage($page);

$page = new Page("postinstall", _T("Post-imaging scripts", "imaging"));
$submod->addPage($page);
$page = new Page("postinstall_edit", _T("Edit post-imaging script", "imaging"));
$page->setOptions(array("visible" => False));
$submod->addPage($page);
$page = new Page("postinstall_duplicate", _T("Edit post-imaging script", "imaging"));
$page->setOptions(array("visible" => False));
$submod->addPage($page);
$page = new Page("postinstall_create_boot_service", _T("Create boot service from postinstall script", "imaging"));
$page->setOptions(array("noHeader" => True, "visible" => False));
$submod->addPage($page);
$page = new Page("postinstall_redirect_to_boot_service", _T("Redirect to Boot Services page", "imaging"));
$page->setOptions(array("noHeader" => True, "visible" => False));
$submod->addPage($page);
$page = new Page("postinstall_delete", _T("Delete post-imaging script", "imaging"));
$page->setOptions(array("visible" => False, "noHeader" => True));
$submod->addPage($page);

$page = new Page("configuration", _T("Imaging configuration", "imaging"));
$submod->addPage($page);
$page = new Page("save_configuration", _T("Save an Imaging Server configuration", "imaging"));
$page->setOptions(array("visible" => False));
$submod->addPage($page);

$page = new Page("ajaxAvailableImagingServer", _T("Available Imaging Server", "imaging"));
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);
$page = new Page("imaging_server_link", _T("Link an Imaging Server", "imaging"));
$page->setOptions(array("AJAX" => True, "visible" => False));
$submod->addPage($page);

if (in_array("dyngroup", $_SESSION["modulesList"])) {
    require_once("modules/dyngroup/includes/includes.php");
    if (isProfilesEnable()) {
        if (isDynamicEnable()) {
            $page = new Page("computersprofilecreator", _T("Computers Profile Creator", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/tab.php");

            $tab = new Tab("tabdyn", _T("Profile creation's tab from dynamic request", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabsta", _T("Profile creation's tab from machine list", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabfromfile", _T("Profile creation's tab from file import", "dyngroup"));
            $page->addTab($tab);
            $submod->addPage($page);

            $page = new Page("computersprofilecreatesubedit", _T("Computers Profile Creator Sub Request Editor", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/tab.php");
            $page->setOptions(array("visible" => False));

            $tab = new Tab("tabdyn", _T("Profile creation's tab from dynamic request", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabsta", _T("Profile creation's tab from machine list", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabfromfile", _T("Profile creation's tab from file import", "dyngroup"));
            $page->addTab($tab);
            $submod->addPage($page);

            $page = new Page("computersprofilecreatesubdel", _T("Computers Profile Creator Sub Request Delete", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/tab.php");
            $page->setOptions(array("visible" => False));

            $tab = new Tab("tabdyn", _T("Profile creation's tab from dynamic request", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabsta", _T("Profile creation's tab from machine list", "dyngroup"));
            $page->addTab($tab);

            $tab = new Tab("tabfromfile", _T("Profile creation's tab from file import", "dyngroup"));
            $page->addTab($tab);
            $submod->addPage($page);

            $page = new Page("computersprofileedit", _T("Computers Profile Editor", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/edithead.php");
            $page->setOptions(array("visible" => False));
            $submod->addPage($page);

            $page = new Page("computersprofilesubedit", _T("Computers Profile Sub Request Editor", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/edithead.php");
            $page->setOptions(array("visible" => False, "noACL" => True));
            $submod->addPage($page);

            $page = new Page("computersprofilesubdel", _T("Computers Profile Sub Request Delete", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/edithead.php");
            $page->setOptions(array("visible" => False, "noACL" => True));
            $submod->addPage($page);

            $page = new Page("list_profiles", _T("List all profiles of computers", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/list_profiles.php");
            $submod->addPage($page);
        } else {
            $page = new Page("computersprofilecreator", _T("Computers Profile Creator", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
            $submod->addPage($page);

            $page = new Page("computersprofileedit", _T("Computers Profile Editor", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
            $page->setOptions(array("visible" => False));
            $submod->addPage($page);

            $page = new Page("list_profiles", _T("List all profiles of computers", "dyngroup"));
            $page->setFile("modules/dyngroup/dyngroup/list_profiles.php");
            $submod->addPage($page);
        }

        // imaging on group
        $page = new Page("groupregister_target", _T("Register a profile in the imaging module", "imaging"));
        $page->setFile("modules/imaging/imaging/register_target.php");
        $page->setOptions(array("visible" => False));
        $submod->addPage($page);


        $page = new Page("groupimgtabs", _T("Imaging on group", "imaging"));
        $page->setFile("modules/imaging/imaging/tabs.php");
        $page->setOptions(array("visible" => False));
        $tab = new Tab("grouptabbootmenu", _T("Boot menu", "imaging"));
        $page->addTab($tab);
        $tab = new Tab("grouptabimages", _T("Images and Masters", "imaging"));
        $page->addTab($tab);
        $tab = new Tab("grouptabservices", _T("Boot services", "imaging"));
        $page->addTab($tab);
        $tab = new Tab("grouptabimlogs", _T("Imaging Log", "imaging"));
        $page->addTab($tab);
        $tab = new Tab("grouptabconfigure", _T("Menu configuration", "imaging"));
        $page->addTab($tab);
        $submod->addPage($page);
        $page = new Page("groupbootmenu_remove", _T("Remove from boot menu", "imaging"));
        $page->setFile("modules/imaging/imaging/bootmenu_remove.php");
        $page->setOptions(array("visible" => False, "noHeader" => True));
        $submod->addPage($page);
        $page = new Page("display", _T("Display computers group content", "dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/display.php");
        $page->setOptions(array("visible" => False));
        $submod->addPage($page);
        $page = new Page("delete_group", _T("Delete a group of computers", "dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/delete_group.php");
        $page->setOptions(array("visible" => False, "noHeader" => True));
        $submod->addPage($page);
        $page = new Page("computersgroupedit", _T("Computers Group Editor", "dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/groupshead.php");
        $page->setOptions(array("visible" => False));
        $submod->addPage($page);
        $page = new Page("edit_share", _T("Share a group of computers", "dyngroup"));
        $page->setFile("modules/dyngroup/dyngroup/edit_share.php");
        $page->setOptions(array("visible" => False));
        $submod->addPage($page);

        if (in_array("msc", $_SESSION["modulesList"])) {
            $page = new Page("groupmsctabs", _T("Secure control on a group of computers", "msc"));
            $page->setFile("modules/msc/msc/tabs.php");
            $page->setOptions(array("visible" => False));

            $tab = new Tab("grouptablaunch", _T("MSC launch tab for a group", "msc"));
            $page->addTab($tab);

            $tab = new Tab("grouptabbundle", _T("MSC bundle tab for a group", "msc"));
            $page->addTab($tab);

            $tab = new Tab("grouptablogs", _T("MSC logs tab for a group", "msc"));
            $page->addTab($tab);

            $tab = new Tab("grouptabhistory", _T("MSC history tab for a group", "msc"));
            $page->addTab($tab);

            $submod->addPage($page);
        }
    }
}

$mod->addSubmod($submod);
$MMCApp = & MMCApp::getInstance();
$MMCApp->addModule($mod);

/* put in base/computer */
/* Get the base module instance */
$base = &$MMCApp->getModule('base');
/* Get the computers sub-module instance */
$submod = & $base->getSubmod('computers');

if (!empty($submod)) {
    // imaging on computer
    $page = new Page("register_target", _T("Register a computer in the imaging module", "imaging"));
    $page->setFile("modules/imaging/imaging/register_target.php");
    $page->setOptions(array("visible" => False));
    $submod->addPage($page);

    $page = new Page("createCustomMenuStaticGroup", _T("Create a static group containing computers with custom imaging menu", "imaging"));
    $page->setFile("modules/imaging/imaging/createCustomMenuStaticGroup.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    $page = new Page("imgtabs", _T("Imaging on computer", "imaging"));
    $page->setFile("modules/imaging/imaging/tabs.php");
    $page->setOptions(array("visible" => False));
    $tab = new Tab("tabbootmenu", _T("Boot menu", "imaging"));
    $page->addTab($tab);
    $tab = new Tab("tabimages", _T("Images and Masters", "imaging"));
    $page->addTab($tab);
    $tab = new Tab("tabservices", _T("Boot services", "imaging"));
    $page->addTab($tab);
    $tab = new Tab("tabimlogs", _T("Imaging Log", "imaging"));
    $page->addTab($tab);
    $tab = new Tab("tabconfigure", _T("Menu configuration", "imaging"));
    $page->addTab($tab);
    $submod->addPage($page);

    // actions on computer & groups
    $page = new Page("bootmenu_remove", _T("Remove from boot menu", "imaging"));
    $page->setFile("modules/imaging/imaging/bootmenu_remove.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);
    $page = new Page("showtarget", _T("Show target that use that image", "imaging"));
    $page->setFile("modules/imaging/imaging/showtarget.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);
    $page = new Page("showsyncstatus", _T("Show sync status", "imaging"));
    $page->setFile("modules/imaging/imaging/showsyncstatus.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    $page = new Page("ajaxStatus");
    $page->setFile("modules/imaging/imaging/ajaxStatus.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxImages");
    $page->setFile("modules/imaging/imaging/ajaxImages.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxLogs");
    $page->setFile("modules/imaging/imaging/ajaxLogs.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxMaster");
    $page->setFile("modules/imaging/imaging/ajaxMaster.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxMasterLevel2");
    $page->setFile("modules/imaging/imaging/ajaxMasterLevel2.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxService");
    $page->setFile("modules/imaging/imaging/ajaxService.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxServiceLevel2");
    $page->setFile("modules/imaging/imaging/ajaxServiceLevel2.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxBootmenu");
    $page->setFile("modules/imaging/imaging/ajaxBootmenu.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);
    $page = new Page("ajaxConfiguration");
    $page->setFile("modules/imaging/imaging/ajaxConfiguration.php");
    $page->setOptions(array("AJAX" => True, "visible" => False));
    $submod->addPage($page);

    $page = new Page("addservice", _T("Add a service to a target", "msc"));
    $page->setFile("modules/imaging/imaging/addservice.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);
    $page = new Page("editservice", _T("Edit parameters of a service on a target", "msc"));
    $page->setFile("modules/imaging/imaging/addservice.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);
    $page = new Page("delservice", _T("Remove a service from a target", "msc"));
    $page->setFile("modules/imaging/imaging/addservice.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    $page = new Page("addimage", _T("Add a image to a target", "msc"));
    $page->setFile("modules/imaging/imaging/addimage.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);
    $page = new Page("editimage", _T("Edit parameters of a image on a target", "msc"));
    $page->setFile("modules/imaging/imaging/addimage.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);
    $page = new Page("images_delete", _T("Delete image", "imaging"));
    $page->setFile("modules/imaging/imaging/images_delete.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);
    $page = new Page("images_iso", _T("Create iso image", "imaging"));
    $page->setFile("modules/imaging/imaging/images_iso.php");
    $page->setOptions(array("visible" => False, "noHeader" => True));
    $submod->addPage($page);

    unset($submod);
}
?>
