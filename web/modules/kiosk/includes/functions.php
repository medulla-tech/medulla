<?php
/**
 * (c) 2018 Siveo, http://siveo.net
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/medulla_server/includes/utilities.php");

/**
 * Entities of the user.
 *
 * @return array GLPI id => full name, not escaped
 */
function kioskEntities()
{
    list($labels, $values) = getEntitiesSelectableElements();
    $entities = array();
    foreach ($values as $key => $uuid) {
        $entities[intval(substr((string) $uuid, 4))] = (string) $labels[$key];
    }
    return $entities;
}

/**
 * Entity chosen in the list filter.
 *
 * @return string "UUIDn" of an entity of the user, "" for all of them
 */
function kioskSelectedLocation()
{
    $location = $_GET['location'] ?? '';
    if (!is_string($location) || !preg_match('/^UUID(\d+)$/', $location, $match)) {
        return '';
    }
    return array_key_exists(intval($match[1]), kioskEntities()) ? $location : '';
}

/**
 * Entity id received from the form.
 *
 * @return int|null null when it is not an id
 */
function kioskPostedEntity()
{
    $entity = $_POST['entity_id'] ?? '';
    return (is_string($entity) && ctype_digit($entity)) ? intval($entity) : null;
}

/**
 * Strings of a posted list.
 *
 * @param string $key Name of the posted field
 * @return array
 */
function kioskPostedList($key)
{
    $values = $_POST[$key] ?? array();
    if (!is_array($values)) {
        return array();
    }
    return array_values(array_filter(array_map('strval', array_filter($values, 'is_scalar')), 'strlen'));
}

/**
 * Stops a page called by the interface when the user lacks the ACL of the
 * pages that carry it.
 *
 * @param string|array $pages Actions of kiosk/kiosk, one is enough
 */
function kioskRequireAcl($pages)
{
    foreach ((array) $pages as $page) {
        if (hasCorrectAcl("kiosk", "kiosk", $page)) {
            return;
        }
    }
    http_response_code(403);
    exit;
}

/**
 * Translated labels of the profile sources.
 *
 * @return array source => label
 */
function kioskSourceLabels()
{
    return array(
        "entity" => _T("None", "kiosk"),
        "ou_user" => _T("User OU", "kiosk"),
        "ou_machine" => _T("Machine OU", "kiosk"),
        "group" => _T("Group", "kiosk"),
        "ldap" => _T("LDAP", "kiosk"),
    );
}

/**
 * Information window for an action the server refused.
 *
 * @param string $message Translated text, already escaped
 */
function kioskNotifyRefusal($message)
{
    $n = new NotifyWidget(false);
    $n->setLevel(4);
    $n->add('<div class="alert alert-info">' . $message . '</div>');
}

/**
 * Deletes profiles and notifies the outcome.
 *
 * @param array $ids Profile ids
 * @return array Ids actually deleted
 */
function kioskDeleteProfiles($ids)
{
    $deleted = xmlrpc_kiosk_delete_profiles($ids);
    $deleted = is_array($deleted) ? array_map('intval', $deleted) : array();
    if (!empty($deleted)) {
        new NotifyWidgetSuccess(sprintf(_T("%d profile(s) successfully deleted", "kiosk"), count($deleted)));
    }
    $refused = count(array_diff($ids, $deleted));
    if ($refused > 0) {
        kioskNotifyRefusal(sprintf(_T("%d profile(s) could not be deleted", "kiosk"), $refused));
    }
    return $deleted;
}

/**
 * Creates or updates the posted profile and answers in JSON.
 *
 * @param string $page "add" or "edit", the page that carries the form
 */
function kioskSaveProfile($page)
{
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
        http_response_code(405);
        exit;
    }
    kioskRequireAcl($page);
    verifyCSRFToken($_POST);

    $name = trim((string) ($_POST['name'] ?? ''));
    $entity = kioskPostedEntity();
    $source = (string) ($_POST['source'] ?? '');
    $active = (($_POST['active'] ?? '') === '1') ? 1 : 0;
    $ous = kioskPostedList('ous');
    $packages = kioskPostedList('packages');

    $saved = false;
    if ($entity !== null) {
        if ($page === 'edit') {
            $saved = xmlrpc_kiosk_update_profile(intval($_POST['id'] ?? 0), $name, $entity, $source, $ous, $active, $packages) === true;
        } else {
            $created = xmlrpc_kiosk_create_profile($name, $entity, $source, $ous, $active, $packages);
            $saved = is_int($created) && $created > 0;
        }
    }

    header('Content-Type: application/json');
    if ($saved) {
        $safeName = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
        new NotifyWidgetSuccess(sprintf(
            ($page === 'edit') ? _T("The profile %s has been updated", "kiosk") : _T("Profile %s successfully added", "kiosk"),
            $safeName
        ));
        echo json_encode(array("status" => "ok"));
    } else {
        echo json_encode(array(
            "status" => "refused",
            "message" => htmlspecialchars(_T("Profile not saved: its name is already used in this entity or too long, or the selection is no longer valid.", "kiosk"), ENT_QUOTES, 'UTF-8'),
        ));
    }
    exit;
}

/**
 * Paths of a tree returned by kiosk.get_ou_list.
 *
 * @param array $node  Node {name, child, path, selectable}
 * @param array $paths Filled with path => true
 */
function kioskTreePaths($node, &$paths)
{
    if (!is_array($node)) {
        return;
    }
    if (($node['path'] ?? '') !== '') {
        $paths[(string) $node['path']] = true;
    }
    foreach ($node['child'] ?? array() as $child) {
        kioskTreePaths($child, $paths);
    }
}

/**
 * Nested list of checkboxes for a tree returned by kiosk.get_ou_list.
 *
 * @param array $node  Node {name, child, path, selectable}
 * @param int   $count Number of nodes written so far
 * @return string
 */
function recursiveArrayToList($node, &$count)
{
    if (!is_array($node)) {
        return '';
    }
    $html = '';
    $name = (string) ($node['name'] ?? '');
    $children = (isset($node['child']) && is_array($node['child'])) ? $node['child'] : array();
    if ($name !== '') {
        $count += 1;
        $id = 'kiosk-ou-' . $count;
        $label = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
        $html .= '<li><div class="kiosk-ou-row">';
        if (!empty($children)) {
            $html .= '<button type="button" class="kiosk-ou-chevron" aria-expanded="true" aria-label="'
                . htmlspecialchars(sprintf(_T("Sub-levels of %s", "kiosk"), $name), ENT_QUOTES, 'UTF-8') . '"></button>';
        } else {
            $html .= '<span class="kiosk-ou-leaf"></span>';
        }
        if (!isset($node['selectable']) || $node['selectable']) {
            $html .= '<input type="checkbox" id="' . $id . '" value="'
                . htmlspecialchars((string) ($node['path'] ?? ''), ENT_QUOTES, 'UTF-8') . '">'
                . '<label for="' . $id . '" title="' . $label . '">' . $label . '</label>';
        } else {
            $html .= '<span class="kiosk-ou-name" title="' . $label . '">' . $label . '</span>';
        }
        $html .= '</div>';
    }
    if (!empty($children)) {
        $html .= '<ul>';
        foreach ($children as $child) {
            $html .= recursiveArrayToList($child, $count);
        }
        $html .= '</ul>';
    }
    if ($name !== '') {
        $html .= '</li>';
    }
    return $html;
}
