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
 * entitiesManagement.php
 */

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
$p = new PageGenerator(_T("Entities Management", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

$profilelistinfo=xmlrpc_get_CONNECT_API();
if ($_SESSION['login'] == 'root') {
/*
$params = ["source" => "xmppmaster"];

$ajaxmajor = new AjaxFilter(urlStrRedirect("admin/admin/ajax_entity_organisation_admin"),
                            "container-ajax_entity_organisation_admin", $params, 'root_organisation');
$ajaxmajor->display();
$ajaxmajor->displayDivToUpdate();
*/

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
                // on verify les password

                // Création de profil organisation
                $create_entitytag = ($create_entitytag != "" ? $create_entitytag : "");
                $realname = (isset($realname) ? $realname : "");
                $firstname = (isset($firstname) ? $firstname : "");

                $resul = xmlrpc_create_organization(
                    $create_profil_entity_id,
                    $create_organization,
                    $create_userlogin,
                    $create_userpassword,
                    $create_profil,
                    $create_entitytag,
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
}

$f->add(new HiddenTpl("profil_entity_id"),
        array("value" => $profilelistinfo['get_user_info']['profil_entity_id'], "hide" => true));

$f->add(new HiddenTpl("profil_name"),
        array("value" => $profilelistinfo['get_user_info']['profil_name'], "hide" => true));

$f->add(new HiddenTpl("profil_id"),
        array("value" => $profilelistinfo['get_user_info']['profil_id'], "hide" => true));

$f->add(new HiddenTpl("profil_entity_id"),
        array("value" => $profilelistinfo['get_user_info']['profil_entity_id'], "hide" => true));
$f->add(new HiddenTpl("profil_entity_name"),
        array("value" => $profilelistinfo['get_user_info']['profil_entity_name'], "hide" => true));


$profileSelect = new SelectItem("profil");
$profileSelect->setElements($name_profile);
$profileSelect->setElementsVal($id_profile);
$profileSelect->setSelected("3");
$f->push(new Table());
$f->add(
    new TrFormElement(_T("User Profile", "admin"), $profileSelect)
);


 $organization_name_creation = array(
        new InputTpl('organization'),
        new TextTpl(sprintf('<i style="color: #999999">%s</i>', _T('Head Organization', 'admin')))
    );



 $organization_tag_entity = array(
        new InputTpl('entitytag'),
        new TextTpl(sprintf('<i style="color: #999999">%s</i>', _T('Tag Entity Organization', 'admin')))
    );

 $organization_user_entity_profile = array(
        new InputTpl('userlogin'),
        new TextTpl(sprintf('<i style="color: #999999">%s</i>', _T('Organization\'s User', 'admin')))
    );

 $organization_user_password = array(
        new PasswordTpl('userpassword'),
        new TextTpl(sprintf('<i style="color: #999999">%s</i>', _T('Organization\'s password user', 'admin')))
    );

 $organization_user_passwordconfirm = array(
        new PasswordTpl('userpasswordconfirm'),
        new TextTpl(sprintf('<i style="color: #999999">%s</i>', _T('Organization\'s password user confirm', 'admin')))
    );

 $f->add(
        new TrFormElement(
            _T('organization', 'admin'),
            new multifieldTpl($organization_name_creation)
        ),
        "organizationSection"
    );

 $f->add(
        new TrFormElement(
            _T('Tag Entity', 'admin'),
            new multifieldTpl($organization_tag_entity)
        ),
        "entitytagSection"
    );
 $f->add(
        new TrFormElement(
            _T('user', 'admin'),
            new multifieldTpl($organization_user_entity_profile)
        ),
        "userprofilentitySection"
    );

 $f->add(
        new TrFormElement(
            _T('password', 'admin'),
            new multifieldTpl($organization_user_password)
        ),
        "passwordSection"
    );

  $f->add(
        new TrFormElement(
            _T('password confirm', 'admin'),
            new multifieldTpl($organization_user_passwordconfirm)
        ),
        "passwordconfirmSection"
    );


$f->addButton("bcreate", _T("Create new Organization", "admin"));

$f->pop();
$f->display();
}

$params = ["source" => "xmppmaster"];


$ajaxmajor = new AjaxFilter(urlStrRedirect("admin/admin/ajax_entity_user_user"),
                            "container-ajax_entity_user_user", $params, 'entity_user_user');
$ajaxmajor->display();
$ajaxmajor->displayDivToUpdate();

$ajaxmajor = new AjaxFilter(urlStrRedirect("admin/admin/ajax_entity_user_admin"),
                            "container-ajax_entity_user_admin", $params, 'entity_user_admin');
$ajaxmajor->display();
$ajaxmajor->displayDivToUpdate();


?>

