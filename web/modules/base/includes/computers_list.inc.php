<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
 * (c) 2015-2017 Siveo, http://http://www.siveo.net
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
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("includes/xmlrpc.inc.php");

class EmptyActionItem1 extends ActionItem {

    function EmptyActionItem() {
        //$this->classCss='empty';
        $this->desc='';
    }

    function display($param = null, $extraParams = Array()) {
        echo "<li class=\"" . $this->classCss . "\">";
        echo "<a title=\"" . $this->desc . "\" href=\"#\" ";
        echo "onclick=\"return false;\">&nbsp;</a>";
        print "</li>";
    }
    function setClassCss($name) {
        $this->classCss = $name;
    }
    function setDescription($name) {
        $this->desc = $name;
    }
    function getDescription() {
        echo '$this->desc';
    }
}

function list_computers($names,
                        $filter, 
                        $count = 0, 
                        $delete_computer = false, 
                        $remove_from_result = false, 
                        $is_group = false, 
                        $msc_can_download_file = false, 
                        $msc_vnc_show_icon = false,
                        $groupinfodeploy = -1,
                        $login = "") {
    /* $pull_list is an array with UUIDs of pull machines */
    $pull_list = (in_array("pulse2", $_SESSION["modulesList"])) ? get_pull_targets() : array();

    $emptyAction = new EmptyActionItem();

    $inventAction = new ActionItem(_("Inventory"),"invtabs","inventory","inventory", "base", "computers");
    $glpiAction = new ActionItem(_("GLPI Inventory"),"glpitabs","inventory","inventory", "base", "computers");
    $logAction = new ActionItem(_("detaildeploy"),"viewlogs","logfile","computer", "xmppmaster", "xmppmaster");
    $mscAction = new ActionItem(_("Software deployment"),"msctabs","install","computer", "base", "computers");
    if (in_array("xmppmaster", $_SESSION["supportModList"])) {
        $logNoAction = new EmptyActionItem1(_("Read log"),"msctabs","logfileg","computer", "base", "computers", "tablogs");
        $mscNoAction = new EmptyActionItem1(_("Software deployment"),"msctabs","installg","computer", "base", "computers");
        $inventconsole = new ActionItem(_("xmppconsole"),"consolecomputerxmpp","install","computers", "xmppmaster", "xmppmaster");
        $inventnoconsole = new EmptyActionItem1(_("xmppconsole"),"consolecomputerxmpp","installg","computers","xmppmaster", "xmppmaster");
        $actionConsole = array();
    }
    $imgAction = new ActionItem(_("Imaging management"),"imgtabs","imaging","computer", "base", "computers");
    $downloadFileAction = new ActionItem(_("Download file"), "download_file", "download", "computer", "base", "computers");
    $extticketAction = new ActionItem(_("extTicket issue"), "extticketcreate", "extticket", "computer", "base", "computers");
    $vncClientAction = new ActionPopupItem(_("Remote control"), "vnc_client", "vncclient", "computer", "base", "computers");
    $profileAction = new ActionItem(_("Show Profile"), "computersgroupedit", "logfile","computer", "base", "computers");

    // with check presence xmpp
    $vncClientActiongriser = new EmptyActionItem1(_("Remote control"), "vnc_client", "vncclientg", "computer", "base", "computers");

    $actionInventory = array();
    $action_logs_msc = array();
    $action_deploy_msc = array();
    $actionImaging = array();
    $actionDownload = array();
    $actionVncClient = array();
    $actionExtTicket = array();
    $actionProfile = array();

    $params = array();
    $cssClasses = array();

    $headers = getComputersListHeaders();
    $columns = array();
    foreach ($headers as $header) {
        $columns[$header[0]] = array();
    }

    function getUUID($machine) { return $machine['objectUUID']; }
    
    $uuids = array_map("getUUID", $names);

    $countmachine=0;
    $presencemachinexmpp = False;


    foreach($names as $value) {
        $presencemachinexmpp = True;
        if (in_array("xmppmaster", $_SESSION["supportModList"])) {
            // determine presence machine xmpp
            if(isset($uuids[$countmachine])){
                $presencemachinexmpp = xmlrpc_getPresenceuuid( $uuids[$countmachine]);
                $countmachine++;
            }
        }

        //$presencemachinexmpp ? $value['presencemachinexmpp'] = "1" : $value['presencemachinexmpp'] = "0";

        
        $cssClasses[] = (in_array($value['objectUUID'], $pull_list)) ? 'machinePull' : 'machineName';

        foreach ($headers as $header) {
            if (!empty($value[$header[0]])) {
                $v = $value[$header[0]];
            } else {
                $v = '';
            }
            $columns[$header[0]][]= $v;
        }
        if (isset($filter['gid']))
	        $value['gid'] = $filter['gid'];

        if (in_array("inventory", $_SESSION["supportModList"])) {
            $actionInventory[] = $inventAction;
        } else {
            $actionInventory[] = $glpiAction;
        }

        if ( in_array("xmppmaster", $_SESSION["supportModList"])  ) {
            if ($groupinfodeploy == -1  ){
                $action_logs_msc[]   = $logNoAction;
            }
            else{
                $action_logs_msc[]   = $logAction;
            }
            if ( $presencemachinexmpp ){
                $action_deploy_msc[] = $mscAction;
                $actionConsole[] = $inventconsole;
            }
            else{
                $action_deploy_msc[] = $mscNoAction;
                //$actionConsole[] = $emptyAction; // action no console xmpp (icone or not icone)
                $actionConsole[] = $inventnoconsole;
            }
        }
        else{
            if ( in_array("msc", $_SESSION["supportModList"])  ) {
                $action_deploy_msc[] = $mscAction;
                $action_logs_msc[]   = $logAction;
            }
         }


        if (in_array("imaging", $_SESSION["supportModList"])) {
            $actionImaging[] = $imgAction;
        }
	
        if (in_array("extticket", $_SESSION["supportModList"])) {
            $actionExtTicket[] = $extticketAction;
        }

        if ($msc_can_download_file) {
            $actionDownload[] = $downloadFileAction;
        }
        if (in_array("guacamole", $_SESSION["supportModList"]) && in_array("xmppmaster", $_SESSION["supportModList"])) {
            if ($presencemachinexmpp){
                $actionVncClient[] = $vncClientAction;
            }else
            {//show icone vnc griser jfk
                $actionVncClient[] = $vncClientActiongriser;
            }
        }else
        if ($msc_vnc_show_icon) {
            $actionVncClient[] = $vncClientAction;
        }
        $params[] = $value;
    }
    foreach($params as &$element ){

    if ( $groupinfodeploy != -1){
        $element['gr_cmd_id']= $groupinfodeploy;
    }
    if ( $login != ""){
        $element['gr_login']= $login;
    }

        if (in_array("guacamole", $_SESSION["supportModList"])) {
            $element['vnctype'] = "guacamole";
        }
        else{
            if (web_def_use_no_vnc()==1){
                $element['vnctype']="novnc";
            }
            else{
                $element['vnctype']="appletjava";
            }
        }
    }
    if (isset($filter['location'])) {
        $filter = $filter['hostname'] . '##'. $filter['location'];
    } else {
        $filter = $filter['hostname'] . '##';
    }

    $n = null;
    if ($count) {
        foreach ($headers as $header) {
            if ($n == null) {
                if (in_array("glpi", $_SESSION["modulesList"])) {
                    $n = new OptimizedListInfos($columns[$header[0]], _T($header[1], 'glpi'));
                }
                else {
                    $n = new OptimizedListInfos($columns[$header[0]], _($header[1]));
                }
            } else {
                if (in_array("glpi", $_SESSION["modulesList"])) {
                    $n->addExtraInfo($columns[$header[0]], _T($header[1], 'glpi'));
                }
                else {
                    $n->addExtraInfo($columns[$header[0]], _($header[1]));
                }
            }
        }
        $n->setItemCount($count);
        $n->setNavBar(new AjaxNavBar($count, $filter));
        $n->start = 0;
        $n->end = $count - 1;
    } else {
        foreach ($headers as $header) {
            if ($n == null) {
                $n = new ListInfos($columns[$header[0]], _($header[1]));
            } else {
                $n->addExtraInfo($columns[$header[0]], _($header[1]));
            }
        }
        $n->setNavBar(new AjaxNavBar(count($columns[$headers[0][0]]), $filter));
    }

    $n->setName(_("Computers list"));
    $n->setParamInfo($params);
    //$n->setCssClass("machineName");
    $n->setMainActionClasses($cssClasses);
    
    if (in_array("xmppmaster", $_SESSION["supportModList"]) &&  $groupinfodeploy == -1  ){
        $n->addActionItemArray($actionInventory);
    }
    
    if ($msc_can_download_file) {
        $n->addActionItemArray($actionDownload);
    };
    if (in_array("extticket", $_SESSION["supportModList"])) {
        $n->addActionItemArray($actionExtTicket);
    }
    if (in_array("xmppmaster", $_SESSION["supportModList"]) &&  $groupinfodeploy == -1  ){
        if (in_array("backuppc", $_SESSION["supportModList"]))
            $n->addActionItem(new ActionItem(_("Backup status"),"hostStatus","backuppc","backuppc", "backuppc", "backuppc"));

        if ($msc_vnc_show_icon) {
            $n->addActionItemArray($actionVncClient);
        };
    }
    /*if (in_array("dyngroup", $_SESSION["modulesList"])) {
        $n->addActionItemArray($actionProfile);
    }*/

    if (in_array("msc", $_SESSION["supportModList"]) || in_array("xmppmaster", $_SESSION["supportModList"]) ) {
        if (in_array("xmppmaster", $_SESSION["supportModList"]) &&  $groupinfodeploy == -1  ){
            $n->addActionItemArray($action_deploy_msc);
        }else{
            $n->addActionItemArray($action_logs_msc);
        }
    }

    if (in_array("imaging", $_SESSION["supportModList"])) {
        if (in_array("xmppmaster", $_SESSION["supportModList"]) &&  $groupinfodeploy == -1  ){
            $n->addActionItemArray($actionImaging);
        }
    }
    if (isExpertMode()){
        if (in_array("xmppmaster", $_SESSION["supportModList"]) ){
            $n->addActionItemArray($actionConsole);
        }
    }
    if (in_array("xmppmaster", $_SESSION["supportModList"]) &&  $groupinfodeploy == -1  ){
        if ($delete_computer && canDelComputer()) {
            // set popup window to 400px width
            $n->addActionItem(new ActionPopupItem(_("Delete computer"),"delete","delete","computer", "base", "computers", null, 400));
        }
        if ($remove_from_result) {
            $n->addActionItem(new ActionPopupItem(_("Remove machine from group"),"remove_machine","remove_machine","name", "base", "computers"));
        }
    }
    $n->display();
}

?>
