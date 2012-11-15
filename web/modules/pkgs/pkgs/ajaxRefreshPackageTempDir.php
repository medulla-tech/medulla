<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once("modules/pkgs/includes/xmlrpc.php");

$files = getTemporaryFiles($_GET['papi']);

$r = new SelectItem("rdo_files");
$vals = array();
$keys = array();
foreach ($files as $fi) {
    if ($fi[1] == True) {
        $vals[] = $fi[0];
        $keys[] = $fi[0];
    }
}
$r->setElementsVal($vals);
$r->setElements($keys);

$r->display();
?>
<script type="text/javascript">
    /*
     * Auto fill fields of form
     * if tempdir is empty (when changing packageAPI)
     * default tempdir will be chosen in ajaxGetSuggestedCommand
     * php file.
     */
    // FIXME: duplicated fillForm function
    function fillForm(selectedPapi, tempdir) {
        url = '<?php echo urlStrRedirect("pkgs/pkgs/ajaxGetSuggestedCommand")?>&papiid=' + selectedPapi;
        if (tempdir != undefined) {
            url += '&tempdir=' + tempdir;
        }
        new Ajax.Request(url, {
            onSuccess: function(response) {
                $('label').value = response.headerJSON.label;
                $('version').value = response.headerJSON.version;
                $('commandcmd').value = response.headerJSON.commandcmd;
            }
        });
    }
    // fill form when changing temp package
    $('rdo_files').observe('change', function() {
        var box = $('rdo_files');
        var selectedIndex = box.selectedIndex;
        var tempdir = box.options[selectedIndex].value;
        var box = $('p_api');
        var selectedIndex = box.selectedIndex;
        var selectedPapi = box.options[selectedIndex].value;
        fillForm(selectedPapi, tempdir);
    });
</script>
