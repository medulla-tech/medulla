<?php

$sidemenu = new SideMenu();
$sidemenu->setClass("computers");
$sidemenu->addSideMenuItem(new SideMenuItem(_("All computers"), "base", "computers", "index", "img/machines/icn_allMachines_active.gif", "img/machines/icn_allMachines_ro.gif"));

if (canAddComputer()) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_("Add computer"), "base", "computers", "add", "img/machines/icn_addMachines_active.gif", "img/machines/icn_addMachines_ro.gif"));
}

if (in_array("dyngroup", $_SESSION["modulesList"])) {
    require("modules/dyngroup/dyngroup/localSidebar.php");
}
if (in_array("monitoring", $_SESSION["modulesList"])) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Discovery", 'monitoring'), "base", "computers", "discovery"));
}
?>
