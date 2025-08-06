<?php
/*
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
 * ajaxEntitiesManagement.php
 */
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
?>

require_once("modules/admin/includes/xmlrpc.php");

// "Management of Organizational Entities"
echo "modules/admin/admin/ajax_entity_organisation_admin.php";
$profilelistinfo=xmlrpc_get_CONNECT_API();
// echo "<pre>";
// print_r($_GET);
// echo "</pre>";
// echo "<br>";
// echo "<pre>";
// print_r($_POST);
// echo "</pre>";
// echo "<br>";
// echo "<pre>";
// print_r($profilelistinfo);
// echo "</pre>";



$listdefprofil = $profilelistinfo['get_list_profiles'];
$infodefprofil = $profilelistinfo['get_user_info'];

$MessageFailure = _T("Failed to create the organization: The provided parameters are not valid. Please check the information and try again.", 'admin');

if (isset($_POST["bcreate"])) {
    verifyCSRFToken($_POST); // on fait verif sur auth_token
    // on verifie si on a des variables de bien definie $POST
    // !!! attention si parametre ajouter dans formulaire ils faut ajouter dans la list suivante "$required_keys"

    $required_keys = [  'old_profil',
                        'profil',
                        'profil_id',
                        'organization',
                        'auth_token',
                        'bcreate',
                        'entitytag',
                        'profil_entity_id',
                        'profil_name',
                        'profil_entity_name',
                        'userlogin',
                        'userpassword',
                        'userpasswordconfirm'];

    // print_r(array_diff($required_keys, array_keys($_POST)));

    if (!empty(array_diff($required_keys, array_keys($_POST)))) {

        // on ne peut pas creer
        new NotifyWidgetFailure($MessageFailure);
        header("Location: " . urlStrRedirect("admin/admin/manage_entity_organisation", array()));
        exit;
    } else {
        // on recupere les variables de post
        extract($_POST, EXTR_PREFIX_ALL, 'create');
        if ($create_profil_entity_id == "" ||
            $create_organization == "" ||
             $create_userlogin == "" ||
             $create_profil_id == "" ||
             $create_entitytag == "" ||
             $create_userpassword == "" ||
             $create_userpasswordconfirm == ""||
             $create_profil == ""){
                new NotifyWidgetFailure($MessageFailure);
                header("Location: " . urlStrRedirect("admin/admin/manage_entity_organisation", array()));
                exit;
            }else
            {
                // Création de profil organisation
                $tag_value = ($create_entitytag != "" ? $create_entitytag : "");
                $realname = (isset($realname) ? $realname : "");
                $firstname = (isset($firstname) ? $firstname : "");

                $resul = xmlrpc_create_organization(
                    $create_profil_entity_id,
                    $create_organization,
                    $create_userlogin,
                    $create_userpassword,
                    $create_profil,
                    $tag_value,
                    $realname,
                    $firstname
                );

                if (is_array($resul) && count($resul) === 3) {
                    // on cree l'entitee organization
                    $MessageTemplate = _T("The organization [%s] %s has been successfully created. pour user %s [%s] avec le profil %s",
                                          'admin');
                    $MessageSuccess = sprintf($MessageTemplate,
                                            $resul[0],
                                            $create_organization,
                                            $resul[1],
                                            $create_userlogin,
                                            $resul[2]);
                    new NotifyWidgetSuccess($MessageSuccess);
                    header("Location: " . urlStrRedirect("admin/admin/manage_entity_organisation", array()));
                    exit;
                } else {
                    $MessageTemplate = _T("The organization %s could not be created for user %s with profile %s", 'admin');
                    $MessageFailure = sprintf($MessageTemplate, $create_organization, $create_userlogin, $create_profil_id);
                    new NotifyWidgetFailure($MessageFailure);
                    header("Location: " . urlStrRedirect("admin/admin/manage_entity_organisation", array()));
                    exit;
                }
            }
    }
}
$f = new ValidatingForm(array("action" => urlStrRedirect("admin/admin/ajax_entity_organisation_admin"),));

$id_profile = array();
$name_profile = array();

foreach ($listdefprofil as $profile_id_name) {
    if ($profile_id_name['name'] != "Super-Admin"){


        $id_profile[] = $profile_id_name['id'];
        $name_profile[]=$profile_id_name['name'];
    }
</style>

<?php
// Recovers its entity and children and small children ...
$myEntitiesTree = xmlrpc_get_list("entities", True);

$types = [
    "École",
    "Entreprise",
    "Collectivité"
];

$usersCount = [
    "5 utilisateurs",
    "12 utilisateurs",
    "3 utilisateurs"
];

$created = [
    "2024-01-15",
    "2023-11-03",
    "2025-02-28"
];

$edit = new ActionItem(_("Edit"), "editEntities", "edit", "", "admin", "admin");
$add = new ActionItem(_("Add"), "editEntities", "add", "", "admin", "admin");
$view = new ActionItem(_("View"), "manageentity", "display", "", "admin", "admin");
$download = new ActionItem(_("Download"), "manageentity", "down", "", "admin", "admin");

$params = [];

// sort entities by increasing id
usort($myEntitiesTree['myentities'], function($a, $b) {
    return $a['id'] <=> $b['id'];
});

foreach ($myEntitiesTree['myentities'] as $entity) {
    $editAction[] = $edit;
    $addAction[] = $add;
    $viewAction[] = $view;
    $downloadAction[] = $download;

    $titles[] = $entity['name'];
    $params[] = [
        'entity_id' => $entity['id'],
        'entity_name' => $entity['name'],
    ];
}

$f->add(new HiddenTpl("profil_entity_id"),
        array("value" => $profilelistinfo['get_user_info']['profil_entity_id'], "hide" => true));

$f->add(new HiddenTpl("profil_name"),
        array("value" => $profilelistinfo['get_user_info']['profil_name'], "hide" => true));

$f->add(new HiddenTpl("profil_id"),
        array("value" => $profilelistinfo['get_user_info']['profil_id'], "hide" => true));

$n->addActionItemArray($editAction);
$n->addActionItemArray($addAction);
$n->addActionItemArray($viewAction);
$n->addActionItemArray($downloadAction);
$n->setParamInfo($params);
$n->display();
?>
<script>
jQuery(document).ready(function($) {
    $('li.edit a, li.add a').on('click', function(e) {
        const $link = $(this);
        let href = $link.attr('href');

        if (href.includes('mode=')) return;

        let mode = '';
        if ($link.closest('li').hasClass('edit')) {
            mode = 'edit';
        } else if ($link.closest('li').hasClass('add')) {
            mode = 'add';
        }

        const separator = href.includes('?') ? '&' : '?';
        href += separator + 'mode=' + mode;

        window.location.href = href;
        e.preventDefault();
    });
});
</script>
