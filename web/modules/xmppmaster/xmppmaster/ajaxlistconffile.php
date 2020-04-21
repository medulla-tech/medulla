<?php
/**
 *  (c) 2015-2017 Siveo, http://www.siveo.net
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
 * file ajaxFiltercustom.php
 */

require_once("modules/xmppmaster/includes/xmlrpc.php");
?>
<style>
a.info{
    position:relative;
    z-index:24;
    color:#000;
    text-decoration:none
}

a.info:hover{
    z-index:25;
    background-color:#FFF
}

a.info span{
    display: none
}

a.info:hover span{
    display:block;
    position:absolute;
    top:2em; left:2em; width:25em;
    border:1px solid #000;
    background-color:#E0FFFF;
    color:#000;
    text-align: justify;
    font-weight:none;
    padding:5px;
}
</style>

<?php
$jid = (isset($_GET['jid'])) ? $_GET['jid'] : '';
$machine =(isset($_GET['hostname'])) ? $_GET['hostname'] : "";

$result = xmlrpc_remotefileeditaction($jid, array('action' => 'listconfigfile'));


$editaction =  new ActionItem(_("Edit config files"),
                                "remoteeditorconfigurationlist",
                                "edit",
                                "computers",
                                "xmppmaster",
                                "xmppmaster");

$editactions = [];


$params = [];
if(isset($result['result'])){

foreach($result['result'] as $file){
  $params[] = ['jid'=> $jid, 'name'=>$file];
  $editactions[] = $editaction;
}

$n = new ListInfos($result['result'], _T("Config file", "xmppmaster"));
$n->first_elt_padding = 1;
$n->disableFirstColumnActionLink();
$n->setParamInfo($params);
$n->addActionItemArray($editactions);
$n->display();
}

if (isset($result['err'])){
    if ( $result['err'] == 'Timeout Error'){
        $msg = sprintf(_T("Sorry, the remote machine [%s] takes too much time to answer.", "xmppmaster"), $machine);
    }else{
        $msg = sprintf(_T("Error : %s", "xmppmaster"), $machine);
    }
        new NotifyWidgetFailure($msg);
}
?>
