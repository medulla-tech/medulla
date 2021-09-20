<?php
/**
 * (c) 2018 Siveo, http://siveo.net
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

//Import the functions and classes needed
require("graph/navbar.inc.php");
require("modules/pkgs/pkgs/localSidebar.php");
require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/pkgs/includes/class.php");

$p = new PageGenerator(_T("Edit a Rule",'pkgs'));
$p->setSideMenu($sidemenu);
$p->display();

if(isset($_POST['bconfirm']))
{
  foreach($_POST as $key=>$value)
  {
    if($key != 'rule_order')
      $_POST[$key] = addslashes($value);
  }
  add_extension($_POST);
  new NotifyWidgetSuccess(sprintf(_T("The rule %s has been modified", "pkgs"),$_POST['rule_name']));
}

if(isset($_GET['id']))
{
  $id = (int)$_GET['id'];
  $rule = get_extension($id);
  $f = new ValidatingForm(array("id" => "add-rule"));

  $f->push(new Table());

  $hiddenfields = array(

      array("rule_order", ["value" => $rule['rule_order'], 'hide' => True]),
      array("id", ["value" => $rule['id'], 'hide' => True]),
      array("magic_command", ["value" => stripslashes($rule['magic_command']), 'hide' => True]),
  );

  foreach ($hiddenfields as $p) {
      $f->add(new HiddenTpl($p[0]), $p[1]);
  }

  $fields = array(
      array("rule_name", _T("Rule Name", "pkgs"), ["required" => True, 'placeholder' => _T('Rule Name', 'pkgs'), 'value'=>stripslashes($rule['rule_name'])]),
      array('description', _T("Description", "pkgs"), ['placeholder' => _T('Description', 'pkgs'), 'value'=>stripslashes($rule['description'])]),
      array("name", _T("Search in Name", "pkgs"), ['placeholder' => _T('File Name', 'pkgs'), 'value'=>stripslashes($rule['name'])]),
      array("extension", _T("Search in Extension", "pkgs"), ['placeholder' => _T('File Extension', 'pkgs'), 'value'=>stripslashes($rule['extension'])]),
      array("bang", _T("Search in Bang", "pkgs"), ['placeholder' => _T('Element in Bang', 'pkgs'), 'value'=>stripslashes($rule['bang'])]),
      array("file", _T("Search into File command", "pkgs"), ['placeholder' => _T('Element in File Result', 'pkgs'), 'value'=>stripslashes($rule['file'])]),
      array("strings", _T("Search into Strings command", "pkgs"), ['placeholder' => _T('Element in Strings Result', 'pkgs'), 'value'=>stripslashes($rule['strings'])]),
  );

  foreach ($fields as $p) {
      $f->add(
              new TrFormElement($p[1], new InputTpl($p[0])), $p[2]
      );
  }

  $f->add(new TrFormElement("Install Proposition", new TextareaTplArray(["value"=>stripslashes($rule['proposition']),"name"=>"proposition", "required"=>true, "cols"=>"39px", "rows"=>1, 'style'=>"width:auto; height:auto;"])));
  $f->addValidateButton("bconfirm", _T("Add", "pkgs"));
  $f->display(); // display the form
}
else{
  header("Location: " . urlStrRedirect("pkgs/pkgs/rulesList"));
}
?>
