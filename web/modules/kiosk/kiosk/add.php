<?php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
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

<link rel="stylesheet" href="modules/kiosk/graph/css/kiosk.css" />
<link rel="stylesheet" href="jsframework/lib/pluginjqueryjtree/themes/default/style.min.css" />

<?php $p = new PageGenerator(_T("Add New Profile", 'kiosk'));
$p->setSideMenu($sidemenu);
$p->display();

$ou = (isset($_POST['ou'])) ? $_POST['ou'] : "";
$owner = (!empty($_POST['owner'])) ? htmlentities($_POST['owner']) : $_SESSION['login'];

$ou_list = xmlrpc_get_ou_list($ou, $owner, $_SESSION['glpi_user']['api_token']);

if(is_array($ou_list)) {
    $f = new ValidatingForm(array("id" => "profile-form"));

    $f->add(new HiddenTpl("action"), array("value" => $_GET['action'], "hide" => true));
    $f->add(new HiddenTpl("owner"), array("value" => $_SESSION['login'], "hide" => true));
    $f->add(new SpanElement('', "packages"));

    // Section title for profile information
    $f->add(new SpanElement(_T("Profile information", "kiosk"), "section-title"));

    $f->push(new Table());

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

    // Section title for package management
    $f->add(new SpanElement(_T("Manage packages", "kiosk"), "section-title"));
    // Get the list of the packages
    $available_packages = [];
    $available_packages_str = "";

    $row = 0;
    foreach($packages['datas']['uuid'] as $package) {
        if ($packages['datas']['associateinventory'][$row] == 1) {
            $available_packages[$packages['datas']['name'][$row]] = $package;
            $available_packages_str .= '<li data-draggable="item" data-uuid="'.$package.'">'.$packages['datas']['name'][$row].'</li>';
        }
        $row++;
    }

    $restricted_area = (xmlrpc_get_conf_kiosk()['enable_acknowledgements'] == true) ? '<div>
            <h3>'._T("Restricted packages", "kiosk").'</h3>
            <ol data-draggable="target" id="restricted-packages">
            </ol>
        </div>' : '';

    $f->add(new SpanElement('<div id="packages">
        <div>
            <h3>'._T("Available packages", "kiosk").'</h3>
            <input type="text" id="availableFilter" value="" placeholder="'._T("Search by name ...", "pkgs").'">
            <ol data-draggable="target" id="available-packages">'.$available_packages_str.'</ol>
        </div>'.$restricted_area.'<div>
            <h3>'._T("Allowed packages", "kiosk").'</h3>
            <input type="text" id="allowedFilter" value="" placeholder="'._T("Search by name ...", "pkgs").'">
            <ol data-draggable="target" id="allowed-packages">
            </ol>
        </div>
    </div>', "packages"));

    // Section title for source selection
    $f->add(new SpanElement(_T("Source selection", "kiosk"), "section-title"));

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
        '<div id="source-container"></div>
        <div id="ou-container">
            <input type="button" id="treeToggler" value="+" />
            <div id="jstree" role="tree">'.$result.'</div>
            <div id="users"></div>
        </div>',
        "kiosk"
    ));

    $f->add(new HiddenTpl("jsonDatas"), array("value" => "", "hide" => true));

    $bo = new ValidateButtonTpl('bvalid', _T("Create", 'kiosk'), 'btnPrimary', _T("Create the profile", "kiosk"));
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
var MSG_OU_REQUIRED = "<?php echo _T('Please select the concerned OUs'); ?>";
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
