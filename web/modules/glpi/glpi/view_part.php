<?
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require_once("modules/glpi/includes/xmlrpc.php");

$uuid = '';
if (isset($_GET['uuid'])) {
    $uuid = $_GET['uuid'];
} elseif (isset($_GET['objectUUID'])) {
    $uuid = $_GET['objectUUID'];
}
$inv = getLastMachineGlpiPart($uuid, $_GET['part']);
if (!is_array($inv)) $inv = array();

$all = array();
$i = 0;
foreach ($inv as $line) {
    foreach ($line as $vals) {
        $all[$vals[0]][$i] = $vals[1];
    }
    $i+=1;
}

$n = null;

foreach (array('type', 'designation', 'name') as $i) {
    if ($i == 'type' && array_key_exists($i, $all)) {
        $conv = array();
        foreach ($all[$i] as $j) { $conv[] = _T($j, 'glpi'); }
        $all[$i] = $conv;
    }
    if (array_key_exists($i, $all)) {
        if ($n == null) {
            $n = new ListInfos($all[$i], _T($i, 'glpi'));
        } else {
            $n->addExtraInfo($all[$i], _T($i, 'glpi'));
        }
        unset($all[$i]);
    }
}

foreach ($all as $k => $v) {
    if ($n == null) {
        $n = new ListInfos($v, _T($k, 'glpi'));
    } else {
        $n->addExtraInfo($v, _T($k, 'glpi'));
    }
}
if ($n) {
    $n->drawTable(0);
}

/**  to get i18n labels... */

_T('name', 'glpi');
_T('comments', 'glpi');
_T('ifaddr', 'glpi');
_T('ifmac', 'glpi');
_T('netmask', 'glpi');
_T('gateway', 'glpi');
_T('subnet', 'glpi');
_T('type', 'glpi');
_T('designation', 'glpi');
_T('specif_default', 'glpi');
_T('frequence', 'glpi');
_T('bandwidth', 'glpi');
_T('is_writer', 'glpi');
_T('interface', 'glpi');
_T('comment', 'glpi');

_T('processor', 'glpi');
_T('ram', 'glpi');
_T('hdd', 'glpi');
_T('iface', 'glpi');
_T('drive', 'glpi');
_T('gfxcard', 'glpi');
_T('sndcard', 'glpi');
_T('pci', 'glpi');


/* xxxxxxx */

?>

</table>

