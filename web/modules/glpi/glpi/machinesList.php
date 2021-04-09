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
        'id'                    => _T("Machine ID", 'xmppmaster'),
        'jid'                   => _T("Jabber ID", 'xmppmaster'),
        'uuid_serial_machine'   => _T("Machine UUID" , 'xmppmaster'),
        'need_reconf'           => _T("Reconf. requested" , 'xmppmaster'),
        'enabled'               => _T("Online" , 'xmppmaster'),
        'platform'              => _T("Platform" , 'xmppmaster'),
        'archi'                 => _T("Architecture" , 'xmppmaster'),
        'hostname'              => _T("Hostname", 'xmppmaster'),
        'uuid_inventorymachine' => _T("GLPI ID" , 'xmppmaster'),
        'ip_xmpp'               => _T("IP address", 'xmppmaster'),
        'subnetxmpp'            => _T("Subnet" , 'xmppmaster'),
        'macaddress'            => _T("Mac address" , 'xmppmaster'),
        'ippublic'              => _T("Public IP", 'xmppmaster'),
        'agenttype'             => _T("Agent type" , 'xmppmaster'),
        'classutil'             => _T("Usage class", 'xmppmaster'),
        'groupdeploy'           => _T("Relay JID", 'xmppmaster'),
        'ad_ou_machine'         => _T("AD machine OU" , 'xmppmaster'),
        'ad_ou_user'            => _T("AD user OU" , 'xmppmaster'),
        'kiosk_presence'        => _T("Kiosk enabled" , 'xmppmaster'),
        'lastuser'              => _T("Last user connected" , 'xmppmaster'),
        'keysyncthing'          => _T("Syncthing ID" , 'xmppmaster'),
        'regedit'               => _T("Registry keys"  , 'xmppmaster'),
        'glpi_description'      => _T("GLPI description"  , 'xmppmaster'),
        'glpi_owner_firstname'  => _T("Owner firstname" , 'xmppmaster'),
        'glpi_owner_realname'   => _T("Owner lastname", 'xmppmaster'),
        'glpi_owner'            => _T("Owner" , 'xmppmaster'),
        'model'                 => _T("Model", 'xmppmaster'),
        'manufacturer'          => _T("Manufacturer", 'xmppmaster'),
        'entityname'            => _T("Short entity name" , 'xmppmaster'),
        'entitypath'            => _T("Full entity name", 'Xmppmaster'),
        'entityid'              => _T("Entity ID", 'xmppmaster'),
        'locationname'          => _T("Short location name" , 'xmppmaster'),
        'locationpath'          => _T("Full location name", 'Xmppmaster'),
        'locationid'            => _T("Location ID", 'xmppmaster'),
        'listipadress'          => _T("IP addresses" , 'xmppmaster'),
        'mask'                  => _T("Network mask" , 'xmppmaster'),
        'broadcast'             => _T("Broadcast address", 'xmppmaster'),
        'gateway'               => _T("Gateway address" , 'xmppmaster'));


$ajax->setfieldsearch(array_flip ($chaine ));

list($list, $values) = getEntitiesSelectableElements();

$listWithAll = array_merge([_T("All my entities", "glpi")], $list);
$valuesWithAll = array_merge([implode(',',$values)], $values);

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
