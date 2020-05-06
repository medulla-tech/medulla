<?php
/*
 * (c) 2015-2020 Siveo, http://www.siveo.net
 *
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

if(isset($_POST['jid'], $_POST['switch'])){
  if (!isset($_POST["switchsecurity"])) {
      new NotifyWidgetFailure(_("You have to check the box <b>\"I am aware that this disable/enable a relay forcing a <em><b>reconfiguration of all the machines</b></em> managed by the cluster."));
      header("Location: " . urlStrRedirect("base/computers/xmppRelaysList"));
      exit;
  }
  else{
    $result = xmlrpc_change_relay_switch($_POST['jid'], $_POST['switch']);

    new NotifyWidgetSuccess(_('The relay '.htmlentities($_POST['jid']).' has been switched to '.htmlentities($_POST['switch'])));
    header("Location: " . urlStrRedirect("base/computers/xmppRelaysList"));
    exit;
  }
}
if (isset($_GET['switch']))
{
  $title = ($_GET['switch'] == 1) ? _T("Switch Off the relay", "xmppmaster") : _T("Switch On the relay", "xmppmaster");

  $f = new PopupForm($title. ' '.$_GET['jid']);
  $f->push(new Table());


  $hiddenjid = new HiddenTpl("jid");
  $hiddenswitch = new HiddenTpl("switch");
  $f->add($hiddenjid, array("value" => $_GET['jid'], "hide" => True));
  $switch = ($_GET['switch'] == 1) ? 0 : 1;
  $f->add($hiddenswitch, array("value" => $switch, "hide" => True));
  $f->pop();
  $tr = new TrFormElement(_("I am aware that this disable/enable a relay forcing a <em><b>reconfiguration of all the machines</b></em> managed by the cluster.<br />Check this box if it is what you want."), new CheckBoxTpl("switchsecurity"), array("value" => ''));
  $tr->setFirstColWidth('100%');
  $f->add($tr);
  //new NotifyWidgetFailure(_("You have to check the box <b>\"I am aware that all related images (non-master) will be deleted\"</b> if you want to remove this computer."));
  $f->addValidateButton("bconfirm");
  $f->addCancelButton("bback");
  $f->display();
}
?>
