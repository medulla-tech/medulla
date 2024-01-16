<?php
global $conf;
$displayname = (!empty($conf['global']['glpidisplayname'])) ? $conf['global']['glpidisplayname'] : "glpi";
$sidemenu = new SideMenu();
$sidemenu->setClass("computers");
$sidemenu->addSideMenuItem(new SideMenuItem(_("All computers"), "base", "computers", "machinesList"));
$sidemenu->addSideMenuItem(new SideMenuItem(sprintf(_("All computers %s"), $displayname), "base", "computers", "machinesListglpi"));

if (canAddComputer()) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_("Add computer"), "base", "computers", "add"));
}

if (in_array("glpi", $_SESSION["modulesList"])) {
    require("modules/glpi/glpi/localSidebar.php");
}

if (in_array("dyngroup", $_SESSION["modulesList"])) {
    require("modules/dyngroup/dyngroup/localSidebar.php");
}

if (in_array("inventory", $_SESSION["modulesList"])) {
    require("modules/inventory/inventory/localComputersSidebar.php");
}

if (in_array("xmppmaster", $_SESSION["modulesList"])) {
    require("modules/xmppmaster/xmppmaster/localSidebar.php");
}


?>
