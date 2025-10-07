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
 * file ajaxEntitiesManagement.php
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
$u = isset($_SESSION['glpi_user']) && is_array($_SESSION['glpi_user']) ? $_SESSION['glpi_user'] : [];

if (empty($u)) {
    echo '<div style="background:#fce4e4;color:#900;padding:10px;text-align:center">'
       . htmlspecialchars(_T("No GLPI session found. Please sign in again.", "admin"), ENT_QUOTES, 'UTF-8')
       . '</div>';
    return;
}

global $conf;
$maxperpage = isset($conf["global"]["maxperpage"]) ? (int)$conf["global"]["maxperpage"] : 10;
$maxperpage = 1;

$filter = isset($_GET["filter"]) ? htmlentities($_GET["filter"]) : "";
$start  = isset($_GET['start']) ? (int)$_GET['start'] : 0;
$end    = isset($_GET['end']) ? (int)$_GET['start'] + $maxperpage : $maxperpage;

$facilitylevel = 0;
$profil = !empty($u['profile_name']) ? $u['profile_name'] : _T("Not defined", 'admin');

if (empty($u['api_token'])) {
    $message = sprintf(
        _T("Your account with profile [%s] is not provisioned to consult the entities", 'admin'),
        $profil
    );
    $facilitylevel = 2;
}

$entitiesList = [];
if (!empty($u['api_token'])) {
    $entitiesList = xmlrpc_get_list_user_token($u['api_token']);
}

if (is_array($entitiesList) && count($entitiesList) === 0) {
    $message = sprintf(
        _T("Your account with profile [%s] has no reference entities.", 'admin'),
        $profil
    );
    $facilitylevel = 3;
}

if ($facilitylevel > 0) {
    if ($facilitylevel != 3) {
        $n = new ListInfos(array(!empty($u['email']) ? $u['email'] : $u['login']), _T("User", "admin"));
        $n->addExtraInfo(array(isset($u['lastname']) ? $u['lastname'] : ''), _T("real name", "admin"));                 // map -> realname
        $n->addExtraInfo(array(isset($u['firstname']) ? $u['firstname'] : ''), _T("first name", "admin"));
        $n->addExtraInfo(array($profil), _T("profil", "admin"));
        $n->addExtraInfo(array(isset($u['entity']) ? $u['entity'] : ''), _T("entity", "admin"));
        $n->addExtraInfo(array(isset($u['entity_path']) ? $u['entity_path'] : ''), _T("complete_entity", "admin"));
        $n->start = 0;
        $n->end = 1;
        $converter = new ConvertCouleur();
        $n->setCaptionText($message);
        $n->setCssCaption(
            $border = 1,
            $bold = 0,
            $bgColor = "lightgray",
            $textColor = "black",
            $padding = "10px 0",
            $size = "20",
            $emboss = 1,
            $rowColor = $converter->convert("lightgray")
        );
        $n->disableFirstColumnActionLink();
        $n->display($navbar = 0, $header = 0);
    } else {
        echo '<div style="background-color:#ddd;padding:10px;text-align:center;font-size:14px;">'
           . htmlspecialchars($message, ENT_QUOTES, 'UTF-8')
           . '</div>';
    }
}

if ($facilitylevel <= 1) {
    // Paginated search + filtered of accessible root entities
    $entitiesListseach = xmlrpc_get_counts_by_entity_root(
        filter: $filter,
        start:  $start,
        end:    $end,
        entities: $entitiesList
    );

    //Actions
    $action_edit         = new ActionItem(_("Modify"), "editEntity", "edit", "", "admin", "admin");
    $action_add          = new ActionItem(_("Add"), "editEntity", "add", "", "admin", "admin");
    $action_manageusers  = new ActionItem(_("Manage users"), "listUsersofEntity", "manageusers", "", "admin", "admin");
    $action_download     = new ActionItem(_("Download"), "downloadAgent", "download", "", "admin", "admin");
    $action_non_edit     = new EmptyActionItem1(_("Unauthorized modification"), "", "editg", "", "admin", "admin");
    $action_non_delete   = new EmptyActionItem1(_("Unauthorized modification"), "", "deleteg", "", "admin", "admin");

    $editAction = $addAction = $manageusersAction = $downloadAction = $deleteAction = $params = [];
    $data = $entitiesListseach['data'];

    $count = isset($data['id']) ? count($data['id']) : 0;

    for ($i = 0; $i < $count; $i++) {
        $params[] = [
            'userIds'              => $data['userIds'][$i],
            'entityId'             => $data['id'][$i],
            'entityName'           => $data['name'][$i],
            'nbusers'              => $data['nb_users'][$i],
            'nbcomputer'           => $data['nb_machines'][$i],
            'entitycompletename'   => $data['completename'][$i],
            'tag'                  => $data['tag'][$i],

            // ---- mapping from the session ----
            'userId'               => (int)$u['id'],
            'realname'             => isset($u['lastname']) ? $u['lastname'] : null,            // ex- realname
            'firstname'            => isset($u['firstname']) ? $u['firstname'] : null,
            'is_activeuser'        => isset($u['active']) ? (int)$u['active'] : null,
            'locations_id'         => isset($u['location_id']) ? (int)$u['location_id'] : null,
            'profiles_id'          => isset($u['profile_id']) ? (int)$u['profile_id'] : null,
            'users_id_supervisor'  => isset($u['supervisor_id']) ? (int)$u['supervisor_id'] : null,
            'nameprofil'           => isset($u['profile_name']) ? $u['profile_name'] : null,
            'nameentity'           => isset($u['entity']) ? $u['entity'] : null,
            'nameentitycomplete'   => isset($u['entity_path']) ? $u['entity_path'] : null,
        ];

        // Action rights according to belonging
        $deleteToAdd = new ActionConfirmItem(
            _("Delete"),
            "deleteEntity",
            "delete",
            "",
            "admin",
            "admin",
            sprintf(
                _T("Are you sure you want to delete the entity <strong>%s</strong> ? All packages linked to this entity will also be deleted.", "admin"), htmlspecialchars($data['name'][$i]
            ))
        );

    // ---- strict deactivation on the root entity (id = 0) ----
    $entityIdCurrent = isset($data['id'][$i]) ? (int)$data['id'][$i] : null;
    if ($entityIdCurrent === 0) {
        // we gray edit and delete for the root
        $editAction[]        = new EmptyActionItem1(_("Modification non autorisée"), "", "editg", "", "admin", "admin");
        $addAction[]         = $action_add;
        $manageusersAction[] = $action_manageusers;
        $downloadAction[]    = $action_download;
        $deleteAction[]      = new EmptyActionItem1(_("Suppression non autorisée"), "", "deleteg", "", "admin", "admin");

        continue;
    }

        $array_list_user_for_entity = array_filter(array_map('trim', explode(",", $data['userIds'][$i])));
        if (in_array((string)$u['id'], $array_list_user_for_entity, true) || in_array((int)$u['id'], $array_list_user_for_entity, true)) {
            // Owner: Limited actions
            $editAction[]        = $action_non_edit;
            $addAction[]         = $action_add;
            $manageusersAction[] = $action_manageusers;
            $downloadAction[]    = $action_download;
            $deleteAction[]      = $action_non_delete;
        } else {
            // Non owner: Complete actions
            $editAction[]        = $action_edit;
            $addAction[]         = $action_add;
            $manageusersAction[] = $action_manageusers;
            $downloadAction[]    = $action_download;
            $deleteAction[]      = $deleteToAdd;
        }
    }


$cn = array_values((array)($data['completename'] ?? []));

// entities_id = 0  => We do not touch the 1st element
// sinon            => We treat all the elements
$entitiesId  = (int)($u['entities_id'] ?? 0);
$processAll  = ($entitiesId !== 0);

$displayArray = array_map(function ($s, $i) use ($processAll) {
    $s = trim((string)$s);

    // If we should not treat the 1st, we return it as it is
    if (!$processAll && $i === 0) {
        return $s;
    }

    $parts = array_map('trim', explode('>', $s));
    if (count($parts) > 1) {
        array_shift($parts); // remove the 1st part
        return implode(' > ', $parts);
    }
    return $s;
}, $cn, array_keys($cn));

// Rendered list
$n = new OptimizedListInfos($data['name'], _T("Name of Entity", "admin"));
$n->addExtraInfo($displayArray, _T("Complete Name", "admin"));
$n->addExtraInfo($data['nb_users'], _T("Users", "admin"));
$n->addExtraInfo($data['nb_machines'], _T("Computers", "admin"));

    $n->addActionItemArray($editAction);
    $n->addActionItemArray($addAction);
    $n->addActionItemArray($manageusersAction);
    $n->addActionItemArray($downloadAction);
    $n->addActionItemArray($deleteAction);
    $n->setParamInfo($params);
    $n->start = $start;
    $n->end   = $entitiesListseach['total_count'];
    $n->setNavBar(new AjaxNavBar("10", $filter));
    $n->disableFirstColumnActionLink();
    $n->display();
}
?>

<script>
jQuery(document).ready(function($) {
    // Click management on publishing and addition links
    $('li.edit a, li.add a').on('click', function(e) {
        const $link = $(this);
        let href = $link.attr('href');
        if (href.includes('mode=')) return;

        let mode = $link.closest('li').hasClass('edit') ? 'edit'
                 : $link.closest('li').hasClass('add')  ? 'add'
                 : '';

        const separator = href.includes('?') ? '&' : '?';
        window.location.href = href + separator + 'mode=' + mode;
        e.preventDefault();
    });
});
</script>