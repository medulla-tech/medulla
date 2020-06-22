<?php
/*
 * (c) 2020 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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
 */

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/html.inc.php");

function redirectToRelays(){
  $url = urlStrRedirect('xmppmaster/xmppmaster/xmppRelaysList');
  header('location: '.$url);
}


// Some information are missing
if(isset($_POST['jid'], $_POST['qa_relay_id']))
{
  $jid = htmlentities($_POST['jid']);
  $qa_relay_id = htmlentities($_POST['qa_relay_id']);
  $launch_relay_qa = (isset($_POST['launch_relay_qa'])) ? true : false;

  // Test if the relay is still online
  if(xmlrpc_is_relay_online($jid)){
      //$ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxqalaunched"), 'container', ['launch_relay_qa'=> $launch_relay_qa, 'jid'=>$jid, 'qa_relay_id'=>$qa_relay_id]);

    $p = new PageGenerator(_T("Relay Quick Leunched Action", 'xmppmaster'));
    $p->setSideMenu($sidemenu);
    $p->display();
    if($launch_relay_qa){

      $qa_relay = xmlrpc_get_relay_qa($_SESSION['login'], $qa_relay_id);
      $qa_launched = xmlrpc_add_qa_relay_launched($qa_relay_id, $_SESSION['login'], "", $jid);
      $uuid = uniqid();
      $datas = array(
        "command" => $qa_relay['script'],
        "machine" => $jid,
        "uidunique" => $uuid,
      );
      xmlrpc_runXmppCommand("plugin_asynchromeremoteshell", $jid, array($datas));
      $qa_result = xmlrpc_add_qa_relay_result($jid, $qa_launched['command_start'], $qa_relay_id, $qa_launched['id'], $uuid);

      usleep(250000);
      header('location: '.urlStrRedirect('xmppmaster/xmppmaster/qaresult', ['result_id'=>$qa_result['id'],
        'execution_date'=>$qa_launched['command_start'],
        'name'=>$qa_relay['name'],
        'description'=>$qa_relay['description']
      ]));
    }
  }//fi relay is online
  else{
    redirectToRelays();
  }
}
else if(isset($_GET['jid'])) {
  // Display all the quick action launched for this relay and user
  $jid = $_GET['jid'];

  $p = new PageGenerator(_T("QA Launched", 'xmppmaster'));
  $p->setSideMenu($sidemenu);
  $p->display();

  print "<br/><br/><br/>";
  $ajax = new AjaxFilter(urlStrRedirect("xmppmaster/xmppmaster/ajaxqalaunched"), "container", ['jid' => $jid]);
  $ajax->display();
  print "<br/><br/><br/>";
  $ajax->displayDivToUpdate();
}
else{
  redirectToRelays();
}
?>
