<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id: edit.php 433 2008-05-16 12:29:42Z cdelfosse $
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

require_once("modules/pkgs/includes/xmlrpc.php");

$package = array();

if (isset($_POST["bcreate"])) {
    $p_api_id = $_POST['p_api'];
    foreach (array('id', 'label', 'version', 'description') as $post) {
        $package[$post] = $_POST[$post];
    }
    foreach (array('command') as $post) {
        $package[$post] = array('name'=>$_POST[$post.'name'], 'command'=>$_POST[$post.'cmd']);
    }
    $ret = putPackageDetail($p_api_id, $package);
    if (!isXMLRPCError() and $ret) {
        new NotifyWidgetSuccess(_T("Package successfully added"));
        header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('location'=>$p_api_id))); # TODO add params to go on the good p_api
    } else {
        new NotifyWidgetFailure(_T("Package failed to save"));
    }
}
$p_api_id = base64_decode($_GET['p_api']);


//title differ with action
if ($_GET["action"]=="add") {
    $title = _("Add package");
    $activeItem = "add";
    $formElt = new DomainInputTpl("id");
    
    $res = getUserPackageApi();
    $list_val = $list = array();
    if (!isset($_SESSION['PACKAGEAPI'])) { $_SESSION['PACKAGEAPI'] = array(); }
    foreach ($res as $mirror) {
        $list_val[$mirror['uuid']] = base64_encode($mirror['uuid']);
        $list[$mirror['uuid']] = $mirror['mountpoint'];
        $_SESSION['PACKAGEAPI'][$mirror['uuid']] = $mirror;
    }
    $selectpapi = new SelectItem('p_api');
    $selectpapi->setElements($list);
    $selectpapi->setElementsVal($list_val);
} else {
    $title = _("Edit package");
    $activeItem = "index";
    # get existing package
    $pid = base64_decode($_GET['pid']);
    $package = getPackageDetail($p_api_id, $pid);
    $formElt = new HiddenTpl("id");
    
    $selectpapi = new HiddenTpl('p_api');
}

$p = new PageGenerator($title);
$sidemenu->forceActiveItem($activeItem);
$p->setSideMenu($sidemenu);
$p->display();


$f = new ValidatingForm();
$f->push(new Table());

$f->add(
        new TrFormElement(_T("Package API"), $selectpapi),
        array("value" => $p_api_id, "required" => True)
        );

$f->add(
        new TrFormElement(_T("Package Id"), $formElt),
        array("value" => $package['id'], "required" => True)
        );

$fields = array(
    array("label", _T("Package label", "pkgs")),
    array("version", _T("Package version", "pkgs")),
    array('description', _T("Description", "pkgs")),
);

$cmds = array(
    array('command', _T('Command\'s name : ', 'pkgs'), _T('Command : ', 'pkgs'))/*,
    array('installInit', _T('', 'pkgs')),
    array('preCommand', _T('', 'pkgs')),
    array('postCommandFailure', _T('', 'pkgs')),
    array('postCommandSuccess', _T('', 'pkgs'))*/
);

foreach ($fields as $p) {
    $f->add(
        new TrFormElement($p[1], new InputTpl($p[0])),
        array("value" => $package[$p[0]])
    );
}

foreach ($cmds as $p) {
    $f->add(
        new TrFormElement($p[1], new InputTpl($p[0].'name')),
        array("value" => $package[$p[0]]['name'])
    );
    $f->add(
        new TrFormElement($p[2], new InputTpl($p[0].'cmd')),
        array("value" => $package[$p[0]]['command'])
    );
}

$f->pop();
$f->addValidateButton("bcreate");
$f->display();


?>
