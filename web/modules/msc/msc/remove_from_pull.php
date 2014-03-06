<?php


/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2014 Mandriva, http://www.mandriva.com
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

/*
 * Check if we come from computer page by checking if random ID provided
 * by $_GET matches the $_SESSION one
 */

if ($_GET['remove_pull_id'] == $_SESSION['remove_pull_id']) {
    // then remove pull targets from DB
    $result = xmlCall('msc.remove_pull_targets', array($_GET['uuid']));
    if ($result) {
        // then remove random ID
        unset($_SESSION['remove_pull_id']);
        // Remove current UUID from pull_targets session list
        if (($key = array_search($_GET['uuid'], $_SESSION['pull_targets'])) !== false) {
            unset($_SESSION['pull_targets'][$key]);
        }
    }
}
header('Location: ' . $_SERVER['HTTP_REFERER']);
?>
