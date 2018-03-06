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

//require_once("modules/xmppmaster/includes/xmlrpc.php");
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

        $uuid  = isset($_GET['objectUUID']) ? $_GET['objectUUID'] : ( isset($_POST['objectUUID']) ? $_POST['objectUUID'] : "");
        $machine  = isset($_POST['Machine']) ? $_POST['Machine'] : xmlrpc_getjidMachinefromuuid( $uuid );
        $ma = xmlrpc_getMachinefromjid($machine);

        $result = xmlrpc_remotefileeditaction($ma['jid'], array('action' => 'listconfigfile'));

        print_r($result['result'] );
        $count = count($result['result']);

        $param = array(
            "cn" => $_GET['cn'],
            "type" => $_GET['type'],
            "objectUUID" => $_GET['objectUUID'],
            "entity" => $_GET['entity'],
            "owner" => $_GET['owner'],
            "user" => $_GET['user'],
            "os" => $_GET['os']
        );

        $emptyAction = new EmptyActionItem();

        $actionEdit = array();

        $removeconf =  new ActionItem(_("Edit configs files"), 
                                        "remoteeditorconfigurationlist",
                                        "edit",
                                        "computers",
                                        "xmppmaster",
                                        "xmppmaster");
        $params = array();
        // $result['result'] is list name conf file
        foreach($result['result'] as $fichierconf){
            $param['name'] = $fichierconf;
            $params[] = $param;
            $actionEdit[] = $removeconf;
        }
        $n = new ListInfos($result['result'], _T("Conf File name", "xmppmaster"));
        $n->first_elt_padding = 1;
        $n->disableFirstColumnActionLink();
        $n->setParamInfo($params);
        $n->addActionItemArray($actionEdit);
        $n->display();

?>
