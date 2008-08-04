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

$p_api_id = $_GET['p_api'];
$pid = base64_decode($_GET['pid']);

if (isset($_POST["bassoc"])) {
    $cbx = array();
    foreach ($_POST as $post => $v) {
        if (preg_match("/cbx_/", $post) > 0) {
            $cbx[] = preg_replace("/cbx_/", "", $post);
        }
    }
    $ret = associatePackages($p_api_id, $pid, $cbx);
    if (!isXMLRPCError() and $ret and $ret != -1) {
        if ($ret[0]) {
            new NotifyWidgetSuccess(sprintf(_T("Files succesfully associated with package %s", "pkgs"), $pid));
            header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('location'=>$p_api_id))); # TODO add params to go on the good p_api
        } else {
            new NotifyWidgetFailure($ret[1]);
        }
    } else {
        new NotifyWidgetFailure(_T("Failed to associate files", "pkgs"));
    }
}

# temporary files
$files = getTemporaryFiles($p_api_id);

$p = new PageGenerator(sprintf(_T("Associate files to package %s", "pkgs"), $pid));
$p->setSideMenu($sidemenu);
$p->display();


$f = new ValidatingForm();
$f->push(new Table());

foreach ($files as $p) {
    # TODO use $p[1] to put a different style to directories
    $f->add(
        new TrFormElement($p[0], new CheckboxTpl("cbx_".$p[0])),
        array()
    );
}
$hidden = new HiddenTpl("p_api");
$f->add($hidden, array("value" => $p_api_id, "hide" => True));
$hidden = new HiddenTpl("pid");
$f->add($hidden, array("value" => $pid, "hide" => True));

$f->pop();
$f->addButton("bassoc", _T("Associate", 'pkgs'));
$f->display();


?>
