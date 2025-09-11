<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://siveo.net
 *
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once('modules/glpi/includes/xmlrpc.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');
require("modules/medulla_server/includes/profiles_xmlrpc.inc.php");
require_once("modules/medulla_server/includes/utilities.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$start = 0;
if (isset($_GET["start"])) {
    $start = $_GET['start'];
}

if(isset($_GET['type'])) {
    $is_gp = $_GET['type'];
} else {
    $is_gp = 0;
}

$params = array('min'=>$start, 'max'=>$start + $maxperpage, 'filter'=>$_GET["filter"]);

if (isset($_GET['favourite'])) {
    $params['canShow'] = true;
    $params['localSidebar'] = true;
}

if ($is_gp == 1) { # Profile
    $list = getAllProfiles($params);
    $count = countAllProfiles($params);
} else {
    $list = getAllGroups($params);
    $count = countAllGroups($params);

    $ownerlist = [];
    // on recuperer les id des possedeurs du groupes
    foreach ($list as $group) {
        if (isset($group->owner_login) && !in_array($group->owner_login, $ownerlist, true)) {
            $ownerlist[] = $group->owner_login;
        }
    }
$entitiesByUser = getLocationsForUsersName($ownerlist);
}
$filter = $_GET["filter"];

$ids  = array();
$name = array();
$type = array();
$show = array();
$owner = array();

$actionxmppquickdeploy = array();
$action_delete = array();
$array_action_owner = array(); // on veut display le group avec le droit du posseseur de group

if ($is_gp != 1) { // Simple Group
    $delete = new ActionPopupItem(_T("Delete this group", 'dyngroup'), "delete_group", "delete", "id", "base", "computers");
} else { // Imaging group
    $delete = new ActionPopupItem(_T("Delete this imaging group", 'dyngroup'), "delete_group", "delete", "id", "imaging", "manage");
}

if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    $DeployQuickxmpp = new ActionPopupItem(_("Quick action"), "deployquickgroup", "quick", "computer", "xmppmaster", "xmppmaster");
    $DeployQuickxmpp->setWidth(600);
}

/**
 * Création d'une action "Display this group's content as the owner"
 * -----------------------------------------------------------------
 * @param string $desc        Description de l'action (affichée en tooltip)
 * @param string $action      Nom de l'action appelée dans l'URL (ici "display")
 * @param string $classCss    Classe CSS pour le <li> du lien (ex: "displaygroup")
 * @param string $paramString Nom du paramètre GET principal qui sera ajouté à l'URL (ici "login")
 * @param string $module      Module de l'application (ici "base")
 * @param string $submod      Sous-module de l'application (ici "computers")
 * @param string $tab         (optionnel) Nom de l'onglet, ajouté dans l'URL si non null
 * @param mixed  $mod         (optionnel) Indicateur de contexte "mod", ajouté par défaut si présent
 * @param array  $staticParams (optionnel) Tableau clé/valeur de paramètres GET statiques,
 *                             toujours ajoutés dans l'URL en plus du paramètre principal
 *
 * Exemple :
 *   - Ici on définit "login=root" comme paramètre principal (avec display())
 *   - On ajoute aussi des paramètres fixes : "restreint=1&entity=1"
 */
$action_display_group_owner = new ActionItem(
    _T("Display this group's content as the owner", 'dyngroup'),
    "display",       // action
    "displaygroup",  // classe CSS
    "login",         // paramètre GET principal
    "base",          // module
    "computers",     // sous-module
    null,            // pas d'onglet
    false,           // pas de mod
    array(           // paramètres GET statiques ajoutés systématiquement
        'restreint' => 1,
        'entity'    => 1
    )
);


$empty = new EmptyActionItem();
foreach ($list as $group) {
    // Nettoyage des infos propriétaire
    $owneruser   = clean_xss($group->owner_login ?? '');
    $owneruserid = clean_xss($group->owner_id ?? '');
    $owner[]     = $owneruser; // stocke le propriétaire

    // Prépare les infos de base du groupe
    $groupData = [
        "id"       => clean_xss($group->id),
        "gid"      => clean_xss($group->id),
        "groupname"=> clean_xss($group->name),
        "type"     => clean_xss($is_gp),
        "owner"    => $owneruser,
        "idowner"  => $owneruserid,
        "exist"    => clean_xss($group->exists ?? 0),
        "is_owner" => clean_xss($group->is_owner ?? 0)
    ];

    // ✅ Ajout des infos entité si disponibles
    if (!empty($owneruser) && isset($entitiesByUser[$owneruser][0])) {
        $entityInfo = $entitiesByUser[$owneruser][0];

        $groupData['entity_id']            = clean_xss($entityInfo['entity_id']);
        $groupData['entity_name']          = clean_xss($entityInfo['entity_name']);
        $groupData['entity_completename'] = $entityInfo['entity_completename'];
        $groupData['profile']              = clean_xss($entityInfo['profile']);
        $groupData['is_recursive']         = clean_xss($entityInfo['is_recursive']);
        $groupData['is_dynamic']           = clean_xss($entityInfo['is_dynamic']);
        $groupData['login']           = "root";
    }

    // Cas particulier : groupe particulier avec profil "gp"
    if ($is_gp == 1) {
        $profile = xmlrpc_getProfileLocation($group->id);
        $groupData['profile'] = clean_xss($profile);
    }

    // Ajoute dans la liste finale
    $ids[] = $groupData;

    // Stockage des autres infos pour affichage
    $name[] = clean_xss($group->getName());

    // Type dynamique ou statique
    if ($group->isDyn()) {
        $type[] = (!$group->isRequest()
            ? sprintf(_T('result (%s)', 'dyngroup'), $group->countResult())
            : _T('query', 'dyngroup'));
    } else {
        $type[] = _T('static group', 'dyngroup');
    }

    // Affichable ?
    $show[] = ($group->canShow() ? _T('Yes', 'dyngroup') : _T('No', 'dyngroup'));

    // Suppression possible ?
    if ($groupData['is_owner'] == 1 || $_SESSION['login'] == "root") {
        $action_delete[] = $delete;
    } else {
        $action_delete[] = $empty;
    }

    // Action propriétaire uniquement si root
    if ($_SESSION['login'] == "root") {
        $array_action_owner[] = ($_SESSION['login'] != $owneruser ? $action_display_group_owner : $empty);
    }

    // Déploiement rapide XMPP
    if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        $actionxmppquickdeploy[] = $DeployQuickxmpp;
    }
}


// Avoiding the CSS selector (tr id) to start with a number
$ids_grp = [];
foreach($ids as $index => $gid_grp) {
    $ids_grp[] = 'g_'.$gid_grp['groupname'];
}

if ($is_gp != 1) { // Simple Group
    $n = new OptimizedListInfos($name, _T('Group name', 'dyngroup'));
} else { // Imaging group
    $n = new OptimizedListInfos($name, _T('Group name', 'dyngroup'));
}
$n->setcssIds($ids_grp);
$n->setTableHeaderPadding(0);
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->start = 0;
$n->end = $conf["global"]["maxperpage"];

if ($_SESSION['login'] == "root") {
        $n->addExtraInfo($owner, _T('Owner', 'dyngroup'));
}
if ($is_gp != 1) { // Simple group
    $n->addExtraInfo($type, _T('Type', 'dyngroup'));
}
$n->addExtraInfo($show, _T('Favourite', 'dyngroup'));
$n->setParamInfo($ids);


if ($_SESSION['login'] == "root") {
        $n->addActionItemArray($array_action_owner);
}



if ($is_gp != 1) { // Simple group
    $n->addActionItem(new ActionItem(_T("Display1 this group's content", 'dyngroup'), "display", "displaygroup", "id", "base", "computers"));
    if (in_array("inventory", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Inventory on this group", "dyngroup"), "groupinvtabs", "inventory", "inventory", "base", "computers"));
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this group", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $n->addActionItem(new ActionItem(_T("Edit this group", 'dyngroup'), "computersgroupedit", "edit", "id", "base", "computers"));
    $n->addActionItem(new ActionItem(_T("Share this group", 'dyngroup'), "edit_share", "groupshare", "id", "base", "computers"));

    if (in_array("msc", $_SESSION["supportModList"])) {
        if (!in_array("xmppmaster", $_SESSION["supportModList"])) {
            $n->addActionItem(new ActionItem(_T("Read log", "dyngroup"), "groupmsctabs", "logfile", "computer", "base", "computers", "grouptablogs"));
        }
        $n->addActionItem(new ActionItem(_T("Software deployment on this group", "dyngroup"), "groupmsctabs", "install", "computer", "base", "computers"));
    }
    if (in_array("update", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Update on this group", "dyngroup"), "view_updates", "reload", "id", "base", "computers"));
    }
    $n->addActionItem(new ActionItem(_("Updates compliance by machines"), "detailsByMachines", "auditbymachine", "updates", "updates", "updates"));
    //$n->addActionItem(new ActionItem(_("Deploy all update on this group"),"deployAllUpdates", "updateall","updates", "updates", "updates") );
    $n->addActionItem(new ActionItem(_("Deploy specific update on this group"), "deploySpecificUpdate", "updateone", "updates", "updates", "updates"));
} else { // Imaging group
    $n->addActionItem(new ActionItem(_T("Display this imaging group's content", 'dyngroup'), "display", "displaygroup", "id", "imaging", "manage"));


    if (in_array("inventory", $_SESSION["supportModList"])) {
        $n->addActionItem(new ActionItem(_T("Inventory on this imaging group", "dyngroup"), "groupinvtabs", "inventory", "inventory", "imaging", "manage"));
    } else {
        # TODO implement the glpi inventory on groups
        #    $n->addActionItem(new ActionItem(_T("Inventory on this profile", "dyngroup"),"groupglpitabs","inventory","inventory", "base", "computers"));
    }
    $n->addActionItem(new ActionItem(_T("Edit this imaging group", 'dyngroup'), "computersgroupedit", "edit", "id", "imaging", "manage"));
    $n->addActionItem(new ActionItem(_T("Share this imaging group", 'dyngroup'), "edit_share", "groupshare", "id", "imaging", "manage"));
    if (in_array("msc", $_SESSION["supportModList"])) {
        if (!in_array("xmppmaster", $_SESSION["supportModList"])) {
            $n->addActionItem(new ActionItem(_T("Read log", "dyngroup"), "groupmsctabs", "logfile", "computer", "imaging", "manage", "grouptablogs"));
        }
        $n->addActionItem(new ActionItem(_T("Software deployment on this imaging group", "dyngroup"), "groupmsctabs", "install", "computer", "imaging", "manage"));
    }
    if (in_array("imaging", $_SESSION["supportModList"])) {
        if (xmlrpc_isImagingInProfilePossible()) {
            $n->addActionItem(new ActionItem(_("Imaging management"), "groupimgtabs", "imaging", "computer", "imaging", "manage"));
        }
    }
    $n->addActionItem(new ActionItem(_("Updates compliance by machines"), "detailsByMachines", "auditbymachine", "updates", "updates", "updates"));
}


if (in_array("xmppmaster", $_SESSION["supportModList"])) {
    // quick action for group with xmppmodule
    $n->addActionItemArray($actionxmppquickdeploy);
}


$n->addActionItemArray($action_delete);

$n->addActionItem(new ActionItem(_T("Csv export", "dyngroup"), "csv", "csv", "computer", "base", "computers"));
//$n->disableFirstColumnActionLink();

$n->display();
