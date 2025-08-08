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

function xmlrpc_get_CONNECT_API()
{
    return xmlCall("admin.get_CONNECT_API", []);
}

function xmlrpc_get_list($entities, $is_recursive = False)
{
    return xmlCall("admin.get_list", array($entities, $is_recursive));
}

function xmlrpc_get_user_info($userId = '')
{
    return xmlCall("admin.get_user_info", array($userId));
}

function xmlrpc_get_users_count_by_entity($entityId)
{
    return xmlCall("admin.get_users_count_by_entity", [$entityId]);
}

function xmlrpc_get_counts_by_entity($entities = [])
{
    return xmlCall("admin.get_counts_by_entity", [$entities]);
}

function xmlrpc_get_entity_info($entityId)
{
    return xmlCall("admin.get_entity_info", array($entityId));
}

function xmlrpc_get_profile_name($profilId)
{
    return xmlCall("admin.get_profile_name", array($profilId));
}

function xmlrpc_create_entity_under_custom_parent($parent_entity_id, $name)
{
    return xmlCall("admin.create_entity_under_custom_parent", array($parent_entity_id, $name));
}


function xmlrpc_update_entity($entityId, $itemName, $newEntityName, $parentId)
{
    return xmlCall("admin.update_entity", array($entityId, $itemName, $newEntityName, $parentId));
}

function xmlrpc_delete_entity($entityId)
{
    return xmlCall("admin.delete_entity", array($entityId));
}

function xmlrpc_create_organization(
    $parent_entity_id,
    $name_new_entity,
    $name_user,
    $pwd,
    $profiles_id,
    $tag_value = "",
    $realname = null,
    $firstname = null
) {
    return xmlCall("admin.create_organization", [
        $parent_entity_id,
        $name_new_entity,
        $name_user,
        $pwd,
        $profiles_id,
        $tag_value,
        $realname,
        $firstname
    ]);
}
