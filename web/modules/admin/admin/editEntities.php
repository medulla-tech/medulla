<?php

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
$title = (isset($_GET['mode']) && $_GET['mode'] === 'edit')
    ? _T("Edit Entities", 'admin')
    : _T("Add Entities", 'admin');
$p = new PageGenerator($title);
$p->setSideMenu($sidemenu);
$p->display();

/* DEBUG */
echo "<pre>";
print_r($_GET);
echo "</pre>";
// exit;


if (isset($_POST["bcreate"])) {
    $MessageFailure = _T("Failed to create the organization: The provided parameters are not valid. Please check the information and try again.", 'admin');

    // on fait verif sur auth_token
    verifyCSRFToken($_POST);

    $parent_entity_id = $_POST['parent_entity_id'];
    $name = $_POST['organization'];

    $token = $_POST['auth_token'];

    $result = xmlrpc_create_entity_under_custom_parent($parent_entity_id, $name);

    if($result) {
        new NotifyWidgetSuccess(_T("The entity " . $name . " was created successfully.", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", array()));
        exit;
    } else {
        new NotifyWidgetFailure(_T("Failed to create the entity " . $name . ".", "admin"));
        header("Location: " . urlStrRedirect("admin/admin/entitiesManagement", array()));
        exit;
    }
}

$f = new ValidatingForm(array('method' => 'POST'));
$f->addValidateButtonWithLabel("bcreate", "Create new Organization");

$id_profile = array();
$name_profile = array();

foreach ($listdefprofil as $profile_id_name) {
    if ($profile_id_name['name'] != "Super-Admin"){
        $id_profile[] = $profile_id_name['id'];
        $name_profile[]=$profile_id_name['name'];
    }
}

$f->push(new Table());
$organization_name_creation = array(
    new InputTpl('organization'),
    new TextTpl(sprintf('<i style="color: #999999">%s</i>', _T('Head Organization', 'admin')))
);

$f->add(
    new TrFormElement(
        _T('Organization', 'admin'),
        new multifieldTpl($organization_name_creation)
    ),
    "organizationSection"
);

$f->add(new HiddenTpl("parent_entity_id"), array("value" => $_GET['entity_id'], "hide" => true));

$f->pop();
$f->display();

?>
