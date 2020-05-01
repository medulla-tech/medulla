<?php
/*
 * (c) 2016-2018 Siveo, http://www.siveo.net
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
 * GNU General Public License for more details.<?php
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *  file xmppmaster/ajaxxmppremoteaction.php
 */
?>
<?php
    header('Content-type: application/json');

    require_once("../includes/xmlrpc.php");
    require_once("../../../includes/config.inc.php");
    require_once("../../../includes/i18n.inc.php");
    require_once("../../../includes/acl.inc.php");
    require_once("../../../includes/session.inc.php");
    extract($_POST);

    switch($action){
        case "loadfile":
            $data = array('action' => $action, 'file' => $file);
            $result = xmlrpc_remotefileeditaction($machine, $data);
            //md5($str)
            $result['action'] = "loadfile";
            $result['md5'] = md5($result['result']);
            $result['file'] = $file;
            echo json_encode($result);
            break;
        case "save":
            $data = array('action' => $action, 'file' => $file, 'content' => $content);
            $result = xmlrpc_remotefileeditaction($machine, $data);
            echo json_encode($data);
            break;
    }

?>
