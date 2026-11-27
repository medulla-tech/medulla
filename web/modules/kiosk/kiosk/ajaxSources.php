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
 * file: ajaxSources.php
 */

require_once("modules/kiosk/includes/xmlrpc.php");
require_once("modules/kiosk/includes/functions.php");

kioskRequireAcl(array("add", "edit"));

$source = (string) ($_POST['source'] ?? '');
$entity = kioskPostedEntity();
if ($entity === null) {
    exit;
}

$tree = xmlrpc_kiosk_get_ou_list($source, $entity);
if (!is_array($tree) || !isset($tree['child']) || !is_array($tree['child'])) {
    $tree = array('name' => '', 'child' => array());
}

// Values of the edited profile no machine carries any more stay selectable.
if (!empty($_POST['profile_id'])) {
    $profile = xmlrpc_kiosk_get_profile_by_id(intval($_POST['profile_id']));
    if (is_array($profile) && $profile['source'] === $source && $profile['entity_id'] !== null
        && intval($profile['entity_id']) === $entity) {
        $paths = array();
        kioskTreePaths($tree, $paths);
        foreach ($profile['ous'] as $ou) {
            if (!isset($paths[(string) $ou])) {
                $tree['child'][] = array('name' => (string) $ou, 'child' => array(), 'path' => (string) $ou, 'selectable' => true);
            }
        }
    }
}

$count = 0;
echo recursiveArrayToList($tree, $count);
exit;
