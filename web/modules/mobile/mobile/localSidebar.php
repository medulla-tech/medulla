<?php
/**

*/
require_once("modules/mobile/includes/xmlrpc.php");

$sidemenu = new SideMenu();
$sidemenu->setClass("mobile");
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All devices", 'mobile'), "mobile", "mobile", "index"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All devices (GLPI)", 'mobile'), "mobile", "mobile", "glpiPhonesList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("All groups", 'mobile'), "mobile", "mobile", "groups"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Configurations", 'mobile'), "mobile", "mobile", "configurations"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Applications", 'mobile'), "mobile", "mobile", "applications"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Files", 'mobile'), "mobile", "mobile", "files"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Push messages", 'mobile'), "mobile", "mobile", "pushMessages"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Messages", 'mobile'), "mobile", "mobile", "messaging"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Network Filtering", 'mobile'), "mobile", "mobile", "netfilterSettings"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Contacts sync", 'mobile'), "mobile", "mobile", "contactsList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Photos", 'mobile'), "mobile", "mobile", "photosList"));
$sidemenu->addSideMenuItem(new SideMenuItem(_T("Device Export/Import", 'mobile'), "mobile", "mobile", "deviceExport"));


$_show_admin_menu = false;
try {
    $current_hmdm_user = xmlrpc_get_current_hmdm_user();
    if ($current_hmdm_user && isset($current_hmdm_user['userRole'])) {
        $role_name = $current_hmdm_user['userRole']['name'] ?? '';
        $_show_admin_menu = (stripos($role_name, 'admin') !== false);
        error_log("HMDM User: " . ($current_hmdm_user['login'] ?? 'unknown') . ", Role: $role_name, Show admin menu: " . ($_show_admin_menu ? 'YES' : 'NO'));
    }
} catch (Exception $e) {
    error_log("Error checking HMDM user role: " . $e->getMessage());
}

if ($_show_admin_menu) {
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Users", 'mobile'), "mobile", "mobile", "mobileUsers"));
    $sidemenu->addSideMenuItem(new SideMenuItem(_T("Roles", 'mobile'), "mobile", "mobile", "mobileRoles"));
}
 ?>
