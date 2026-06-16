<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
 * (c) 2022-2023 Siveo, http://http://www.siveo.net
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
 * file : web/modules/updates/includes/xmlrpc.php
 */


function xmlrpc_has_update_data()
{
    return xmlCall("updates.has_update_data");
}

function xmlrpc_tests()
{
    return xmlCall("updates.tests");
}

function xmlrpc_get_grey_list($start, $end, $filter = "", $entityid=-1)
{
    return xmlCall("updates.get_grey_list", [  $start,
                                                $end,
                                                $filter,
                                                $entityid] );
}

function xmlrpc_get_white_list($start, $end, $filter = "", $entityid=-1)
{
    return xmlCall("updates.get_white_list", [  $start,
                                                $end,
                                                $filter,
                                                $entityid] );
}

function xmlrpc_get_black_list($start, $end, $filter = "", $entityid=-1)
{
    return xmlCall("updates.get_black_list", [  $start,
                                                $end,
                                                $filter,
                                                $entityid] );
}

function xmlrpc_get_enabled_updates_list($entity, $upd_list = "gray", $start = 0, $end = -1, $filter = "")
{
    return xmlCall("updates.get_enabled_updates_list", [$entity, $upd_list, $start, $end, $filter]);
}

function xmlrpc_get_family_list($start, $end, $filter = "", $entityid=-1)
{
    return xmlCall("updates.get_family_list", [$start, $end, $filter, $entityid=-1]);
}

function xmlrpc_approve_update($updateid, $entityid)
{
    return xmlCall("updates.approve_update", [$updateid, $entityid]);
}

function xmlrpc_grey_update($updateid, $entityid, $enabled = 0)
{
    return xmlCall("updates.grey_update", [$updateid, $entityid, $enabled]);
}

function xmlrpc_exclude_update($updateid, $entityid)
{
    return xmlCall("updates.exclude_update", [$updateid, $entityid]);
}

function xmlrpc_delete_rule($id, $entityid)
{
    return xmlCall("updates.delete_rule", [$id, $entityid]);
}

function xmlrpc_white_unlist_update($updateid, $entityid)
{
    return xmlCall("updates.white_unlist_update", [$updateid, $entityid]);
}

function xmlrpc_get_machine_with_update($kb, $updateid="", $entity, $start=0, $limit=-1, $filter=""){
    return xmlCall("updates.get_machine_with_update", [$kb, $updateid, $entity, $start, $limit, $filter]);
}

function xmlrpc_get_count_machine_with_update($kb, $uuid, $list)
{
    return xmlCall("updates.get_count_machine_with_update", [$kb, $uuid, $list]);
}

function xmlrpc_get_count_machine_as_not_upd($updateid)
{
    return xmlCall("updates.get_count_machine_as_not_upd", [$updateid]);
}

function xmlrpc_get_machines_needing_update($updateid, $entity, $start=0, $limit=-1, $filter="")
{
    return xmlCall("updates.get_machines_needing_update", [$updateid, $entity, $start, $limit, $filter]);
}

function xmlrpc_get_conformity_update_by_entity($entities = [], $source)
{
    return xmlCall("updates.get_conformity_update_by_entity", [$entities, $source]);
}

function xmlrpc_get_machines_xmppmaster($start=0, $limit=-1, $filter="")
{
    return xmlCall("updates.get_machines_xmppmaster", [$start, $limit, $filter]);
}

function xmlrpc_get_all_machines_grouped_by_os($start=0, $limit=-1, $filter="", $os_filter="")
{
    return xmlCall("updates.get_all_machines_grouped_by_os", [$start, $limit, $filter, $os_filter]);
}


function xmlrpc_get_machine_in_both_sources($glpi_uuids)
{
    return xmlCall("updates.get_machine_in_both_sources", [$glpi_uuids]);
}

function xmlrpc_get_conformity_update_by_machines($ids = [])
{
    return xmlCall("updates.get_conformity_update_by_machines", [$ids]);
}



function xmlrpc_get_os_update_major_stats_win_serv()
{
    return xmlCall("updates.get_os_update_major_stats_win_serv", []);
}

function xmlrpc_get_os_update_major_stats_win()
{
    return xmlCall("updates.get_os_update_major_stats_win", []);
}

function xmlrpc_get_os_xmpp_update_major_stats()
{
    return xmlCall("updates.get_os_xmpp_update_major_stats", []);
}


function xmlrpc_get_outdated_major_os_updates_by_entity($entity_id,
                                                        $typeaction,
                                                        $start=0,
                                                        $limit=-1,
                                                        $filter="",
                                                        $colonne=True)
{
    return xmlCall("updates.get_outdated_major_os_updates_by_entity", [$entity_id,
                                                                        $typeaction,
                                                                        $start,
                                                                        $limit,
                                                                        $filter,
                                                                        $colonne]);
}

function xmlrpc_get_os_update_major_details($entity_id,
                                            $typeaction,
                                            $filter="",
                                            $start=0,
                                            $limit=-1)
{
    return xmlCall("updates.get_os_update_major_details", [ $entity_id,
                                                            $typeaction,
                                                            $filter,
                                                            $start,
                                                            $limit]);
}

function xmlrpc_get_os_xmpp_update_major_details($entity_id, $filter="",$start=0, $limit=-1, )
{
    return xmlCall("updates.get_os_xmpp_update_major_details", [$entity_id, $filter, $start, $limit]);
}

function xmlrpc_get_machines_update_grp($entity_id,
                                        $type="window",
                                        $colonne="hardware_requirements")
{
    return xmlCall("updates.get_machines_update_grp", [$entity_id, $type, $colonne]);
}
// JFKJFK
function xmlrpc_analyze_machine_compliance_linux($entity_id,
                                                 $filter="",
                                                 $start=-1,
                                                 $limit=-1,
                                                 $colonne=True)
{
    return xmlCall("updates.analyze_machine_compliance_linux", [$entity_id,
                                                                $filter,
                                                                $start,
                                                                $limit,
                                                                $colonne]);
}

/**
 * Met à jour la conformité des machines via XML-RPC.
 *
 * @param string $action Type d'action (ex: "require_kernel", "current_all", etc.).
 * @param int $onoff 0 ou 1 pour activer/désactiver.
 * @param string|array|null $harduuids Liste de UUIDs ou un seul UUID (ou null).
 * @param int|array|null $entity_ids ID d'entité ou tableau d'IDs (ou null).
 * @param array|null $distributor_ids Tableau de distributeurs (ex: ["debian", "redhat"]) ou null.
 * @param string|null $date_start Date de début (format valide ou null/"").
 * @param string|null $date_stop Date de fin (format valide ou null/"").
 * @param string|null $interval Intervalle (format valide ou null/"").
 *
 * @return array Résultat de l'appel XML-RPC sous la forme [bool, string].
 *               Le booléen indique le succès (true) ou l'échec (false), et la chaîne contient le message.
 */
function xmlrpc_update_machine_compliance_by_action($action,
                                                    $onoff,
                                                    $date_start = null,
                                                    $date_stop = null,
                                                    $interval = null,
                                                    $harduuids = null,
                                                    $entity_ids = null,
                                                    $distributor_ids = null) {
    // Liste des actions autorisées
    $valid_actions = [
        "require_kernel",
        "require_security",
        "require_other",
        "current_kernel",
        "current_security",
        "current_other",
        "require_all",
        "current_all"
    ];

    // Vérification de $action
    if (!in_array($action, $valid_actions)) {
        return [false, "Erreur : Action invalide. Les valeurs autorisées sont : " . implode(", ", $valid_actions)];
    }

    // Vérification de $onoff (doit être 0 ou 1)
    if (!in_array($onoff, [0, 1], true)) {
        return [false, "Erreur : 'onoff' doit être 0 ou 1."];
    }

    // Vérification de $date_start (doit être null, "", ou une date valide)
    if ($date_start !== null && $date_start !== "") {
        if (!is_string($date_start) || !validateDate($date_start)) {
            return [false, "Erreur : 'date_start' doit être une date valide, null ou une chaîne vide."];
        }
    }

    // Vérification de $date_stop (doit être null, "", ou une date valide)
    if ($date_stop !== null && $date_stop !== "") {
        if (!is_string($date_stop) || !validateDate($date_stop)) {
            return [false, "Erreur : 'date_stop' doit être une date valide, null ou une chaîne vide."];
        }
    }

    // Vérification de $interval (doit être null, "", ou une chaîne non vide)
    if ($interval !== null && $interval !== "") {
        if (!is_string($interval) || empty(trim($interval))) {
            return [false, "Erreur : 'interval' doit être une chaîne non vide, null ou une chaîne vide."];
        }
    }

    // Vérification de $harduuids (doit être null, une chaîne non vide ou un tableau de chaînes non vides)
    if ($harduuids !== null) {
        if (is_string($harduuids)) {
            // Si c'est une chaîne vide, on la remplace par null
            if (empty(trim($harduuids))) {
                $harduuids = null;
            }
        } elseif (is_array($harduuids)) {
            // Vérifier que chaque élément est une chaîne non vide
            $valid_uuids = [];
            foreach ($harduuids as $uuid) {
                if (is_string($uuid) && !empty(trim($uuid))) {
                    $valid_uuids[] = $uuid;
                }
            }
            // Si aucun UUID valide, on remplace par null
            if (empty($valid_uuids)) {
                $harduuids = null;
            } else {
                $harduuids = $valid_uuids;
            }
        } else {
            return [false, "Erreur : 'harduuids' doit être une chaîne, un tableau de chaînes ou null."];
        }
    }
    // Vérification de $entity_ids (doit être null, un entier (y compris 0) ou un tableau d'entiers >= 0)
    if ($entity_ids !== null) {
        if (is_string($entity_ids) && $entity_ids === '') {
            // Si c'est une chaîne vide, on la remplace par null
            $entity_ids = null;
        } elseif (is_int($entity_ids)) {
            if ($entity_ids < 0) { // On accepte 0, mais pas les négatifs
                return [false, "Erreur : L'ID d'entité doit être un entier positif ou nul."];
            }
        } elseif (is_array($entity_ids)) {
            $valid_ids = [];
            foreach ($entity_ids as $id) {
                if (is_int($id) && $id >= 0) { // On accepte 0 et les positifs
                    $valid_ids[] = $id;
                }
            }
            // Si aucun ID valide, on remplace par null
            if (empty($valid_ids)) {
                $entity_ids = null;
            } else {
                $entity_ids = $valid_ids;
            }
        } else {
            return [false, "Erreur : 'entity_ids' doit être un entier, un tableau d'entiers ou null."];
        }
    }
    // Vérification de $distributor_ids (doit être null ou un tableau de chaînes non vides)
    if ($distributor_ids !== null) {
        if (is_string($distributor_ids) && $distributor_ids === '') {
            // Si c'est une chaîne vide, on la remplace par null
            $distributor_ids = null;
        } elseif (is_array($distributor_ids)) {
            $valid_distros = [];
            foreach ($distributor_ids as $distro) {
                if (is_string($distro) && !empty(trim($distro))) {
                    $valid_distros[] = $distro;
                }
            }
            // Si aucun distributeur valide, on remplace par null
            if (empty($valid_distros)) {
                $distributor_ids = null;
            } else {
                $distributor_ids = $valid_distros;
            }
        } else {
            return [false, "Erreur : 'distributor_ids' doit être un tableau ou null."];
        }
    }


    // Appel XML-RPC si tous les contrôles sont passés
    $result = xmlCall("updates.update_machine_compliance_by_action", [
        $action,
        $onoff,
        $date_start,
        $date_stop,
        $interval,
        $harduuids,
        $entity_ids,
        $distributor_ids
    ]);

    // Vérification du résultat de l'appel XML-RPC
    if (is_array($result) && count($result) >= 2) {
        if ($result[0] === false) {
            return [false, $result[1]];
        } else {
            return [true, $result[1]];
        }
    }
    return [false, "Erreur : Réponse XML-RPC invalide."];
}

/**
 * Valide une date au format YYYY-MM-DD HH:MM:SS.
 *
 * @param string $date La date à valider.
 * @return bool True si la date est valide, false sinon.
 */
function validateDate($date) {
    $d = DateTime::createFromFormat('Y-m-d H:i:s', $date);
    return $d && $d->format('Y-m-d H:i:s') === $date;
}

function xmlrpc_analyze_machine_compliance_distribution_linux(  $entity_id,
                                                                $filter="",
                                                                $start=-1,
                                                                $limit=-1,
                                                                $colonne=True)
{
    return xmlCall("updates.analyze_machine_compliance_distribution_linux", [$entity_id,
                                                                             $filter,
                                                                             $start,
                                                                             $limit,
                                                                             $colonne]);
}

function xmlrpc_get_machines_by_update_type(  $entity_id,
                                              $updatetype,
                                              $filter="",
                                              $start=-1,
                                              $limit=-1,
                                              $colonne=True)
{
    return xmlCall("updates.get_machines_by_update_type", [$entity_id,
                                                           $updatetype,
                                                           $filter,
                                                           $start,
                                                           $limit,
                                                           $colonne]);
}

function xmlrpc_deploy_update_major($package_id,
                                    $uuid_inventorymachine,
                                    $hostname,
                                    $title_deployement=null,
                                    $start_date = null,
                                    $end_date = null,
                                    $deployment_intervals="",
                                    $userconnect="root",
                                    $usercreator="root",
                                    $list_file="fileslistpackage")
{
    return xmlCall("updates.deploy_update_major", [ $package_id,
                                                    $uuid_inventorymachine,
                                                    $hostname,
                                                    $title_deployement,
                                                    $start_date,
                                                    $end_date,
                                                    $deployment_intervals,
                                                    $userconnect,
                                                    $usercreator,
                                                    $list_file]);
}
