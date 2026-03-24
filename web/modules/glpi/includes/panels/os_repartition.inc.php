<?php

/**
 * (c) 2012 Mandriva, http://www.mandriva.com
 * (c) 2018 Siveo, http://www.siveo.net
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
require_once("modules/medulla_server/includes/xmlrpc.inc.php");
require_once("modules/medulla_server/includes/locations_xmlrpc.inc.php");
include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
?>
<script src="modules/dashboard/graph/js/pie.js"></script>
<?php
$options = array(
  "class" => "os_repartitionPanel",
  "id" => "osrepartition",
  "refresh" => 960,
  "title" => _T("Operating systems", "glpi"),
);

class os_repartitionPanel extends Panel {
  function display_content() {
    $urlRedirect = urlStrRedirect("base/computers/createOSStaticGroup");
    $pcs = xmlrpc_get_os_for_dashboard();

    $uninventorized_text = _T("Uninventoried Machines", "dashboard");
    $uninventorized = get_computer_count_for_dashboard()['total_uninventoried'];

    // Sort by count descending
    usort($pcs, function($a, $b) { return $b['count'] - $a['count']; });

    // Group OS beyond top 5 into "Other" with tooltip grouped by family
    $maxDisplay = 5;
    if (count($pcs) > $maxDisplay) {
        $top = array_slice($pcs, 0, $maxDisplay);
        $rest = array_slice($pcs, $maxDisplay);
        $otherCount = 0;
        $families = [];
        foreach ($rest as $r) {
            $otherCount += $r['count'];
            $os = $r['os'];
            if (stripos($os, 'Windows') !== false) $family = 'Windows';
            elseif (stripos($os, 'macOS') !== false || stripos($os, 'OS X') !== false) $family = 'macOS';
            elseif (stripos($os, 'BSD') !== false) $family = 'BSD';
            elseif (stripos($os, 'Android') !== false) $family = 'Android';
            else $family = 'Linux';
            $label = $r['version'] ? $r['os'] . ' (' . $r['version'] . ')' : $r['os'];
            $families[$family][] = ['label' => $label, 'count' => $r['count']];
        }
        $tooltipHtml = '<table class="ttable">';
        foreach ($families as $familyName => $items) {
            $tooltipHtml .= '<tr class="ttabletr tt-section"><td class="ttabletd" colspan="2">' . htmlspecialchars($familyName) . '</td></tr>';
            foreach ($items as $item) {
                $tooltipHtml .= '<tr class="ttabletr"><td class="ttabletd">' . htmlspecialchars($item['label']) . '</td><td class="ttabletd">: ' . $item['count'] . '</td></tr>';
            }
        }
        $tooltipHtml .= '</table>';
        $top[] = [
            'os' => _T('Other', 'dashboard'),
            'version' => '',
            'count' => $otherCount,
            'tooltip' => $tooltipHtml
        ];
        $pcs = $top;
    }

    $pcs = array_map(function($pcs) {
    // android hmdm devices redirect to mobile group creation
    if ($pcs['os'] === 'Android' && $pcs['version'] === 'HMDM') {
        $href = urlStrRedirect("mobile/mobile/addGroup").'&autoselect=all&name=widget';
    } else {
        $href = urlStrRedirect("base/computers/createOSStaticGroup").'&os='.$pcs['os'].'&version='.$pcs['version'];
    }

    $item = array(
        'label' => $pcs['os'],
        'value' => $pcs['count'],
        'version' => $pcs['version'],
        'href' => $href,
    );
    if (isset($pcs['tooltip'])) {
        $item['tooltip'] = $pcs['tooltip'];
    }
    return $item;
}, $pcs);

  // Add the uninventorized machines to the os list
  $pcs[] = array(
      'label' => $uninventorized_text,
      'value' => $uninventorized,
      'version' => '',
      'href' => '',
  );

    $datas = json_encode($pcs);
    $top5Label = json_encode(_T("Distribution — Top 5 OS", "dashboard"));
        echo <<< SPACE
        <div id="os-graphs"></div>
        <script type="text/javascript">
          var pieLabelTop5 = $top5Label;
          customPie("os-graphs",$datas);
        </script>
SPACE;
    }
}
?>
