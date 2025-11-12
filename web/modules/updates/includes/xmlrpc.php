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
 */

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

function xmlrpc_get_all_machines_grouped_by_os($start=0, $limit=-1, $filter="")
{
    return xmlCall("updates.get_all_machines_grouped_by_os", [$start, $limit, $filter]);
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
