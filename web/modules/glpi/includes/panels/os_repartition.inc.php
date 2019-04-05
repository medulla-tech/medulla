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
require_once("modules/pulse2/includes/xmlrpc.inc.php");
require_once("modules/pulse2/includes/locations_xmlrpc.inc.php");
include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/base/includes/computers.inc.php");
require_once("modules/glpi/includes/xmlrpc.php");
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
    $uninventorized = $total = get_computer_count_for_dashboard()['unregistered'];

    $pcs = array_map(function($pcs) {
    return array(
        'label' => $pcs['os'],
        'value' => $pcs['count'],
        'version' => $pcs['version'],
        'href' => urlStrRedirect("base/computers/createOSStaticGroup").'&os='.$pcs['os'].'&version='.$pcs['version'],
    );
}, $pcs);

  // Add the uninventorized machines to the os list
  $pcs[] = array(
      'label' => $uninventorized_text,
      'value' => $uninventorized,
      'version' => '',
      'href' => '',
  );

    $datas = json_encode($pcs);
        echo <<< SPACE
        <div id="os-graphs"></div>
        <script type="text/javascript">
          customPie("os-graphs",$datas);
        </script>
SPACE;
    }
}
?>
