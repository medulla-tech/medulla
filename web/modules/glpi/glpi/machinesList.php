<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require("graph/navbar.inc.php");
require("modules/base/computers/localSidebar.php");
require("modules/glpi/includes/html.php");
$p = new PageGenerator(_T("Machines List view xmpp", 'glpi'));
$p->setSideMenu($sidemenu);
$p->display();

$computerpresence = isset($_GET['computerpresence']) ? $_GET['computerpresence'] : (isset($_SESSION['computerpresence']) ? $_SESSION['computerpresence'] : "all_computer");

$_SESSION['computerpresence'] = $computerpresence;

echo '<input type="radio" ';
if ($computerpresence == "all_computer") echo "checked";
echo ' id="namepresence1" name="namepresence" value="all_computer"/> ';
echo '<label for="namepresence1" style="display:initial;">'._('All computers').'</label>';
echo '<input type="radio" ';
if ($computerpresence == "presence") echo "checked";
echo ' id="namepresence2" name="namepresence" value="presence"/> ';
echo '<label for="namepresence2" style="display:initial;">'._('Online computers').'</label>';
echo '<input type="radio" ';
if ($computerpresence == "no_presence") echo "checked";
echo ' id="namepresence3" name="namepresence" value="no_presence"/> ';
echo '<label for="namepresence3" style="display:initial;">'._('Offline computers').'</label>';



$ajax = new AjaxFilterParamssearch(urlStrRedirect("base/computers/ajaxMachinesList"));


        $chaine = array(
        'id'                    => _T("Identifiant Machine: ", 'xmppmaster'),
        'jid'                   => _T("Jabber Identifiers: ", 'xmppmaster'),
        'uuid_serial_machine'   => _T("Serial Setup Identifier Machine: " , 'xmppmaster'),
        'need_reconf'           => _T("Reconfiguration needed: " , 'xmppmaster'),
        'enabled'               => _T("Machine online: " , 'xmppmaster'),
        'platform'              => _T("Machine Platform: " , 'xmppmaster'),
        'archi'                 => _T("Architecture Machine: " , 'xmppmaster'),
        'hostname'              => _T("Hostname: ", 'xmppmaster'),
        'uuid_inventorymachine' => _T("Glpi Inventory UUID: " , 'xmppmaster'),
        'ippublic'              => _T("Public IP: ", 'xmppmaster'),
        'ip_xmpp'               => _T("IP used to talk to xmpp: ", 'xmppmaster'),
        'macaddress'            => _T("Mac Adress used to talk to xmpp: " , 'xmppmaster'),
        'subnetxmpp'            => _T("Subnet: " , 'xmppmaster'),
        'agenttype'             => _T("Agent type: " , 'xmppmaster'),
        'classutil'             => _T("Usage class: ", 'xmppmaster'),
        'groupdeploy'           => _T("Relay agent server used: ", 'xmppmaster'),
        'ad_ou_machine'         => _T("Actif Directory OU Machine: " , 'xmppmaster'),
        'ad_ou_user'            => _T("Actif Directory OU User: " , 'xmppmaster'),
        'kiosk_presence'        => _T("Kiosk enabled: " , 'xmppmaster'),
        'lastuser'              => _T("Last user name: " , 'xmppmaster'),
        'regedit'               => _T("keys Registers Windows: "  , 'xmppmaster'),
        'glpi_description'      => _T("GLPI Description: "  , 'xmppmaster'),
        'glpi_owner_firstname'  => _T("GLPI Owner firstname: " , 'xmppmaster'),
        'glpi_owner_realname'   => _T("GLPI Owner real name: ", 'xmppmaster'),
        'glpi_owner'            => _T("GLPI Owner: " , 'xmppmaster'),
        'model'                 => _T("GLPI Model computer: ", 'xmppmaster'),
        'manufacturer'          => _T("GLPI Manufacturer: ", 'xmppmaster'),
        'entityname'            => _T("GLPI Entity Name: " , 'xmppmaster'),
        'entitypath'            => _T("GLPI full Entity Name: ", 'Xmppmaster'),
        'entityid'              => _T("GLPI Entity Identifiant: ", 'xmppmaster'),
        'locationname'          => _T("GLPI Location Name: " , 'xmppmaster'),
        'locationpath'          => _T("GLPI full Location Name: ", 'Xmppmaster'),
        'locationid'            => _T("GLPI Location Identifiant: ", 'xmppmaster'),
        'listipadress'          => _T("IP List Adress on Machine: " , 'xmppmaster'),
        'broadcast'             => _T("IP List Broadcast: ", 'xmppmaster'),
        'gateway'               => _T("Gateway: " , 'xmppmaster'),
        'mask'                  => _T("List Mask Network: " , 'xmppmaster'),
        'keysyncthing'          => _T("Syncthing Key: " , 'xmppmaster'));


$ajax->setfieldsearch(array_flip ($chaine ));

list($list, $values) = getEntitiesSelectableElements();

$listWithAll = array_merge([_T("All my entities", "glpi")], $list);
$valuesWithAll = array_merge([""], $values);

$ajax->setElements($listWithAll);
$ajax->setElementsVal($valuesWithAll);
$ajax->display();
echo '<br /><br /><br /><br />';
$ajax->displayDivToUpdate();
?>
<script type="text/javascript">
//jQuery('#location option[value=""]').prop('selected', true);

    function getQuerystringDef(key, default_) {
        if (default_==null) default_="";
        key = key.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
        var regex = new RegExp("[\\?&]"+key+"=([^&#]*)");
        var qs = regex.exec(window.location.href);

        if(qs == null)
            return default_;

        else
            return qs[1];
    }
    //Radiobox Mode
    jQuery('input[type=radio][name=namepresence]').change(function(){

        var valselect  = this.value;
        var url = window.location.href;

        if( !getQuerystringDef("computerpresence", false)){
            var url = window.location.href + "&" + "computerpresence"  + "=" + valselect;
            window.location = url;
        }
        else{
            var array_url = url.split("?");
            var adress = array_url[0];
            var parameters = array_url[1];
            var parameterlist = parameters.split("&");
            parameterlist.pop();
            parameterstring = parameterlist.join('&');
            var url = adress + "?" + parameterstring + "&" + "computerpresence"  + "=" + valselect;
            window.location = url;
        }

    });
</script>
