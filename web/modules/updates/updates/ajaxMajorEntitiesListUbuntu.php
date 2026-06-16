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
 * file: ajaxMajorEntitiesListUbuntu.php
 */

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

global $conf;
$maxperpage   = $conf["global"]["maxperpage"];
?>

<style>
.csszoomHover {
    display: inline-block;
    transition: transform 0.15s ease, color 0.15s ease;
}

.csszoomHover:hover {
    transform: translateY(-3px) scale(1.06);
    color: #0a58ca;
}
</style>

<?php
$distribution = "ubuntu";

$filter = isset($_GET['filter']) ? $_GET['filter'] : "";
$start  = isset($_GET['start'])  ? (int) $_GET['start'] : 0;
$end    = $start + $maxperpage;
$source = isset($_GET['source']) ? $_GET['source'] : "";

$_entities = getUserLocations();

$listentity       = [];
$listcompletename = [];
$filtered_entities = [];

foreach ($_entities as $entity) {
    if (
        preg_match("#" . $filter . "#i", $entity['name']) ||
        preg_match("#" . $filter . "#i", $entity['completename'])
    ) {
        $filtered_entities[] = $entity;
    }

    $entityId = (int) preg_replace('/^UUID/', '', $entity['uuid']);
    $listentity[] = $entityId;
    $listcompletename[$entityId] = $entity['completename'];
}

$entities = array_slice($filtered_entities, $start, $maxperpage, false);

$statversion = xmlrpc_get_distribution_version_compliance(
    $distribution,
    $listentity,
    $start,
    (int) $maxperpage
);

$name_version = $statversion['name_version'] ?? "";
$max_version  = $statversion['max_version'] ?? "";

$versionup = ucwords(strtolower(sprintf(
    "%s %s %s",
    $distribution,
    $max_version,
    $name_version
)));

$strversion = sprintf(
    _T("OS Upgrades To %s", "updates"),
    $versionup
);

$p = new PageGenerator($strversion);
$p->display();

$datestring = date("Ymd_Hi");
$title = _T("OS Upgrades", "updates");
$texte_help = _T(
    "%s machines in the entity \"%s\" can benefit from a major update.",
    "updates"
);

$updateAll = new ActionPopupItem(_T("Deploy all major updates on entity", "updates"),
                                "grpDeployUpdateLinuxMajor",
                                "updateallg",
                                "",
                                "updates",
                                "updates",
                                null,
                                320,"machine");

$emptyupdateAll = new EmptyActionItem1(_T("There are no major updates to deploy for the entity.", "updates"),
                                        "grpDeployUpdateLinuxMajor",
                                        "updateallg",
                                        "",
                                        "updates",
                                        "updates");

$outdated_machines          = [];
$up_to_date_machines        = [];
$pending_support_update     = [];
$total_machines             = [];
$comformite_name_major      = [];
$display_entities           = [];
$actionupdateByentity       = [];
$has_deployable_updates     = false;
$params =  array();

$statversion_by_entity = $statversion['by_entity'] ?? [];
if (empty($statversion_by_entity)) {
    foreach ($entities as $entity) {
        $entityId = (int) preg_replace('/^UUID/', '', $entity['uuid']);
        $statversion_by_entity[$entityId] = [
            'entity_id' => $entityId,
            'outdated_machines' => 0,
            'up_to_date_machines' => 0,
            'pending_support_update' => 0,
            'total_machines' => 0,
            'compliance_rate' => 0,
        ];
    }
}

foreach ($statversion_by_entity as $entityId => $ent) {
    if ( $ent['outdated_machines'] > 0){
        $has_deployable_updates = true;
        $actionupdateByentity[] = $updateAll;
    }else{
        $actionupdateByentity[] = $emptyupdateAll;
    }

    $id         = $ent['entity_id'];
    $entityName = $listcompletename[$id] ?? (string) $id;
    $display_entities[] = $entityName;

    $formattedText_help = sprintf(
        $texte_help,
        $ent['outdated_machines'],
        $entityName
    );

    if (intval($ent['total_machines']) > 0) {
        $comformite_name_major[] = (string) new medulla_progressbar_static(
            $ent['compliance_rate'],
            "",
            $formattedText_help
        );
    } else {
        $comformite_name_major[] = "";
    }

    $grp = new ActionAjaxPopup(
        "CreateGroup",
        "ajaxUpdateCreateGroup",
        "btnCreateGroup",
        '',
        _T("Do you want to create the group?", "updates"),
        "updates",
        "updates",
        null,
        450,
        false,
        true
    );

    if (intval($ent['outdated_machines']) > 0) {
        $namegrp = sprintf(
            "%s - %s - [%s] (%s) - %s",
            ucfirst($distribution),
            _T("Outdated machines", "updates"),
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s\n\n%s\n%s",
            $formattedText_help,
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "outdated_machines",
            "typeaction" => $distribution
        ]);

        $outdated_machines[] = $grp->render(
            $ent['outdated_machines'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
    } else {
        $outdated_machines[] = $ent['outdated_machines'];
    }

    if (intval($ent['up_to_date_machines'])  > 0) {
        $namegrp = sprintf(
            "%s - %s %s - [%s] (%s)- %s",
            ucfirst($distribution),
            _T("Up to date machines", "updates"),
            $versionup,
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s %s\n\n%s\n%s",
            _T("All machines are up to date with version", "updates"),
            $versionup,
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "up_to_date_machines",
            "typeaction" => $distribution
        ]);

        $up_to_date_machines[] = $grp->render(
            $ent['up_to_date_machines'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
    } else {
        $up_to_date_machines[] = $ent['up_to_date_machines'];
    }

    if (intval($ent['pending_support_update']) > 0) {
        $namegrp = sprintf(
            "%s - %s - [%s] (%s) - %s",
            ucfirst($distribution),
            _T("Pending support update", "updates"),
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s\n\n%s\n%s",
            _T("Machines with Ubuntu version pending support update", "updates"),
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "pending_support_update",
            "typeaction" => $distribution
        ]);

        $pending_support_update[] = $grp->render(
            $ent['pending_support_update'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
    } else {
        $pending_support_update[] = $ent['pending_support_update'];
    }

    if (intval($ent['total_machines']) > 0) {
        $namegrp = sprintf(
            "%s - %s - [%s] - ()%s)%s",
            ucfirst($distribution),
            _T("All machines", "updates"),
            $entityName,
            $_SESSION['login'],
            $datestring
        );

        $msgtitle = sprintf(
            "%s %s\n\n%s\n%s",
            _T("Total Ubuntu machines in entity", "updates"),
            $entityName,
            _T("Create group:", "updates"),
            $namegrp
        );

        $tabcgi = array_merge($ent, [
            "grp"        => $distribution,
            "namegrp"    => $namegrp,
            "colonne"    => "total_machines",
            "typeaction" => $distribution
        ]);

        $total_machines[] = $grp->render(
            $ent['total_machines'],
            $tabcgi,
            $msgtitle,
            "csszoomHover"
        );
    } else {
        $total_machines[] = $ent['total_machines'];
    }

    $ent['entityName'] = $entityName;
    $ent['distribution'] = $statversion['distribution'] ?? $distribution;
    $ent['name_version'] = $name_version;
    $ent['max_version']  = $max_version;
    $params[] = $ent;
}

$display_entities = array_values($display_entities);
$comformite_name_major = array_values($comformite_name_major);
$outdated_machines = array_values($outdated_machines);
$up_to_date_machines = array_values($up_to_date_machines);
$pending_support_update = array_values($pending_support_update);
$total_machines = array_values($total_machines);
$actionupdateByentity = array_values($actionupdateByentity);
$params = array_values($params);

$count = count($display_entities);
$n = new OptimizedListInfos($display_entities, _T("Entity name", "updates"));
$n->disableFirstColumnActionLink();
$n->addExtraInfo($comformite_name_major, _T("Compliance rate", "updates"));
$n->addExtraInfoRaw($outdated_machines, _T("Upgrade to ", "updates")." ".$strversion);
$n->addExtraInfoRaw($up_to_date_machines, _T("Up to date", "updates"));
$n->addExtraInfoRaw($pending_support_update, _T("Pending Support Update", "updates"));
$n->addExtraInfoRaw($total_machines, _T("Total Machines", "updates")." ".$distribution);
if ($has_deployable_updates) {
    $n->addActionItemArray($actionupdateByentity);
}
$n->setNavBar(new AjaxNavBar($count, $filter));
$n->display();

?>
