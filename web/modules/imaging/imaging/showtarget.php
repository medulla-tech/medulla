<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

include('modules/imaging/includes/includes.php');
include('modules/imaging/includes/xmlrpc.inc.php');
$params = getParams();
$id = $_GET['itemid'];
$tid = $_GET['target_uuid'];
$label = urldecode($_GET['itemlabel']);

if (isset($_GET['gid'])) {
    $type = 'group';
} else {
    $type = '';
}

$ret = xmlrpc_areImagesUsed(array(array($id, $tid, $type)));
$ret = $ret[$id];

$f = new ValidatingForm();
$f->add(new TitleElement(_T("Show all targets that use that image in their boot menu", "imaging"), 2));

foreach ($ret as $target) {
    if ($target[1]==-1) { # this is an imaging server
        $params['location'] = $target[0];
        $url = urlStrRedirect("imaging/manage/master", $params);
        $f->add(new TitleElement("<a href='".$url."'>"._T("Imaging server", 'imaging')." : ".$target[2]."</a>", 5));
    } else {
        $params['uuid'] = $target[0];
        $params['hostname'] = $target[2];
        $url = urlStrRedirect("base/computers/imgtabs/".$type."tabimages", $params);
        $f->add(new TitleElement("<a href='".$url."'>".($target[1]==2?_T('Profile', 'imaging'): _T('Computer', 'imaging'))." : ".$target[2]."</a>", 5));
    }
}

$f->addCancelButton('bback');
$f->display();

?>
