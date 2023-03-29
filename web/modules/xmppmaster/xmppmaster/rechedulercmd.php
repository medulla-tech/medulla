<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
 * (c) 2015-2017 Siveo, http://http://www.siveo.net
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
 *
 * file rechedulercmd.php   extend_command($cmd_id, $start_date, $end_date);
 */
require_once("modules/msc/includes/commands_xmlrpc.inc.php");
// affichedebugJFKJFK( $_GET,  "GET");
// affichedebugJFKJFK( $_POST,  "POST");
if (isset($_POST["bconfirm"])) {
   extract($_POST);
 extend_command($cmd_id, $start_date, $end_date);
//      if (isset($deployment_intervals) && isset($old_deployment_intervals)){
//          if ($start_date != $old_$start_date || $end_date != $old_end_date)
//          {
//
//          }
//      }

/*
     if (isset($deployment_intervals) && isset($old_deployment_intervals)){
         if ($deployment_intervals != $old_deployment_intervals)
         {

         }
     }*/
     header("Location: " . urlStrRedirect("xmppmaster/xmppmaster/index", array()));
   exit;
} else {
     extract($_GET);


     $f = new PopupForm("<h1>"._T('<h1>Reschedule this command', 'xmppmaster')."</h1>");

     // add parameter pour post

     $f->add(new HiddenTpl("cmd_id"),
             array("value" => $_GET['cmd_id'],
                   "hide" => True));
     $f->add(new textTpl("<br>"));
     $f->add(new HiddenTpl("cmd_id"),
             array("value" => $_GET['cmd_id'],
                   "hide" => True));
     $f->add(new textTpl("<br>"));

     $f->add(new TrFormElement(_T('deployment intervals', 'xmppmaster'), new InputTpl('deployment_intervals')), array("value" => isset($_GET['deployment_intervals']) ? $_GET['deployment_intervals'] : '', "required" => False));
     $f->add(new textTpl("<br>"));

$f->add(new TrFormElement(_T('Start date', 'xmppmaster'),
                          new DateTimeTpl('start_date')),array('value' => $start_date));
$f->add(new textTpl("<br>"));
$f->add(new TrFormElement(_T('End date', 'xmppmaster'),
                          new DateTimeTpl('end_date')),array('value' => $end_date));
$f->add(new textTpl("<br>"));
$f->addValidateButton("bconfirm");
$f->add(new textTpl("<br>"));
$f->addCancelButton("bback");
$f->display();
}

?>
