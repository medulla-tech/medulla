<?php
/**
 * (c) 2018-2023 Siveo, http://siveo.net
 * $Id$
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

// Need the user sharing groups
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
?>

<style type="text/css">
    @import url(modules/kiosk/graph/style.min.css);

    #availableFilter, #allowedFilter {
        width: 80%;
        margin-bottom: 2px;
    }
</style>

<?php $p = new PageGenerator(_T("Add New Profile", 'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$ou = $_POST['ou'];
$owner = (!empty($_POST['owner'])) ? htmlentities($_POST['owner']) : $_SESSION['login'];

$ou_list = xmlrpc_get_ou_list($ou, $owner);

if(is_array($ou_list)) {
    $f = new ValidatingForm(array("id" => "profile-form"));

    $f->push(new Table());

    $f->add(new HiddenTpl("action"), array("value" => $_GET['action'], "hide" => true));
    $f->add(new HiddenTpl("owner"), array("value" => $_SESSION['login'], "hide" => true));
    $f->add(new SpanElement('', "packages"));

    // -------
    // Add an input for the profile name
    // -------
    $f->add(
        //InputTplTitle came from modules/imaging/includes/class_form.php
        new TrFormElement(_T('Profile Name', 'kiosk').":", new InputTplTitle('name', _T('Profile Name', 'kiosk'))),
        array("value" => "", 'placeholder' => _T('Name', 'kiosk'), "required" => true)
    );

    // -------
    // Add a selector to activate / desactivate the profile
    // -------
    $profileStatus = new SelectItemtitle("status", _T("Set the profile to active / inactive state", "kiosk"));
    $profileStatus->setElements([_T('Active', "kiosk"), _T('Inactive', 'kiosk')]);
    $profileStatus->setElementsVal([1,0]);
    $f->add(
        new TrFormElement(_T('Profile Status', 'kiosk').":", $profileStatus),
        array("value" => "1","required" => true)
    );

    $f->pop(); // End of the table
    //SepTpl came from modules/imaging/includes/class_form.php
    $f->add(new SepTpl());
    // Create a section without table in the form
    $f->add(new TitleElement(_T("Manage packages", "kiosk")));
    // Get the list of the packages
    $available_packages = [];
    $available_packages_str = "";

    $row = 0;
    foreach($packages['datas']['uuid'] as $package) {
        $available_packages[$packages['datas']['name'][$row]] = $package;
        $available_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';
        $row++;
    }

    $restricted_area = (xmlrpc_get_conf_kiosk()['enable_acknowledgements'] == true) ? '<div style="width:100%">
            <h1>'._T("Restricted packages", "kiosk").'</h1>
            <ol data-draggable="target" id="restricted-packages">
            </ol>
        </div>' : '';

    $f->add(new SpanElement('<div style="display:inline-flex; width:100%" id="packages">
        <!-- Source : https://www.sitepoint.com/accessible-drag-drop/ -->
        <div style="width:100%">
            <h1>'._T("Available packages", "kiosk").'</h1>
            <input type="text" id="availableFilter" value="" placeholder="'._T("Search by name ...", "pkgs").'"><br/>
            <ol data-draggable="target" id="available-packages">'.$available_packages_str.'</ol>
        </div>'.$restricted_area.'<div style="width:100%">
            <h1>'._T("Allowed packages", "kiosk").'</h1>
            <input type="text" id="allowedFilter" value="" placeholder="'._T("Search by name ...", "pkgs").'"><br/>
            <ol data-draggable="target" id="allowed-packages">
            </ol>
        </div>
    </div>', "packages"));

    $sources = ["Entity", "Group", "LDAP", "Ou User", "Ou Machine"];
    if(xmlrpc_get_conf_kiosk()['use_external_ldap'] == true) {
        $sources[] = 'ldap';
    }
    $select = new SelectItemtitle("source", "Source provider");
    $select->setElements($sources);
    $select->setElementsVal($sources);
    $f->add(
        new TrFormElement(_T('Source', 'kiosk').": ", $select),
        array("value" => (!empty($profile['source'])) ? $profile['source'] : "1")
    );

    // -------
    // Add the OUs tree
    // -------
    $result = "";
    $f->add(new SpanElement(
        '
    <div id="source-container" class="user-list" style="display:inline"></div>
        <div id="ou-container" style="display:flex; max-height:350px;">
            <br>
            <input type="button" id="treeToggler" value="+" />
            <div id="jstree" role="tree" style="width:40%;overflow:scroll;">'.$result.'</div>
            <div id="users" class="user-list" style="display:inline"></div>
        </div>',
        "kiosk"
    ));

    $f->add(new HiddenTpl("jsonDatas"), array("value" => "", "hide" => true));

    $bo = new ValidateButtonTpl('bvalid', _T("Create the profile", 'kiosk'), 'btnSecondary');
    //$rr = new TrFormElementcollapse($bo);
    $bo->setstyle("text-align: center;");
    $f->add($bo);

    $f->pop(); // end of form

    $f->display(); // display the form
} else {
    echo _T("The LDAP is not configured correctly. Please check your configuration.");
}
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
