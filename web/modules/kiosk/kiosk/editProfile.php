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

// Import the css needed
require("modules/kiosk/graph/index.css");
require("modules/kiosk/graph/packages.css");

//Import the functions and classes needed
require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/kiosk/includes/functions.php");
require_once("modules/kiosk/includes/html.inc.php");
require_once("modules/imaging/includes/class_form.php");

require("graph/navbar.inc.php");
require("modules/kiosk/kiosk/localSidebar.php");
?>

<style type="text/css">
    @import url(modules/kiosk/graph/style.min.css);
</style>
<?php

if(isset($_SESSION['sharings'])){
    $sharings = $_SESSION['sharings'];
  }
  else{
    $sharings = $_SESSION['sharings'] = xmlrpc_pkgs_search_share(["login"=>$_SESSION["login"]]);
  }

  // Get all packages for this sharings
  if($sharings['config']['centralizedmultiplesharing'] == true){
    $packages = xmlrpc_get_all_packages($_SESSION['login'], $sharings['config']['centralizedmultiplesharing'], -1, -1, $filter);
  }
  else{
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
foreach($profile['packages'] as $tmpPackage)
{
    if($tmpPackage['status'] == 'restricted')
        $restrictedPackages[$tmpPackage['name']]=$tmpPackage['uuid'];
    else
        $allowedPackages[$tmpPackage['name']]=$tmpPackage['uuid'];
}


// The packages are contained into the lists :
// - available_packages
// - allowedPackages
// - restrictedPackages
$row = 0;
foreach($packages['datas']['uuid'] as $package)
{
    if(in_array($package, $allowedPackages)){
        $allowed_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';
    }
    else if(in_array($package, $restrictedPackages)){
        $restricted_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';
    }
    else{
        $available_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';

    }
    $row++;
}


$p = new PageGenerator(_T("Edit Profile",'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$f = new ValidatingForm(array("id" => "profile-form"));

$f->push(new Table());


$f->add(new HiddenTpl("id"), array("value" => $_GET['id'], "hide" => True));
$ous = join(';', $profile['ous']);

$f->add(new HiddenTpl("ous"), array("value" => $ous, "hide" => True));
$f->add(new HiddenTpl("action"), array("value" => $_GET['action'], "hide" => True));
$f->add(new SpanElement('',"packages"));


// -------
// Add an input for the profile name
// -------
$f->add(
//InputTplTitle came from modules/imaging/includes/class_form.php
    new TrFormElement(_T('Profile Name','kiosk').":", new InputTplTitle('name',_T('Profile Name','kiosk'))),
    array("value" => _T($profile['name'],'kiosk'), 'placeholder'=> _T('Name','kiosk'), "required" => True)
);

// -------
// Add a selector to activate / desactivate the profile
// -------
$profileStatus = new SelectItemtitle("status",_T("Set the profile to active / inactive state", "kiosk"));
$profileStatus->setElements([_T('Active',"kiosk"), _T('Inactive','kiosk')]);
$profileStatus->setElementsVal([1,0]);
$f->add(
    new TrFormElement(_T('Profile Status','kiosk').":", $profileStatus),
    array("value" => $profile['active'],"required" => True)
);
$f->pop(); // End of the table

//SepTpl came from modules/imaging/includes/class_form.php
$f->add( new SepTpl());
$defaultValue = (safeCount($profile['ous']) > 0 && $profile['ous'][0] !="") ? ["value"=>"checked"] : [];

// Create a section without table in the form
$f->add(new TitleElement(_T("Manage packages", "kiosk")));

if(xmlrpc_get_conf_kiosk()['enable_acknowledgements'] == true){
    $restricted_area = '<div style="width:100%">
    <h1>'._T("Restricted packages","kiosk").'</h1>
    <ol data-draggable="target" id="restricted-packages">'.$restricted_packages_str.'</ol>
    </div>';
}
else{
    $restricted_area = '';

    $allowed_packages_str .= $restricted_packages_str;
}

$f->add(new SpanElement('<div style="display:inline-flex; width:100%" id="packages">
        <!-- Source : https://www.sitepoint.com/accessible-drag-drop/ -->
        <div style="width:100%">
            <h1>'._T("Available packages","kiosk").'</h1>
            <ol data-draggable="target" id="available-packages">'.$available_packages_str.'</ol>
        </div>'.$restricted_area.'<div style="width:100%">
            <h1>'._T("Allowed packages","kiosk").'</h1>
            <ol data-draggable="target" id="allowed-packages">'.$allowed_packages_str.'</ol>
        </div>
    </div>',"packages"));

$sources = ["ou", "group", "entity"];
if(xmlrpc_get_conf_kiosk()['use_external_ldap'] == true){
    $sources[] ='ldap';
}
$select = new SelectItemtitle("source","Source provider");
$select->setElements($sources);
$select->setElementsVal($sources);
$f->add(
    new TrFormElement(_T('Source','kiosk').":", $select),
    array("value" => (!empty($profile['source'])) ? $profile['source'] : "1")
);

$f->add(new HiddenTpl("jsonDatas"), array("value" => "", "hide" => True));

$f->add(
    new TrFormElement("", new CheckBoxTpl("no_ou")), $defaultValue
);
// -------
// Add the OUs tree
// -------
$result = "";
$number = 0;
recursiveArrayToList(xmlrpc_get_ou_list(), $result, $number);

$f->add(new TrFormElement(_T("Select OUs",'kiosk'),new SpanElement('<div id="ou-container" style="display:flex; max-height:350px;">
<input type="button" id="treeToggler" value="+" />
<div id="jstree" role="tree" style="width:40%;overflow:scroll;">'.$result.'</div>
<div id="users" class="user-list" style="display:inline"></div>
</div>',"kiosk")));

$bo = new ValidateButtonTpl('bvalid', _T("modify",'kiosk'),'btnPrimary',_T("Modify the profile", "kiosk"));
//$rr = new TrFormElementcollapse($bo);
$bo->setstyle("text-align: center;");
$f->add($bo);

$f->pop(); // end of form

$f->display(); // display the form
?>


<script src="modules/kiosk/graph/js/packages.js">
    // Manage drag&drop for the packages boxes
    // Generate a json with the packages
</script>
<script src="modules/kiosk/graph/js/tree.js"></script>
<script src="modules/kiosk/graph/js/validate.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.12.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/jstree.min.js"></script>
