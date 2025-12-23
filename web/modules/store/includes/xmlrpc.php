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
 * Store module - XMLRPC functions
 */

function xmlrpc_get_all_software($active_only = true, $start = 0, $limit = 0, $sort = "popular") {
    return xmlCall("store.get_all_software", array($active_only, $start, $limit, $sort));
}

function xmlrpc_get_software_by_id($software_id) {
    return xmlCall("store.get_software_by_id", array($software_id));
}

function xmlrpc_get_filters() {
    return xmlCall("store.get_filters", array());
}

function xmlrpc_search_software($filters = array(), $start = 0, $limit = 0, $sort = "popular") {
    return xmlCall("store.search_software", array($filters, $start, $limit, $sort));
}

function xmlrpc_get_pending_requests() {
    return xmlCall("store.get_pending_requests", array());
}

function xmlrpc_get_store_stats() {
    return xmlCall("store.get_store_stats", array());
}

// ============================================
// Functions for subscriptions
// ============================================

function xmlrpc_get_client_uuid() {
    return xmlCall("store.get_client_uuid", array());
}

function xmlrpc_get_client_info() {
    return xmlCall("store.get_client_info", array());
}

function xmlrpc_get_client_subscriptions() {
    return xmlCall("store.get_client_subscriptions", array());
}

function xmlrpc_save_subscriptions($software_ids) {
    return xmlCall("store.save_subscriptions", array($software_ids));
}

function xmlrpc_get_subscribers_for_software($software_id) {
    return xmlCall("store.get_subscribers_for_software", array($software_id));
}

function xmlrpc_create_software_request($software_name, $os, $requester_name, $requester_email, $message = "") {
    return xmlCall("store.create_software_request", array($software_name, $os, $requester_name, $requester_email, $message));
}
?>
