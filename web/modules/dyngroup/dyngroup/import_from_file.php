<?php
/**
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require("modules/dyngroup/includes/groups.inc.php");
require_once("modules/dyngroup/includes/querymanager_xmlrpc.php");

$groupname = quickGet('groupname');
$visibility = quickGet('visible');
if (!isset($visibility) || $visibility == '') {
    $visibility = 'hidden';
}
$elementare = quickGet('elementare');
# check group name
if (isset($groupname) && $groupname != '' && !xmlrpc_group_name_exists($groupname)) {
    $group = new Group();
    $group->create($groupname, ($visibility == 'visible'));
    $content = file($_FILES['importfile']['tmp_name']);
    $content = array_map('chop', $content);
    $group->importMembers($elementare, $content);
    new NotifyWidgetSuccess(_T("Group successfully created", "dyngroup"));
    header("Location: " . urlStrRedirect("base/computers/display", array('gid'=>$group->id)));
} elseif (xmlrpc_group_name_exists($groupname)) {
    new NotifyWidgetFailure(sprintf(_T("A group already exists with name '%s'", "dyngroup"), $groupname));
}

$f = new ValidatingForm(array('enctype'=>"multipart/form-data"));
$f->push(new Table());

$f->add( new TrFormElement(_T("Group name", "dyngroup"), new InputTpl("groupname")), array("required" => True, "value"=>$groupname));

$r = new RadioTpl('visible');
$r->setChoices(array(_T('Yes', 'dyngroup'), _T('No', 'dyngroup')));
$r->setValues(array('visible', 'hidden'));
$r->setSelected($visibility);
$f->add( new TrFormElement(_T("Add shortcut", "dyngroup"), $r), array("required" => True));

$f->add( new TrFormElement(_T("Select the file you want to import", "dyngroup"), new FileTpl('importfile')), array("required" => True));

$a = getPossiblesCriterionsInMainModule();
$r = new RadioTpl('elementare');
$r->setChoices($a);
$r->setValues($a);
if (!isset($elementare) || $elementare == '') {
    $elementare = $a[0];
}
$r->setSelected($elementare);
$f->add( new TrFormElement(_T("Select what is inside the file", "dyngroup"), $r), array("required" => True));

$f->pop();

$f->addValidateButton("bimport");

$f->display();


?>

