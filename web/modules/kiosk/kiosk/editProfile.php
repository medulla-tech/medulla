<?php
/**
 * (c) 2018-2022 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
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

// Import the css needed - using consolidated kiosk.css

//Import the functions and classes needed
require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/kiosk/includes/functions.php");
require_once("modules/kiosk/includes/html.inc.php");
require_once("modules/imaging/includes/class_form.php");

require("graph/navbar.inc.php");
require("modules/kiosk/kiosk/localSidebar.php");
?>

<link rel="stylesheet" href="modules/kiosk/graph/css/kiosk.css" />
<link rel="stylesheet" href="jsframework/lib/pluginjqueryjtree/themes/default/style.min.css" />
<?php

if(isset($_SESSION['sharings'])) {
    $sharings = $_SESSION['sharings'];
} else {
    $sharings = $_SESSION['sharings'] = xmlrpc_pkgs_search_share(["login" => $_SESSION["login"]]);
}

  // Get all packages for this sharings
  if($sharings['config']['centralizedmultiplesharing'] == true) {
      $packages = xmlrpc_get_all_packages($_SESSION['login'], $sharings['config']['centralizedmultiplesharing'], -1, -1, $filter);
  } else {
      $packages = xmlrpc_xmppGetAllPackages($filter, -1, -1);
  }

$profile = xmlrpc_get_profile_by_id($_GET['id']);
// Get the list of the packages
$available_packages_str = "";
$restricted_packages_str = "";
$allowed_packages_str = "";

$allowedPackages = [];
$restrictedPackages = [];

// Get packages from the profile and divide it into two list : restrictedPackages and allowedPackages
foreach($profile['packages'] as $tmpPackage) {
    if($tmpPackage['status'] == 'restricted') {
        $restrictedPackages[$tmpPackage['name']] = $tmpPackage['uuid'];
    } else {
        $allowedPackages[$tmpPackage['name']] = $tmpPackage['uuid'];
    }
}


// The packages are contained into the lists :
// - available_packages
// - allowedPackages
// - restrictedPackages
$row = 0;
foreach($packages['datas']['uuid'] as $package) {
    if ($packages['datas']['associateinventory'][$row] == 1) {
        if(in_array($package, $allowedPackages)) {
            $allowed_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';
        } elseif(in_array($package, $restrictedPackages)) {
            $restricted_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';
        } else {
            $available_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';
        }
    }
    $row++;
}


$p = new PageGenerator(_T("Edit Profile", 'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm(array("id" => "profile-form"));

$f->push(new Table());


$f->add(new HiddenTpl("id"), array("value" => $_GET['id'], "hide" => true));
$ous = join(';', $profile['ous']);

$f->add(new HiddenTpl("ous"), array("value" => $ous, "hide" => true));
$f->add(new HiddenTpl("action"), array("value" => $_GET['action'], "hide" => true));
$f->add(new HiddenTpl("original_source"), array("value" => $profile['source'], "hide" => true));
$f->add(new HiddenTpl("owner"), array("value" => $_SESSION['login'], "hide" => true));
$f->add(new SpanElement('', "packages"));

// Section title for profile information
$f->add(new TitleElement(_T("Profile information", "kiosk")));

// -------
// Add an input for the profile name
// -------
$f->add(
    //InputTplTitle came from modules/imaging/includes/class_form.php
    new TrFormElement(_T('Profile Name', 'kiosk').":", new InputTplTitle('name', _T('Profile Name', 'kiosk'))),
    array("value" => _T($profile['name'], 'kiosk'), 'placeholder' => _T('Name', 'kiosk'), "required" => true)
);

// -------
// Add a selector to activate / desactivate the profile
// -------
$profileStatus = new SelectItemtitle("status", _T("Set the profile to active / inactive state", "kiosk"));
$profileStatus->setElements([_T('Active', "kiosk"), _T('Inactive', 'kiosk')]);
$profileStatus->setElementsVal([1,0]);
$f->add(
    new TrFormElement(_T('Profile Status', 'kiosk').":", $profileStatus),
    array("value" => $profile['active'],"required" => true)
);
$f->pop(); // End of the table

$defaultValue = (safeCount($profile['ous']) > 0 && $profile['ous'][0] != "") ? ["value" => "checked"] : [];

// Section title for package management
$f->add(new TitleElement(_T("Manage packages", "kiosk")));

if(xmlrpc_get_conf_kiosk()['enable_acknowledgements'] == true) {
    $restricted_area = '<div>
    <h1>'._T("Restricted packages", "kiosk").'</h1>
    <ol data-draggable="target" id="restricted-packages">'.$restricted_packages_str.'</ol>
    </div>';
} else {
    $restricted_area = '';
    $allowed_packages_str .= $restricted_packages_str;
}

$f->add(new SpanElement('<div id="packages">
        <div>
            <h1>'._T("Available packages", "kiosk").'</h1>
            <input type="text" id="availableFilter" value="" placeholder="'._T("Search by name ...", "pkgs").'">
            <ol data-draggable="target" id="available-packages">'.$available_packages_str.'</ol>
        </div>'.$restricted_area.'<div>
            <h1>'._T("Allowed packages", "kiosk").'</h1>
            <input type="text" id="allowedFilter" value="" placeholder="'._T("Search by name ...", "pkgs").'">
            <ol data-draggable="target" id="allowed-packages">'.$allowed_packages_str.'</ol>
        </div>
    </div>', "packages"));

// Section title for source selection
$f->add(new TitleElement(_T("Source selection", "kiosk")));

$sources = ["Entity", "Group", "LDAP", "Ou User", "Ou Machine"];
if(xmlrpc_get_conf_kiosk()['use_external_ldap'] == true) {
    $sources[] = 'ldap';
}
$select = new SelectItemtitle("source", "Source provider");
$select->setElements($sources);
$select->setElementsVal($sources);
$formatedSource = ucwords(str_replace("_", " ", $profile['source']));
$f->add(
    new TrFormElement(_T('Source', 'kiosk').": ", $select),
    array("value" => (!empty($profile['source'])) ? $formatedSource : "1")
);
// -------
// Add the OUs tree
// -------
$result = "";
$f->add(new SpanElement(
    '<div id="source-container"></div>
    <div id="ou-container">
        <input type="button" id="treeToggler" value="+" />
        <div id="jstree" role="tree">'.$result.'</div>
        <div id="users"></div>
    </div>',
    "kiosk"
));

$bo = new ValidateButtonTpl('bvalid', _T("modify", 'kiosk'), 'btnPrimary', _T("Modify the profile", "kiosk"));
//$rr = new TrFormElementcollapse($bo);
$bo->setstyle("text-align: center;");
$f->add($bo);

$f->pop(); // end of form

$f->display(); // display the form
?>


<script src="jsframework/lib/pluginjqueryjtree/jstree.min.js"></script>
<script src="modules/kiosk/graph/js/packages.js"></script>
<script src="modules/kiosk/graph/js/sources.js"></script>
<script src="modules/kiosk/graph/js/validate.js"></script>
<script>
jQuery(document).ready(function(){
    function applyFilter(filterSelector, targetSelector) {
        let value = jQuery(filterSelector).val().toLowerCase();
        jQuery(targetSelector).each(function() {
            jQuery(this).toggle(jQuery(this).text().toLowerCase().indexOf(value) > -1);
        });
    }

    jQuery("#availableFilter").on("keyup", function() {
        applyFilter("#availableFilter", "#available-packages li");
    });

    jQuery("#allowedFilter").on("keyup", function() {
        applyFilter("#allowedFilter", "#allowed-packages li");
    });
});
</script>