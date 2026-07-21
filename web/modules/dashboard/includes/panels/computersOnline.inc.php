<?php
/*
 * (c) 2016 siveo, http://www.siveo.net/
 *
 * This file is part of Management Console (MMC).
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

require_once("modules/dashboard/includes/panel.class.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/mobile/includes/xmlrpc.php");

$options = array(
    "class" => "ComputersOnlinePanel",
    "id" => "computersOnline",
    "refresh" => 300,
    "title" => _T("Machines Online", "dashboard"),
    "enable" => true,
);

class ComputersOnlinePanel extends Panel
{
    public function display_content()
    {
        $urlRedirect = urlStrRedirect("base/computers/createMachinesStaticGroup");
        $counts = get_computer_count_for_dashboard();

        $total_machines = $counts['total'];
        $machines_online = $counts['total_online'];
        $machines_offline = $counts['total_offline'];

        $phones = xmlrpc_get_hmdm_online_count();
        $phones_total   = intval($phones['total']);
        $phones_online  = intval($phones['online']);
        $phones_offline = intval($phones['offline']);
        $hasPhones = $phones_total > 0;

        $online_text  = _T("Online", "dashboard")." : ";
        $offline_text = _T("Offline", "dashboard")." : ";

        $urlPhones        = urlStrRedirect("mobile/mobile/index");
        $urlPhonesOnline  = $urlPhones . '&status=online';
        $urlPhonesOffline = $urlPhones . '&status=offline';

        $computersSectionTitle = _T("Computers", "glpi");
        $phoneSectionTitle     = _T("Phones", "mobile");

        $phoneSectionHtml = '';
        if ($hasPhones) {
            $phoneSectionHtml = '<div class="general-section-title" style="margin-top:12px;">' . htmlspecialchars($phoneSectionTitle) . '</div>'
                . '<div id="phonesonline-graph" style="display:flex;flex-direction:column;align-items:center;flex:1;width:100%;"></div>';
        }

        echo <<< ONLINE
          <div class="general-section-title">$computersSectionTitle</div>
          <div id="computersonline-graph"></div>
          $phoneSectionHtml
          <script>
            var onlineDatas = [
              {'label': '$offline_text', 'value': $machines_offline, "href": "$urlRedirect&machines=offline"},
              {'label': '', 'value': 0, "href": ""},
              {"label": "$online_text", "value":$machines_online, "href":"$urlRedirect&machines=online"},
            ];
            donut("computersonline-graph", onlineDatas, "Total", $total_machines);

            if (document.getElementById('phonesonline-graph')) {
              var phoneOnlineDatas = [
                {'label': '$offline_text', 'value': $phones_offline, "href": "$urlPhonesOffline"},
                {'label': '', 'value': 0, "href": ""},
                {"label": "$online_text", "value": $phones_online, "href": "$urlPhonesOnline"},
              ];
              donut("phonesonline-graph", phoneOnlineDatas, "Total", $phones_total);
            }
          </script>
ONLINE;
    }
}
