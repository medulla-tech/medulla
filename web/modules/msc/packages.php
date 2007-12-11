<?

require("graph/navbar.inc.php");
require("localSidebar.php");
require("modules/msc/includes/package_api.php");

$p = new PageGenerator(_T("Packages"));
$p->setSideMenu($sidemenu);
$p->display(); 

$a_packages = array();
$a_pversions = array();
foreach (getAllPackages() as $package) {
    $a_packages[] = $package->label;
    $a_pversions[] = $package->version;
}

$n = new ListInfos($a_packages, _T("Package"));
$n->addExtraInfo($a_pversions, _T("Version"));

$n->addActionItem(new ActionItem(_T("Launch", "msc"),"start_tele_diff", "start", "msc", "base", "computers"));
$n->addActionItem(new ActionItem(_T("Details", "msc"),"package_detail", "detail", "msc", "base", "computers"));

$n->drawTable(0);


?>
<style>
li.detail a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/info.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

</style>

