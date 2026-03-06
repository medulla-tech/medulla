<?php
/*
 *  (c) 2021 siveo, http://www.siveo.net
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
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("graph/navbar.inc.php");
require("modules/base/computers/localSidebar.php");

require_once("modules/xmppmaster/includes/xmlrpc.php");

$p = new PageGenerator(_T("XMPP Machines list", 'glpi'));
$p->setSideMenu($sidemenu);
$p->display();

$computerpresence = isset($_GET['computerpresence']) ? $_GET['computerpresence'] : (isset($_SESSION['computerpresence']) ? $_SESSION['computerpresence'] : "all");
$_SESSION['computerpresence'] = $computerpresence;

$presenceOptions = array(
    'all' => _('All computers'),
    'presence' => _('Online computers'),
    'nopresence' => _('Offline computers')
);

$presenceSelectHtml = '<span class="searchfield"><select id="computerpresence" class="searchfieldreal noborder">';
foreach ($presenceOptions as $value => $label) {
    $selected = ($computerpresence == $value) ? 'selected' : '';
    $presenceSelectHtml .= '<option value="' . $value . '" ' . $selected . '>' . $label . '</option>';
}
$presenceSelectHtml .= '</select></span>';

$ajax = new AjaxFilter(urlStrRedirect("base/computers/ajaxXmppMachinesList"), "container", array('login' => $_SESSION['login']), 'formRunning');
$ajax->display();
$ajax->displayDivToUpdate();
?>

<script type="text/javascript">
jQuery(function() {
    jQuery('#searchBest').prepend(<?php echo json_encode($presenceSelectHtml); ?>);

    jQuery('#computerpresence').on('change', function() {
        var url = new URL(window.location.href);
        url.searchParams.set("computerpresence", this.value);
        window.location.href = url.toString();
    });
});
</script>
