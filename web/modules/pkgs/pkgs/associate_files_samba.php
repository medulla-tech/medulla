<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require_once("modules/pkgs/includes/xmlrpc.php");

$package = array();

$p_api_id = base64_decode(quickGet('p_api'));
$pid = base64_decode(quickGet('pid'));
$plabel = base64_decode(quickGet('plabel'));
$pversion = base64_decode(quickGet('pversion'));
$mode = quickGet('mode');
$level = 0;
if ($mode == "creation") { $level = 1; }

if (isset($_POST["bassoc"]) || isset($_POST["bempty"])) {
    $cbx = array();
    if (!isset($_POST["bempty"])) {
        /* Get selected directory only if the user don't want to create an
           empty package */
        /* FIXME: maybe this cbx stuff is no more needed ? */
        foreach ($_POST as $post => $v) {
            if (preg_match("/cbx_/", $post) > 0) {
                $cbx[] = preg_replace("/cbx_/", "", $post);
            }
        }
        if (isset($_POST['rdo_files'])) {
            $cbx[] = $_POST['rdo_files'];
        }
    }
    $ret = associatePackages($p_api_id, $pid, $cbx, $level);
    if (!isXMLRPCError() and is_array($ret)) {
        if ($ret[0]) {
            $explain = '';
            if (count($ret) > 1) {
                $explain = sprintf(" : <br/>%s", implode("<br/>", $ret[1]));
            }
            new NotifyWidgetSuccess(sprintf(_T("Files successfully associated with package <b>%s (%s)</b>%s", "pkgs"), $plabel, $pversion, $explain));
            header("Location: " . urlStrRedirect("pkgs/pkgs/pending", array('location'=>base64_encode($p_api_id))));
        } else {
            $reason = '';
            if (count($ret) > 1) {
                $reason = sprintf(" : <br/>%s", $ret[1]);
            }
            new NotifyWidgetFailure(sprintf(_T("Failed to associate files%s", "pkgs"), $reason));
        }
    } else {
        new NotifyWidgetFailure(_T("Failed to associate files", "pkgs"));
    }
}

# temporary files
$files = getTemporaryFiles($p_api_id);

$p = new PageGenerator(sprintf(_T("Associate files to package <b>%s (%s)</b>", "pkgs"), $plabel, $pversion));
$p->setSideMenu($sidemenu);
$p->display();


$f = new ValidatingForm();
$f->push(new Table());

if ($mode == 'creation') {
    $r = new RadioTpl("rdo_files");
    $vals = array();
    $keys = array();
    foreach ($files as $fi) {
        if ($fi[1] == True) {
            $vals[] = $fi[0];
            $keys[] = $fi[0];
        }
    }
    $r->setValues($vals);
    $r->setChoices($keys);
    $f->add(new TrFormElement(_T("Select the directory you want for this package", "pkgs"), $r), array());
    $hidden = new HiddenTpl("mode");
    $f->add($hidden, array("value" => "creation", "hide" => True));
} else {
    foreach ($files as $fi) { # TODO use $p[1] to put a different style to directories
        $f->add(
            new TrFormElement($fi[0], new CheckboxTpl("cbx_".$fi[0])),
            array()
        );
    }
}
$hidden = new HiddenTpl("p_api");
$f->add($hidden, array("value" => $p_api_id, "hide" => True));
$hidden = new HiddenTpl("pid");
$f->add($hidden, array("value" => $pid, "hide" => True));
$hidden = new HiddenTpl("plabel");
$f->add($hidden, array("value" => $plabel, "hide" => True));
$hidden = new HiddenTpl("pversion");
$f->add($hidden, array("value" => $pversion, "hide" => True));

$f->pop();
$f->addButton("bassoc", _T("Associate", 'pkgs'));
$f->addButton('bempty', _T("Create an empty package", "pkgs"), "btnPrimary");
$f->display();


?>
