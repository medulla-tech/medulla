<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: general.php 26 2007-10-17 14:48:41Z nrueff $
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require('modules/msc/includes/machines.inc.php');
require('modules/msc/includes/widgets.inc.php');

if ($_GET['name']) {
    $machine = getMachine(array('hostname'=>$_GET['name'])); // should be changed in uuid
    if ($machine->hostname != $_GET['name']) {
        $msc_host = new RenderedMSCHostDontExists($_GET['name']);
        $msc_host->headerDisplay();
    } else {
        $msc_host = new RenderedMSCHost($machine);
        $msc_host->headerDisplay();
    }
} else {
    $group = new Stagroup($_GET['gid']);
}

?>

