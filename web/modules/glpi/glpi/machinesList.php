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
global $conf;


$p = new PageGenerator(_T("Machines List view xmpp", 'glpi'));
$p->setSideMenu($sidemenu);
$p->display();

$computerpresence = isset($_GET['computerpresence']) ? $_GET['computerpresence'] : (isset($_SESSION['computerpresence']) ? $_SESSION['computerpresence'] : "all_computer");

$_SESSION['computerpresence'] = $computerpresence;

echo '<div style="position: relative; z-index: 1000; padding: 10px 0; margin-bottom: 20px; background: transparent; clear: both;">';
echo '<input type="radio" ';
if ($computerpresence == "all_computer") echo "checked";
echo ' id="namepresence1" name="namepresence" value="all_computer"/> ';
echo '<label for="namepresence1" style="display:initial; cursor: pointer;">'._('All computers').'</label>';
echo '<input type="radio" ';
if ($computerpresence == "presence") echo "checked";
echo ' id="namepresence2" name="namepresence" value="presence"/> ';
echo '<label for="namepresence2" style="display:initial; cursor: pointer;">'._('Online computers').'</label>';
echo '<input type="radio" ';
if ($computerpresence == "no_presence") echo "checked";
echo ' id="namepresence3" name="namepresence" value="no_presence"/> ';
echo '<label for="namepresence3" style="display:initial; cursor: pointer;">'._('Offline computers').'</label>';
echo '</div>';


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


$ajax = new AjaxFilterParamssearch(urlStrRedirect("base/computers/ajaxMachinesList",$chaine) );
$ajax->setfieldsearch(array_flip ($chaine ));

list($list, $values) = getEntitiesSelectableElements();


# FIXME: This variable should be added as a parameter.
$root_sees_all_machines = 0;//  1 The root user sees all the machines, even those with neither entity nor uuid_inventory.

if ($root_sees_all_machines == 1)
{
    if($_SESSION['login'] == "root")
        $valuesWithAll = array_merge([-1], $values);
    else
        $valuesWithAll = array_merge([implode(',',$values)], $values);
        $listWithAll = array_merge([_T("All my entities", "glpi")], $list);
}
else{
    $valuesWithAll = array_merge([implode(',',$values)], $values);
    $listWithAll = array_merge([_T("All my entities", "glpi")], $list);
}

$ajax->setElements($listWithAll);
$ajax->setElementsVal($valuesWithAll);
$ajax->display();
echo '<br /><br /><br /><br />';
$ajax->displayDivToUpdate();
?>


<script type="text/javascript">
// Fonction utilitaire : récupère un paramètre GET avec une valeur par défaut
function getQueryParam(key, defaultValue = "") {
    const params = new URLSearchParams(window.location.search);
    return params.has(key) ? params.get(key) : defaultValue;
}

// Gestion du changement sur les boutons radio
jQuery('input[type=radio][name=namepresence]').change(function () {
    const valselect = this.value;

    // Utilisation de l'API URL
    const url = new URL(window.location.href);
    url.searchParams.set("computerpresence", valselect);

    // Recharge la page avec le nouveau paramètre
    window.location.href = url.toString();
});
</script>

