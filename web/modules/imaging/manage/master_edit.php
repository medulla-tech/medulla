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

require("localSidebar.php");
require("graph/navbar.inc.php");
require_once('modules/imaging/includes/includes.php');
require_once('modules/imaging/includes/xmlrpc.inc.php');

$id = $_GET['itemid'];
$location = getCurrentLocation();
$masters = xmlrpc_getLocationMastersByUUID($location, array($id));

if(count($_POST) == 0) {

    // get current values
    // {'UUID1': {u'name': u'Image 1', u'checksum': u'', u'uuid': u'932d91a6-c4a3-11de-b49a-000c295966ea', 'fk_creator': 1L, u'creation_date': datetime.datetime(2010, 3, 1, 16, 38, 57), 'imaging_uuid': 'UUID1', u'is_master': True, u'path': u'/path/?', u'size': 12345L, u'id': 1L, u'desc': u'Mon Mar  1 15:46:43 CET 2010'}},)
    $master = $masters[$id];
    $label = $master['name'];
    $desc = $master['desc'];
    if($masters[$id][4] == 'yes')
        $in_bootmenu = 'CHECKED';

    $p = new PageGenerator(_T("Edit master : ", "imaging").$label);
    $sidemenu->forceActiveItem("master");
    $p->setSideMenu($sidemenu);
    $p->display();

    $f = new ValidatingForm();
    $f->push(new Table());
    $f->add(new HiddenTpl("itemid"),                        array("value" => $id,                     "hide" => True));

    $f->add(
        new TrFormElement(_T("Label", "imaging"), new InputTpl("image_label")),
        array("value" => $label)
    );
    $f->add(
        new TrFormElement(_T("Description", "imaging"), new InputTpl("image_description")),
        array("value" => $desc)
    );

    $post_installs = xmlrpc_getAllPostInstallScripts($location);
    $post_installs = $post_installs[1];

    $elements = array();
    $elementsVal = array();
    foreach ($post_installs as $ps) {
        $elements[$ps['imaging_uuid']] = $ps['default_name'].' / '.$ps['default_desc'];
        $elementsVal[$ps['imaging_uuid']] = $ps['imaging_uuid'];
    }

    $postInstall = new SelectItem("post_install");
    $postInstall->setElements($elements);
    $postInstall->setElementsVal($elementsVal);
    $postInstall->setSelected($master['post_install_script']['imaging_uuid']);
    $f->add(
        new TrFormElement(_T("Post-installation script", "imaging"), $postInstall)
    );

    /*$f->add(
        new TrFormElement(_T("In default bootmenu", "imaging"),
        new CheckboxTpl("bootmenu")),
        array("value" => $in_bootmenu)
    );*/
    $f->pop();
    $f->addButton("bvalid", _T("Validate"));
    $f->pop();
    $f->display();
} else {
    $item_uuid = $_POST['itemid'];
    $loc_uuid = getCurrentLocation();

    $params = array();
    $params['name'] = $_POST['image_label'];
    $params['desc'] = $_POST['image_description'];
    $params['post_install_script'] = $_POST['post_install'];
    $params['is_master'] = True;

    $ret = xmlrpc_editImageLocation($item_uuid, $loc_uuid, $params);

    if ($ret[0] and !isXMLRPCError()) {
        $str = sprintf(_T("Master <strong>%s</strong> modified with success", "imaging"), $label);
        new NotifyWidgetSuccess($str);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
    } elseif ($ret[0]) {
        header("Location: " . urlStrRedirect("imaging/manage/master"));
    } else {
        new NotifyWidgetFailure($ret[1]);
        header("Location: " . urlStrRedirect("imaging/manage/master"));
    }

}

?>
