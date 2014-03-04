<?php

/**
 * (c) 2013 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
require_once dirname(__FILE__) . '/xmlrpc.inc.php';

function listInfoFriendly($data) {
    // Take a @_listinfo decorator data, and make it listinfo fiendly
    $result = array();

    foreach ($data as $entry) {
        foreach ($entry as $key => $val) {
            if (!isset($result[$key]))
                $result[$key] = array();
            $result[$key][] = $val;
        }
    }
    return $result;
}

function getUpdateTypeLabel($update_type_id) {
    $types = get_update_types();

    foreach ($types as $type)
        if ($type['id'] == $update_type_id)
            return _T($type['name'], 'update');
}

?>