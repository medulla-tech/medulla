<?

require("graph/navbar.inc.php");
require("modules/base/computers/localSidebar.php");

$p = new PageGenerator(_T("General informations"));
$sidemenu->forceActiveItem("index");
$p->setSideMenu($sidemenu);
$p->display(); 

print $_GET["uuid"];

?>