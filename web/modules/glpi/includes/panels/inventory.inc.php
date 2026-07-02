<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$options = array(
    "class" => "GlpiPanel",
    "id" => "inventory",
    "refresh" => 3600,
    "title" => _T("Inventories", "glpi"),
);

class GlpiPanel extends Panel
{
    public function display_content()
    {
        $result = xmlrpc_get_inventories_for_dashboard();
        $count = $result['count'];
        $days = $result['days'];

        $phoneResult = xmlrpc_get_phone_inventories_for_dashboard();
        $phoneCount = $phoneResult['count'];
        $hasPhones = ($phoneCount['green'] + $phoneCount['orange'] + $phoneCount['red']) > 0;

        $jsonCount      = json_encode($count);
        $jsonDays       = json_encode($days);
        $jsonPhoneCount = json_encode($phoneCount);
        $total          = get_computer_count_for_dashboard();
        $unregistered   = json_encode($total['total_uninventoried']);
        $createGroupText  = json_encode(_T("Create a group", "glpi"));
        $lessThanText     = json_encode(_T("< %s days: %percent% (%d)", "glpi"));
        $moreThanText     = json_encode(_T("> %s days: %percent% (%d)", "glpi"));
        $unregisteredText = json_encode(_T("Uninventoried machines", "glpi"));
        $urlRedirect      = json_encode(urlStrRedirect("base/computers/createStaticGroup"));
        $urlPhones        = json_encode(urlStrRedirect("mobile/mobile/glpiPhonesList"));

        $computersSectionTitle = _T("Computers", "glpi");
        $phoneSectionTitle     = _T("Phones", "mobile");

        $phoneSectionHtml = '';
        if ($hasPhones) {
            $phoneSectionHtml = '<div class="general-section-title" style="margin-top:12px;">' . htmlspecialchars($phoneSectionTitle) . '</div>'
                . '<div id="phone-inventory-graphs" style="display:flex;flex-direction:column;align-items:center;flex:1;width:100%;"></div>';
        }

        echo <<< INVENTORY
    <div class="general-section-title">$computersSectionTitle</div>
    <div id="inventory-graphs" style="display:flex;flex-direction:column;align-items:center;flex:1;"></div>
    $phoneSectionHtml
    <script type="text/javascript">
    var machineCount  = $jsonCount,
        days          = $jsonDays,
        phoneCount    = $jsonPhoneCount,
        unregistered  = $unregistered,
        lessThanText  = $lessThanText,
        moreThanText  = $moreThanText,
        unregisteredText = $unregisteredText,
        createGroupText  = $createGroupText,
        urlRedirect   = $urlRedirect,
        urlPhones     = $urlPhones;

    var datas = [
      {'label': '', 'value': 0, 'href': ''},
      {'label': '', 'value': 0, 'href': ''},
      {
        'label': lessThanText.replace("%s", days['orange']).split(": %percent%")[0],
        'value':("green" in machineCount)?machineCount["green"]:0,
        'href':urlRedirect+"&group=green&days="+days['orange'],
      },
      {
        'label': moreThanText.replace("%s", days['orange']).split(": %percent%")[0],
        'value':("orange" in machineCount)?machineCount["orange"]:0,
        'href':urlRedirect+"&group=orange&days="+days['orange'],
      },
      {
        'label': moreThanText.replace("%s", days['red']).split(": %percent%")[0],
        'value':("red" in machineCount)?machineCount["red"]:0,
        'href':urlRedirect+"&group=red&days="+days['red'],
      },
      {
        'label': unregisteredText,
        'value':unregistered,
        'href':'#',
      }
    ];
    donut("inventory-graphs", datas, "Total", parseInt(machineCount["green"])+parseInt(machineCount["red"])+parseInt(machineCount["orange"])+parseInt(unregistered));

    if (document.getElementById('phone-inventory-graphs')) {
      var phoneDatas = [
        {'label': '', 'value': 0, 'href': ''},
        {'label': '', 'value': 0, 'href': ''},
        {
          'label': lessThanText.replace("%s", days['orange']).split(": %percent%")[0],
          'value':("green" in phoneCount)?phoneCount["green"]:0,
          'href': urlPhones + "&group=green&days=" + days['orange'],
        },
        {
          'label': moreThanText.replace("%s", days['orange']).split(": %percent%")[0],
          'value':("orange" in phoneCount)?phoneCount["orange"]:0,
          'href': urlPhones + "&group=orange&days=" + days['orange'],
        },
        {
          'label': moreThanText.replace("%s", days['red']).split(": %percent%")[0],
          'value':("red" in phoneCount)?phoneCount["red"]:0,
          'href': urlPhones + "&group=red&days=" + days['red'],
        },
        {'label': '', 'value': 0, 'href': ''}
      ];
      donut("phone-inventory-graphs", phoneDatas, "Total", parseInt(phoneCount["green"])+parseInt(phoneCount["red"])+parseInt(phoneCount["orange"]));
    }
    </script>
INVENTORY;
    }
}
