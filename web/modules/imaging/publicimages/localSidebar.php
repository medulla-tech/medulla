<?

$sidemenu= new SideMenu();

$sidemenu->setClass("imaging");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Public Images"), "imaging", "publicimages", "index", "modules/imaging/graph/img/publicimages_active.png", "modules/imaging/graph/img/publicimages_inactive.png"));

?>
