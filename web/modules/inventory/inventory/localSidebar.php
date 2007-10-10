<?

$sidemenu= new SideMenu();

$sidemenu->setClass("inventory");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("General"), "inventory", "inventory", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Hardware"), "inventory", "inventory", "hardware"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Network"), "inventory", "inventory", "network"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Controller"), "inventory", "inventory", "controller"));

if (isExpertMode()) {
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Drive"), "inventory", "inventory", "drive"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Input"), "inventory", "inventory", "input"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Memory"), "inventory", "inventory", "memory"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Monitor"), "inventory", "inventory", "monitor"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Port"), "inventory", "inventory", "port"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Printer"), "inventory", "inventory", "printer"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Sound"), "inventory", "inventory", "sound"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("Storage"), "inventory", "inventory", "storage"));
	$sidemenu->addSideMenuItem(new SideMenuItem(_T("VideoCard"), "inventory", "inventory", "videocard"));
}
?>
