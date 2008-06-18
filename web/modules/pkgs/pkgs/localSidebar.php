<?

$sidemenu= new SideMenu();
$sidemenu->setClass("pkgs");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Packages list", 'pkgs'), "pkgs", "pkgs", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Add a packages", 'pkgs'), "pkgs", "pkgs", "add"));

?>
