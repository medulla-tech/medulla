<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("localSidebar.php");
require("graph/navbar.inc.php");

$name = urldecode($_GET["name"]);

$p = new PageGenerator(sprintf(_T("Image informations for %s"), $name));
$p->setSideMenu($sidemenu);
$p->display();

$infos = getPublicImageInfos($name);

printf(_("Title: <b>%s</b><br/>"), $infos['title']);
printf(_("Description: <b>%s</b><br/>"), $infos['desc']);
printf(_("Discs / partitions :<br/><ul>"));
ksort($infos['disks']);
foreach(array_keys($infos['disks']) as $disknr) {
    printf(_("<li>Disk #$disknr:<br/><ul>"));
    ksort($infos['disks'][$disknr]);
    foreach(array_keys($infos['disks'][$disknr]) as $partnr) {
        if (is_int($partnr)) {
            printf(_("<li>Part #%d: type %s, starting at %s, ending at %s (total size: <b>%s</b>)</li>"),
                $partnr,
                $infos['disks'][$disknr][$partnr]['kind'],
                humanReadable($infos['disks'][$disknr][$partnr]['start']),
                humanReadable($infos['disks'][$disknr][$partnr]['size'] + $infos['disks'][$disknr][$partnr]['start']),
                humanReadable($infos['disks'][$disknr][$partnr]['size'])
            );
        }
    }
    printf("</ul>");
}

printf("</ul>");

?>
