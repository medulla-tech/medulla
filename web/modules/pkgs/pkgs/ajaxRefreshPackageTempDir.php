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
require_once("modules/pkgs/includes/functions.php");

// This session variable is used for auto-check upload button
if (isset($_SESSION['pkgs-add-reloaded'][$_GET['papi']])) {
    $_SESSION['pkgs-add-reloaded'][$_GET['papi']]++;
}
else {
    $_SESSION['pkgs-add-reloaded'][$_GET['papi']] = 0;
}

$_SESSION['p_api_id'] = $_GET['papi'];
$files = getTemporaryFiles($_GET['papi']);

if(count($files)) {
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
        jQuery.ajax({
            'url': url,
            type: 'get',
            success: function(data){
                jQuery('#version').val(data.version);
                jQuery('#commandcmd').val(data.commandcmd);
            }
        });
        
    }
    // fill form when changing temp package
    jQuery('#rdo_files').change(function() {
        var tempdir = jQuery(this).val();
        var selectedPapi = jQuery('#p_api').val();
        fillForm(selectedPapi, tempdir);
    });
    
    var jcArray = new Array('label', 'version', 'description', 'commandcmd');
    for (var dummy in jcArray) {
        try {
            jQuery('#'+jcArray[dummy]).css("background","#FFF");
            jQuery('#'+jcArray[dummy]).removeAttr('disabled'); // TODO: Check if no error here
        }
        catch (err){
            // this php file is prototype ajax request with evalscript
            // enabled.
        }
    }
</script>
<?php
}
else {
    // This session variable is used in this case:
    // If it is _first_ time we display Package API tempdir and this is empty,
    // auto-check upload button
    if ($_SESSION['pkgs-add-reloaded'][$_GET['papi']]) {
    print "<strong style='color: red;'>" . _T("Package API temporary directory is empty", "pkgs") . "<strong>";
?>
        <script type="text/javascript">
    var jcArray = new Array('label', 'version', 'description', 'commandcmd');
    for (var dummy in jcArray) {
        try {
            jQuery('#'+jcArray[dummy]).css("background","#DDD");
            jQuery('#'+jcArray[dummy]).attr('disabled', 'disabled'); // TODO: Check if no error here
        }
        catch (err){
            // this php file is prototype ajax request with evalscript
            // enabled.
        }
    }
        </script>

<?php
    }
    else {
?>
<script type="text/javascript">
    var selectedPapi = jQuery('#p_api').val();
    jQuery('#package-temp-directory').load( '<?php echo urlStrRedirect("pkgs/pkgs/ajaxDisplayUploadForm") ?>&papi=' + selectedPapi);
    // reset form fields
    jQuery('#version').val('');
    jQuery('#commandcmd').val('');
    jQuery('input[type="radio"][name="package-method"][value="upload"]:first').attr("checked", "checked");
    jQuery('#directory-label').html("<?php echo sprintf(_T("Files upload (<b><u title='%s'>%sM max</u></b>)", "pkgs"), _T("Change post_max_size and upload_max_filesize directives in php.ini file to increase upload size.", "pkgs"), get_php_max_upload_size()) ?>");
</script>
<?php
    }
}
?>
