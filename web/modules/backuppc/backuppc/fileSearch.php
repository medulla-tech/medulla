<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require_once("modules/backuppc/includes/xmlrpc.php");
require_once("modules/backuppc/includes/functions.php");
require_once("modules/backuppc/includes/html.inc.php");

// ===========================================================================
// ===========================================================================

$package = array();

// display an edit config form 
$f = new ValidatingForm();
$f->push(new Table());

$host = $_GET['objectUUID'];


// Get backup Nums =======================================

$response = get_backup_list($host);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

if (count($response['data']))
    $backups = $response['data'][0];
else {
    print _T('There is no backup point for this machine.','backuppc');
    return;
}

// Get all backup shares =================================

$sharenames = array();
// Get all sharenames
foreach ($backups as $backup_num){
    $response = get_share_names($host, $backup_num);
    
    if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
    }
    
    $sharenames = array_merge($sharenames,$response['data']);
}

$sharenames = array_unique($sharenames);

// ========= BUILDING FORM ========================================

$f->add(new HiddenTpl("host"), array("value" => $host, "hide" => True));
 
// =====================================================================
// FILENAME
// =====================================================================
 
$f->add(
    new TrFormElement(_T('File name','backuppc'), new InputTpl('filename')),
    array("value" => isset($_POST['filename'])?$_POST['filename']:'',"required" => True)
);

// =============================================================================
// BACKUP NUM SELECT FIELD  =====================================================
// =============================================================================

$sel = new SelectItem("backupnum");
$list = array();
$list[-1] = _T('All','backuppc');

foreach ($backups as $num)
    $list[intval($num)] = _T('Backup#','backuppc').$num;  #TODO : Change this to backuptime
$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));

if (isset($_POST['backupnum']))
    $sel->setSelected($_POST['backupnum']);
else
    $sel->setSelected(-1);

 $f->add(
    new TrFormElement(_T("Backup point","backuppc"), $sel,
    array())
);

// =============================================================================
// SHARENAME SELECT FIELD  =====================================================
// =============================================================================

$sel = new SelectItem("sharename");
$list = array();
$list[-1] = _T('All','backuppc');

foreach ($sharenames as $sharename)
    $list[$sharename] = $sharename;  #TODO : Change this to backuptime
$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));

if (isset($_POST['sharename']))
    $sel->setSelected($_POST['sharename']);
else
    $sel->setSelected(-1);

 $f->add(
    new TrFormElement(_T("Folder","backuppc"), $sel,
    array())
);


// =====================================================================
// MIN AND MAX FILESIZE
// =====================================================================

$f->add(new HiddenTpl("minsize"), array("value" => -1, "hide" => True));
$f->add(new HiddenTpl("maxsize"), array("value" => -1, "hide" => True));

/*
$f->add(
    new TrFormElement(_T('Minimum file size','backuppc'), new InputTpl('minsize')),
    array("value" => isset($_POST['minsize'])?$_POST['minsize']:'',"required" => True)
);

$f->add(
    new TrFormElement(_T('Maximum file size','backuppc'), new InputTpl('maxsize')),
    array("value" => isset($_POST['maxsize'])?$_POST['maxsize']:'',"required" => True)
);
*/
// =====================================================================

$f->pop();
$f->addButton("bsearch",_T('Search','backuppc'));
$f->display();

// ===== AJAX FILE TABLE ==============================================

$ajax = new AjaxFilterLocation(urlStrRedirect("backuppc/backuppc/ajaxFileSearch"),'container','location',$_POST);

$fils = array('.');
$fils_v = array('.');
$ajax->setElements($fils);
$ajax->setElementsVal($fils_v);
$ajax->display();
echo "<br/><br/>";
$ajax->displayDivToUpdate();

?>

<script src="modules/backuppc/lib/jquery-1.10.1.min.js"></script>
<script type="text/javascript">
// Avoid prototype <> jQuery conflicts
jQuery.noConflict();

jQuery(function(){
    
    shareLine = jQuery('.removeShare:first').parents('tr:first').clone();
        
     // Remove Share button
     jQuery('.removeShare').click(function(){
         if (jQuery('.removeShare').length > 1)
             jQuery(this).parents('tr:first').remove();
         // Switch to custom profile
         jQuery('select#backup_profile').val(0);
     });
     
     
     // Add Share button
     jQuery('#addShare').click(function(){
        var newline = shareLine.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find('input[type=text]').val('');
         newline.find('textarea').val('');

         newline.find('.removeShare').click(function(){
            if (jQuery('.removeShare').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
        // Switch to custom profile
         jQuery('select#backup_profile').val(0);
     });
     
     // PERIOD FUNCS
     
    periodLine = jQuery('.removePeriod:first').parents('tr:first').clone();
    
    // Multiselect listbox
    multiselConfig = {
        height: 120,
        header: false,
        minWidth : 180,
        noneSelectedText : '<?php echo _T('Select days','backuppc'); ?>',
        selectedText : '<?php echo _T('Select days','backuppc'); ?>'
     };
    jQuery("select[multiple=true]").multiselect(multiselConfig);
     
     // Remove period button
     jQuery('.removePeriod').click(function(){
         if (jQuery('.removePeriod').length > 1)
             jQuery(this).parents('tr:first').remove();
         // Switch to custom profile
         jQuery('select#period_profile').val(0);
     });
     
     // Hour mask inputs
     jQuery('input[name="starthour[]"]').mask('99:99');
     jQuery('input[name="endhour[]"]').mask('99:99');
     
     // Add period button
     jQuery('#addPeriod').click(function(event,nobtn){
        var idx = parseInt(jQuery('select:last').attr('name').replace('days','').replace('[]',''))+1;        
        if (isNaN(idx)) idx = 0;
        var newline = periodLine.clone().insertBefore(jQuery(this).parents('tr:first'));
         newline.find('input[type=text]').val('');
         newline.find('select').val([])
                 .attr({'name':'days'+idx+'[]','id':'days'+idx+'[]'})
         if (!nobtn)
            newline.find('select').multiselect(multiselConfig);
         newline.find('.removePeriod').click(function(){
            if (jQuery('.removePeriod').length > 1)
                jQuery(this).parents('tr:first').remove();
        });
        // Hour mask inputs
        newline.find('input[name="starthour[]"]').mask('99:99');
        newline.find('input[name="endhour[]"]').mask('99:99');
        // Switch to custom profile
         jQuery('select#period_profile').val(0);
     });
    
    
    // If any input changes, profile => custom
    function switchBckToCustom(){
        // If profile select we pass
        if (jQuery(this).attr('name') != 'backup_profile')
            jQuery('select#backup_profile').val(0);
    }
    jQuery('select[multiple=true],input[name="sharenames[]"],textarea[name="excludes[]"]').change(switchBckToCustom);   
    function switchPrdToCustom(){
        // If profile select we pass
        if (jQuery(this).attr('name') != 'period_profile')
            jQuery('select#period_profile').val(0);
    }
    jQuery('select[multiple=true],input[name=full],input[name=incr],input[name="starthour[]"],input[name="endhour[]"]').change(switchPrdToCustom);   
    
    // Profiles definition
    backup_profiles = <?php print json_encode($backup_profiles) ?> ;
    period_profiles = <?php print json_encode($period_profiles) ?> ;
    
    // Backup Profile selection
    jQuery('select#backup_profile').change(function(){
        // Selected profile
        selProfile = jQuery(this).val();    
        for (var i = 0 ; i < backup_profiles.length ; i++ )
            if (backup_profiles[i]['id'] == selProfile) {
                // Deleting Sharenames lines
                jQuery('.removeShare').each(function(){
                    jQuery(this).parents('tr:first').remove();
                });
                // Adding profile shares
                var _sharenames = backup_profiles[i]['sharenames'].split('\n');
                var _excludes = backup_profiles[i]['excludes'].split('||');
                jQuery('#encoding').val(backup_profiles[i]['encoding']);
                for (var z = 0 ; z < _sharenames.length ; z++ ){
                    jQuery('#addShare').trigger('click');
                    jQuery('input[name="sharenames[]"]:last').val(_sharenames[z]).change(switchBckToCustom);
                    jQuery('textarea[name="excludes[]"]:last').val(_excludes[z]).change(switchBckToCustom);
                    jQuery('.removeShare:last').click(switchBckToCustom);
                }
                
                break;
            }
        jQuery(this).val(selProfile);
        
    });
    
    // Period Profile selection
    jQuery('select#period_profile').change(function(){
        // Selected profile
        selProfile = jQuery(this).val();    
        for (var i = 0 ; i < period_profiles.length ; i++ )
            if (period_profiles[i]['id'] == selProfile) {
                // Deleting Sharenames lines
                jQuery('.removePeriod').each(function(){
                    jQuery(this).parents('tr:first').remove();
                });
                
                jQuery('input[name=full]:last').val(parseFloat(period_profiles[i]['full'])+0.03).change(switchPrdToCustom);
                jQuery('input[name=incr]:last').val(parseFloat(period_profiles[i]['incr'])+0.03).change(switchPrdToCustom);
                
                // Adding profile periods
                var regex = /([0-9.]+)=>([0-9.]+):([^:]+)/;
                
                var _periods = period_profiles[i]['exclude_periods'].split('\n');
                for (var z = 0 ; z < _periods.length ; z++ ){
                    jQuery('#addPeriod').trigger('click',[1]);
                    var matches = _periods[z].match(regex);
                    var _starthour = parseFloat(matches[1]);
                    var _endhour = parseFloat(matches[2]);
                    var _days = matches[3].split(',');
                    (_days);
                    
                    jQuery('input[name="starthour[]"]:last').val(("0" + parseInt(_starthour)).slice(-2)+':'+("0" + parseInt((_starthour-parseInt(_starthour))*60)).slice(-2))
                            .change(switchPrdToCustom);
                    jQuery('input[name="endhour[]"]:last').val(("0" + parseInt(_endhour)).slice(-2)+':'+("0" + parseInt((_endhour-parseInt(_endhour))*60)).slice(-2))
                            .change(switchPrdToCustom);
                    jQuery('select[multiple=true]:last').val(_days).multiselect(multiselConfig).change(switchPrdToCustom);
                    jQuery('.removeShare:last').click(switchPrdToCustom);
                }
                
                break;
            }
        jQuery(this).val(selProfile);
        
    });
    
    <?php
    if (isset($_GET['preselected_profile']))
        print "jQuery('select#backup_profile').trigger('change');";
    ?>
    
});   
   
    
</script>



<div id="restoreDiv"></div>

<script type="text/javascript">
function BrowseDir(dir){
//    new Ajax.Updater('container','main.php?module=backuppc&submod=backuppc&action=ajaxBrowseFiles&host=&sharename=', { asynchronous:true, evalScripts: true});
    new Ajax.Updater('<?php echo  $ajax->divid; ?>','<?php echo  $ajax->url; ?>folder='+dir+'<?php echo  $ajax->params ?>', { asynchronous:true, evalScripts: true});
}

function RestoreFile(paramstr){
//    new Ajax.Updater('container','main.php?module=backuppc&submod=backuppc&action=ajaxBrowseFiles&host=&sharename=', { asynchronous:true, evalScripts: true});
    new Ajax.Updater('restoreDiv','<?php echo urlStrRedirect("backuppc/backuppc/ajaxRestoreFile"); ?>&'+paramstr, { asynchronous:true, evalScripts: true});
    setTimeout("refresh();",4000);
}

</script>

<?php
// Downloaded files table
include("modules/backuppc/backuppc/ajaxDownloadsTable.php");

?>

<div id="restoreDiv"></div>