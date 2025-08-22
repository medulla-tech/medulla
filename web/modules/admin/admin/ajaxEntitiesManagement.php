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
 *
 */
require_once("modules/xmppmaster/includes/html.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
?>

<style>
   /* Style CSS pour l'alignement des éléments dans le tableau */
    #container>form>table>thead td:first-child span {
        display: block;
        text-align: left;
        padding-left: 0 !important;
        margin-left: 0 !important;
    }
    #container>form>table>thead td:last-child span {
        display: block;
        text-align: right;
        padding-right: 50px;
    }
</style>

<?php

// Récupération de la configuration globale
global $conf;
$maxperpage = $conf["global"]["maxperpage"];
$maxperpage = 1;
// Récupération des paramètres GET pour le filtrage et la pagination
$filter = (isset($_GET["filter"])) ? htmlentities($_GET["filter"]) : "";
$start = isset($_GET['start'])?$_GET['start']:0;
$end   = (isset($_GET['end'])?$_GET['start']+$maxperpage:$maxperpage);


// Récupération des informations de l'utilisateur connecté via GLPI
$loginglpi = xmlrpc_get_user_by_name($_SESSION['login']);

$facilitylevel = 0; // tout va bien
$profil = !empty($loginglpi['nameprofil']) ? $loginglpi['nameprofil'] : _T("non definie", 'admin');

// Vérification des permissions de l'utilisateur
if (!in_array($loginglpi['nameprofil'], ['Admin', 'Super-Admin']))
{
   $message = sprintf(
    _T("Profile [%s]: you do not have permissions (read-only access)", 'admin'),
    $profil
);
   $facilitylevel = 1;
}
if (empty($loginglpi['api_token'])) {
    $message = sprintf(
        _T("Your account with profile [%s] is not provisioned to consult the entities", 'admin'),
        $profil
    );
    $facilitylevel = 2;
}
// Récupération de la liste des entités accessibles par l'utilisateur
$entitiesList = xmlrpc_get_list_user_token($loginglpi['api_token']);
if (count($entitiesList) == 0) {
    $message = sprintf(
        _T("Your account with profile [%s] has no reference entities.", 'admin'),
        $profil
    );
    $facilitylevel = 3;
}
// Affichage des messages d'erreur ou d'information selon le niveau de permission
if ( $facilitylevel > 0) // message
{
    if ($facilitylevel != 3){
    // Affichage des informations de l'utilisateur si le niveau de permission est 1 ou 2
    $n = new ListInfos(array($loginglpi['nameuser']), _T("User", "admin"));
    $n->addExtraInfo(array($loginglpi['realname']), _T("real name", "admin"));
    $n->addExtraInfo(array($loginglpi['firstname']), _T("first name", "admin"));
    $n->addExtraInfo(array($profil), _T("profil", "admin"));
    $n->addExtraInfo(array($loginglpi['nameentity']), _T("entity", "admin"));
    $n->addExtraInfo(array($loginglpi['nameentitycomplete']), _T("complete_entity", "admin"));
    $n->setNavBar ="frfr";
    $n->start = 0;
    $n->end =1;
    $converter = new ConvertCouleur();
    $n->setCaptionText($message);
    $n->setCssCaption(  $border = 1,
                        $bold = 0,
                        $bgColor = "lightgray",
                        $textColor = "black",
                        $padding = "10px 0",
                        $size = "20",
                        $emboss = 1,
                        $rowColor = $converter->convert("lightgray"));
        $n->disableFirstColumnActionLink();
        $n->display($navbar = 0, $header = 0);
    }else{
        // Affichage d'un message simple si le niveau de permission est 3
        echo'
      <div style="background-color: #ddd; padding: 10px; text-align: center; font-size: 14px;">';
        echo htmlspecialchars($message, ENT_QUOTES, 'UTF-8');
      echo '</div>';
    }
}

// Si le niveau de permission est acceptable (0 ou 1), on affiche la liste des entités
if ( $facilitylevel <= 1)
{
    // Récupération des entités avec leurs informations
    $entitiesListseach = xmlrpc_get_counts_by_entity_root(
        filter: $filter,
        start: $start,
        end: $end,
        entities: $entitiesList
    );
    // Définition des actions possibles sur les entités
    $action_edit = new ActionItem(_("Modifier"), "editEntity", "edit", "", "admin", "admin");
    $action_add = new ActionItem(_("Ajouter"), "editEntity", "add", "", "admin", "admin");
    $action_manageusers = new ActionItem(_("Gérer les utilisateurs"), "listUsersofEntity", "manageusers", "", "admin", "admin");
    $action_download = new ActionItem(_("Télécharger"), "downloadAgent", "download", "", "admin", "admin");
    $action_non_edit = new EmptyActionItem1(_("Modification non autorisée"), "", "editg", "", "admin", "admin");
    $action_non_delete = new EmptyActionItem1(_("Suppression non autorisée"), "", "deleteg", "", "admin", "admin");

    // Initialisation des tableaux pour les actions et les informations
    $editAction = $addAction = $manageusersAction = $downloadAction = $usersCount = $titles = $params = [];
    $entitiesList = $entitiesListseach['data'];

    $count = count($entitiesList['id']); // nombre d'entités
    // Boucle sur les entités pour préparer les données et les actions
    for ($i = 0; $i < $count; $i++) {
        // 'api_token' ne peux pas etre 1 parametre CGI get ou post pour la securite
        // $_SESSION['api_token']=$loginglpi['api_token']
        $params[] = [
            'userIds'    => $entitiesList['userIds'][$i],
            'entityId'   => $entitiesList['id'][$i],
            'entityName' => $entitiesList['name'][$i],
            'nbusers'    => $entitiesList['nb_users'][$i],
            'nbcomputer'    => $entitiesList['nb_machines'][$i],
            'entitycompletename' => $entitiesList['completename'][$i],
            'userId' => $loginglpi['id'],
            'realname' => $loginglpi['realname'],
            'firstname' => $loginglpi['firstname'],
            'is_activeuser'=> $loginglpi['is_activeuser'],
            'locations_id'=> $loginglpi['locations_id'],
            'profiles_id'=> $loginglpi['profiles_id'],
            'users_id_supervisor'=> $loginglpi['users_id_supervisor'],
            'nameprofil'=> $loginglpi['nameprofil'],
            'nameentity'=> $loginglpi['nameentity'],
            'nameentitycomplete'=> $loginglpi['nameentitycomplete'],
        ];

        // Définition des actions en fonction des permissions
        $deleteToAdd = new ActionConfirmItem(
            _("Delete"),
            "deleteEntity",
            "delete",
            "",
            "admin",
            "admin",
            _T("Are you sure you want to delete this entity [" . $entitiesList['name'][$i] . "] ?" , 'admin')
        );
        // Vérification si l'utilisateur est propriétaire de l'entité
        $array_list_user_for_entity = explode(",", $entitiesList['userIds'][$i]);
        if (in_array($loginglpi['id'], $array_list_user_for_entity))
        {
            // Actions limitées si l'utilisateur est propriétaire de l'entité
            $editAction[] = new EmptyActionItem1(_("Modification non autorisée"), "", "editg", "", "admin", "admin");
            $addAction[] = $action_add;
            $manageusersAction[] = $action_manageusers;
            $downloadAction[] = $action_download;
            $deleteAction[] = new EmptyActionItem1(_("Suppression non autorisée"), "", "deleteg", "", "admin", "admin");
        }else
        {
            // Actions complètes si l'utilisateur n'est pas propriétaire de l'entité
            $editAction[] =  $action_edit;
            $addAction[] = $action_add;
            $manageusersAction[] = $action_manageusers;
            $downloadAction[] = $action_download;
            $deleteAction[] = $deleteToAdd;
        }
    }
    // Affichage de la liste des entités avec leurs informations et actions
    $n = new OptimizedListInfos($entitiesList['id'], _T("ID Entity", "admin"));
    $n->addExtraInfo($entitiesList['name'], _T("Name of Entity", "admin"));
    $n->addExtraInfo($entitiesList['completename'], _T("completename Name of Entity", "admin"));
    $n->addExtraInfo($entitiesList['nb_users'], _T("Users", "admin"));
    $n->addExtraInfo($entitiesList['nb_machines'], _T("Computers", "admin"));
    $n->addExtraInfo($entitiesList['userIds'], _T("users attribut", "admin"));

    $n->addActionItemArray($editAction);
    $n->addActionItemArray($addAction);
    $n->addActionItemArray($manageusersAction);
    $n->addActionItemArray($downloadAction);
    $n->addActionItemArray($deleteAction);
    $n->setParamInfo($params);
    $n->start=$start;
    $n->end = $entitiesListseach['total_count'];
    $n->setNavBar(new AjaxNavBar("10", $filter));
    $n->disableFirstColumnActionLink();
    $n->display();
}//  Fin de la condition sur le niveau de permissionend facility
?>

<script>
jQuery(document).ready(function($) {
    // Gestion des clics sur les liens d'édition et d'ajout
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
