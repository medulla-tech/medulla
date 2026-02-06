<?php
/**
 * (c) 2016-2022 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net/
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */

// file : modules/pkgs/includes/actions/action_comment.php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");
extract($_POST);
$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <!-- definie prefixe label -->
    <div style="display:none;">comment_</div>
    <h1 class="action"><?php echo _T("Add info in deployment log","pkgs"); ?></h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="action" value="action_comment" />
        <?php

        $lab =  (isset($actionlabel))? $actionlabel : uniqid();
        ?>
        <table id="tableToggle">
        <?php
        echo'
           <tr class="toggleable">
                <th width="16%">'._T("Step label :","pkgs").'</th>
                <th width="25%">
                    <input type="text" name="actionlabel" value="'.$lab.'"/>
                <th></th>
                <th></th>
            </tr>
            <tr>
             ';
            echo '<td width="16%">
                   '._T("Information","pkgs").'
                </td>
                <td width="25%">
                <textarea name="comment">';

                echo (isset($comment)) ? $comment : _T("Your log comments !","pkgs");

    /*
                echo (isset($comment)) ? $comment : "JID AMR : @@@JID_MASTER@@@[@@@IP_MASTER@@@]
JID ARS : @@@JID_RELAYSERVER@@@[@@@IP_RELAYSERVER@@@]
JID AM  : @@@JID_MACHINE@@@[@@@IP_MACHINE@@@]
Package name : @@@PACKAGE_NAME@@@
Deployement session id : @@@SESSION_ID@@@
Hostname : @@@HOSTNAME@@@
Python implentation : @@@PYTHON_IMPLEMENTATION@@@
Machine architecture : @@@ARCHI_MACHINE@@@
OS family : @@@OS_FAMILY@@@
OS complete name :   @@@OS_COMPLET_NAME@@@
Package UUID : @@@UUID_PACKAGE@@@
Package folder : @@@PACKAGE_DIRECTORY_ABS_MACHINE@@@
List of network interfaces :@@@LIST_INTERFACE_NET@@@
List of MAC addresses : @@@LIST_MAC_ADRESS@@@
list of IP addresses : @@@LIST_IP_ADRESS@@@
Machine IP address connected to XMPP : @@@IP_MACHINE_XMPP@@@
Machine tmp folder : @@@TMP_DIR@@@
" ;*/
                echo '</textarea>';
                echo'
                </td>';
        echo '
        <td></td><td></td>
            </tr>
        </table>';
        ?>

    </div>

    <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
