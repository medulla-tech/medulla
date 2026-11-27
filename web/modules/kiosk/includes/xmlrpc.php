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
 *
 */

function xmlrpc_kiosk_get_profiles_list($entity, $start, $limit, $filter)
{
    return xmlCall("kiosk.get_profiles_list", array($entity, $start, $limit, $filter));
}

function xmlrpc_kiosk_get_profile_by_id($id)
{
    return xmlCall("kiosk.get_profile_by_id", array($id));
}

function xmlrpc_kiosk_create_profile($name, $entity_id, $source, $ous, $active, $packages)
{
    return xmlCall("kiosk.create_profile", array($name, $entity_id, $source, $ous, $active, $packages));
}

function xmlrpc_kiosk_update_profile($id, $name, $entity_id, $source, $ous, $active, $packages)
{
    return xmlCall("kiosk.update_profile", array($id, $name, $entity_id, $source, $ous, $active, $packages));
}

function xmlrpc_kiosk_delete_profiles($ids)
{
    return xmlCall("kiosk.delete_profiles", array($ids));
}

function xmlrpc_kiosk_get_ou_list($source, $entity_id)
{
    return xmlCall("kiosk.get_ou_list", array($source, $entity_id));
}

function xmlrpc_kiosk_count_machines_of_ous($source, $ous, $entity_id)
{
    return xmlCall("kiosk.count_machines_of_ous", array($source, $ous, $entity_id));
}
