<?php
require_once("modules/dyngroup/includes/dyngroup.php");

$sidemenu= new SideMenu();
$sidemenu->setClass("dyngroup");

                                                 
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All groups"), "dyngroup", "dyngroup",  "list"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a group"), "dyngroup", "dyngroup", "creator"));
                                                 
$max = dyngroup_last_id();
$i = 0;

while ($i < $max) {
    $group = new Dyngroup($i);
    if ($group->getName()) {
        $name = $group->getName();
        
        if ($group->canShow()) {
            $sidemenu->addSideMenuItem(
                new SideMenuItem(
                    sprintf(_T("Display %s '%s'"), ($group->isGroup()?_("group"):_("request")), $name),
                    "dyngroup", "dyngroup", "display&id=$i"
                )
            );
        }
    }
    $i++;
}


?>
