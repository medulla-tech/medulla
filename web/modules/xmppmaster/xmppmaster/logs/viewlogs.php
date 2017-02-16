<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
 
require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
extract($_GET);
$p = new PageGenerator(_T("View log deploy"." ".$hostname, 'xmppmaster'));
$p->setSideMenu($sidemenu);
$p->display();



?> 
 
<?



// if ( ! isset($sessionxmpp))
// {
    //recupere information deploie. for cmn_id
    $info = xmlrpc_getdeployfromcommandid($cmd_id);
    if ($info['len'] == 0)
    {
        echo "Wait for the deployment " . $cmd_id;
    }
    else{
        $sessionxmpp=$info['objectdeploy'][0]['sessionid'];
        $uuid=$info['objectdeploy'][0]['inventoryuuid'];
        $state=$info['objectdeploy'][0]['state'];
        $start=get_object_vars($info['objectdeploy'][0]['start'])['timestamp'];
        $result=$info['objectdeploy'][0]['result'];
        $host=$info['objectdeploy'][0]['host'];
        $jidmachine=$info['objectdeploy'][0]['jidmachine'];
        $jid_relay=$info['objectdeploy'][0]['jid_relay'];
        print_r($start );
        
        echo date("Y-m-d H:i:s", $start);

        echo "deployment " . $cmd_id;
        
        
        print_r(xmlrpc_getlinelogssession($sessionxmpp));
    }


// cmd_id associe a $_SESSION['login']
echo "<pre>";
print_r($result);
// print_r($info);
echo "<pre>";
?>

<!-- this page reload automatic -->

<form id="formpage" action="<? echo $_SERVER['PHP_SELF']; ?>" METHODE="GET" >
    <input type="hidden" name="module" value ="<? echo $module; ?>" >
    <input type="hidden" name="submod" value ="<? echo $submod; ?>" >
    <input type="hidden" name="action" value ="<? echo $action; ?>" >
    <input type="hidden" name="uuid" value ="<? echo $uuid; ?>" >
    <input type="hidden" name="hostname" value ="<? echo $hostname; ?>" >
    <input type="hidden" name="gid" value ="<? echo $gid; ?>" >
    <input type="hidden" name="cmd_id" value ="<? echo $cmd_id; ?>" >
    <input type="hidden" name="login" value ="<? echo $login; ?>" >
    <input type="text" name="tab" value ="<? echo $tab; ?>" >
</form>


<script type="text/javascript">
    setTimeout(refresh, 5000);
    function  refresh(){
 jQuery( "#formpage" ).submit();
    }
</script>
