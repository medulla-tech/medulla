<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id: groups-xmlrpc.inc.php 382 2008-03-03 15:13:24Z cedric $
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
?>
<?php

function get_last_log_user($user) {
    $param = array(0,1,0,0,"User",0,0,$user,0);
    
    return xmlCall("base.getLog", $param);
}

function get_log_by_id($id) {
    
    $listlog = xmlCall("base.getLogById", $id);
        
    return $listlog;
}

function get_log_filter($start,$end,$module,$filter,$filtertype,$startdate,$enddate) {
    $object=0;
    $user=0;
    $action=0;
    $type=0;
    if ($module=="all") {
        $module=0;
    }
    
    switch ($filtertype) {
        case "object":
            $object=$filter;
            break;
        case "user":
            $user=$filter;
            break;
        case "action":
            $action=$filter;
            break;
        case "type":
            $type=$filter;
            break;
    }    

    $param = array((int) $start, (int) $end,$module,$user,$type,$startdate,$enddate,$object,$action);
        
    $listlog = xmlCall("base.getLog", $param);
    return  $listlog;
}

function get_log_user_filter($start,$end,$module,$user,$filter,$filtertype,$startdate,$enddate) {
    $action=0;
    $type=0;
    $module=0;
    
    switch ($filtertype) {
    case "object":
        $object=$filter;
        break;
    case "action":
        $action=$filter;
        break;
    case "type":
        $type=$filter;
        break;
    }    

    $param = array((int) $start, (int) $end,$module,0,$type,$startdate,$enddate,$user,$action);
    
    $listlog = xmlCall("base.getLog", $param);
    return  $listlog;
}

function get_action_type($action,$type){
    return xmlCall("base.getActionType",array($action,$type));   
}

function has_audit_working() {
    if (!isset($_SESSION["hasAuditManagerWorking"])) {
        $_SESSION["hasAuditManagerWorking"] = xmlCall("base.hasAuditWorking");
    }
    return $_SESSION["hasAuditManagerWorking"];
}
        
?>
