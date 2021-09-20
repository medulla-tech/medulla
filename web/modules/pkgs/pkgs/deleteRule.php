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
require_once("modules/pkgs/includes/xmlrpc.php");

if(isset($_GET['id']))
{
  $id = (int)$_GET['id'];
  $rule = get_extension([$id]);
  if(isset($rule['rule_name']))
  {
    $params['name'] = $rule['rule_name'];
    if(isset($_POST['bconfirm']) && $_POST['bconfirm'])
    {
      delete_extension($id);
      header('location: '.urlStrRedirect("pkgs/pkgs/rulesList", ["success"=>1, "name"=>$rule['rule_name']]));
    }
    else{
      $title = _T(sprintf("Are you sure to delete the rule %s ?", $rule["rule_name"]));
      $f = new PopupForm($title, 'startPopupForm');
      $f->addValidateButton("bconfirm");
      $f->addCancelButton("bback");
      $f->display();
    }
  }
}

?>
