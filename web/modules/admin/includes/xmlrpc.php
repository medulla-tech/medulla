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

function xmlrpc_get_CONNECT_API($tokenuser=null)
{
    return xmlCall("admin.get_CONNECT_API", [$tokenuser]);
}

function xmlrpc_get_list($entities, $is_recursive = False, $tokenuser=null)
{
    return xmlCall("admin.get_list", array($entities, $is_recursive,$tokenuser));
}

function xmlrpc_get_list_user_token($tokenuser = null)
{
    return xmlCall("admin.get_list_user_token", array($tokenuser));
}

function xmlrpc_get_user_info($userId = '', $tokenuser=null)
{
    return xmlCall("admin.get_user_info", array($userId, $tokenuser));
}

function xmlrpc_get_users_count_by_entity($entityId, $tokenuser=null)
{
    return xmlCall("admin.get_users_count_by_entity", [$entityId, $tokenuser]);
}

function xmlrpc_get_counts_by_entity_root($filter="", $start=-1, $end=-1, $entities=null)
{
    // Récupère les statistiques des entités GLPI (nombre de machines,
    // nombre d'utilisateurs et IDs des utilisateurs), avec options
    // de filtrage, pagination et restriction sur une liste d'entités.
    // attention on doit limiter les entite pour les l'utilisateur non root
    return xmlCall("admin.get_counts_by_entity_root", [$filter, $start, $end, $entities]);
}


function xmlrpc_get_counts_by_entity($entities = [])
{
    return xmlCall("admin.get_counts_by_entity", [$entities]);
}

function xmlrpc_get_entity_info($entityId, $tokenuser=null)
{
    return xmlCall("admin.get_entity_info", array($entityId, $tokenuser));
}

function xmlrpc_get_profile_name($profilId, $tokenuser=null)
{
    return xmlCall("admin.get_profile_name", array($profilId, $tokenuser));
}

function xmlrpc_create_entity_under_custom_parent($parent_entity_id, $name, $tokenuser=null)
{
    return xmlCall("admin.create_entity_under_custom_parent", array($parent_entity_id,
                                                                    $name,
                                                                    $tokenuser));
}


function xmlrpc_update_entity($entityId, $itemName, $newEntityName, $parentId, $tokenuser=null)
{
    return xmlCall("admin.update_entity", array($entityId,
                                                $itemName,
                                                $newEntityName,
                                                $parentId,
                                                $tokenuser));
}

function xmlrpc_delete_entity($entityId, $tokenuser=null)
{
    return xmlCall("admin.delete_entity", array($entityId, $tokenuser));
}

function xmlrpc_create_organization(
    $parent_entity_id,
    $name_new_entity,
    $name_user,
    $pwd,
    $profiles_id,
    $tag_value = "",
    $realname = null,
    $firstname = null,
    $tokenuser=null
) {
    return xmlCall("admin.create_organization", [
        $parent_entity_id,
        $name_new_entity,
        $name_user,
        $pwd,
        $profiles_id,
        $tag_value,
        $realname,
        $firstname,
        $tokenuser
    ]);
}
