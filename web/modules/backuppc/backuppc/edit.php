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

$backup_profile_id = get_host_backup_profile($host);
$period_profile_id = get_host_period_profile($host);

if ( $backup_profile_id == -1 )
{
    print _T("Host backup is not set.",'backuppc');
    return;
}

$response = get_host_config($host);

// Check if error occured
if ($response['err']) {
    new NotifyWidgetFailure(nl2br($response['errtext']));
    return;
}

// Getting all avavaible profiles
$backup_profiles = get_backup_profiles();
$period_profiles = get_period_profiles();

// BackupPC config for this host
$host_config = $response['host_config'];

$f->add(new HiddenTpl("host"), array("value" => $host, "hide" => True));

// Backup Active
$f->add(
        new TrFormElement(_T("Enabled","backuppc"), new CheckboxTpl('active')),
        array("value" => ($host_config['BackupsDisable']=='0' ? 'checked' : ''))
    );

// BACKUP PROFILE SELECT FIELD

$sel = new SelectItem("backup_profile");
$list = array();
$list[0] = _T('Custom','backuppc');
foreach ($backup_profiles as $profile)
    $list[intval($profile['id'])] = $profile['profilename'];
$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));
$sel->setSelected($backup_profile_id);

 $f->add(
    new TrFormElement(_T("Fileset","backuppc"), $sel,
    array())
);

 // Client host encoding

$sel = new SelectItem("encoding");
$list = array(
    "utf8"=>'UTF8',
    "cp1252" => _T('Windows-1252 - Western europe','backuppc'),
    "cp874" => _T('Windows-874 - Thai','backuppc'),
    "cp932" => _T('Windows-932 - Japanese','backuppc'),
    "cp936" => _T('Windows-936 - Chinese (simplified)','backuppc'),
    "cp949" => _T('Windows-949 - Korean','backuppc'),
    "cp950" => _T('Windows-950 - Chinese (traditional)','backuppc'),
    "cp1250" => _T('Windows-1250 - Latin (Central europe)','backuppc'),
    "cp1251" => _T('Windows-1251 - Cyrillic','backuppc'),
    "cp1253" => _T('Windows-1253 - Greek','backuppc'),
    "cp1254" => _T('Windows-1254 - Turkish','backuppc'),
    "cp1255" => _T('Windows-1255 - Hebrew','backuppc'),
    "cp1256" => _T('Windows-1256 - Arabic','backuppc'),
    "cp1257" => _T('Windows-1257 - Latin (Baltic languages)','backuppc'),
    "cp1258" => _T('Windows-1258 - Vietnamese','backuppc')
    );

$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));
$sel->setSelected($host_config['ClientCharset']);

 $f->add(
    new TrFormElement(_T("Client encoding","backuppc"), $sel,
    array())
);


// =====================================================================

// Exclude lists
$sharenames = $host_config['RsyncShareName'];
$excludes = $host_config['BackupFilesExclude'];

$i = 0;

foreach ($sharenames as $sharename) {
    
    $_excludes = isset($excludes[$sharename])?$excludes[$sharename]:array();    
    $_excludes = implode("\n", $_excludes);
    
    // Fields
    $fields = array(
        new InputTpl('sharenames[]'),
        new textTpl(_T('Excluded files','backuppc')),
        new TextareaTpl('excludes[]'),
        new buttonTpl('removeShare',_T('Remove','backuppc'),'removeShare')
        );
    
    $values = array(
        $sharename,
        '',
        $_excludes,
        ''
    );
    
    $f->add(
        new TrFormElement(_T('Folder','backuppc'), new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );
}

// Add Share button
$addShareBtn = new buttonTpl('addShare',_T('Add folder','backuppc'));
$addShareBtn->setClass('btnPrimary');
$f->add(
    new TrFormElement('', $addShareBtn),
    array()
);

//=======================================
// PERIOD PROFILE SELECT FIELD

$sel = new SelectItem("period_profile");
$list = array();
$list[0] = _T('Custom','backuppc');
foreach ($period_profiles as $profile)
    $list[intval($profile['id'])] = $profile['profilename'];
$sel->setElements(array_values($list));
$sel->setElementsVal(array_keys($list));
$sel->setSelected($period_profile_id);

 $f->add(
    new TrFormElement(_T("Schedule",'backuppc'), $sel,
    array())
);

// =====================================================================
// Period config

// FULL period
$f->add(
    new TrFormElement(_T('Interval between two full backups (days)','backuppc'), new InputTpl('full')),
    array("value" => $host_config['FullPeriod']==''?'':floatval($host_config['FullPeriod'])+0.03,"required" => True)
);

// INCR period
$f->add(
    new TrFormElement(_T('Interval between two incr backups (days)','backuppc'), new InputTpl('incr')),
    array("value" => $host_config['IncrPeriod']==''?'':floatval($host_config['IncrPeriod'])+0.03,"required" => True)
);

$daynames = array(
    _T('Monday','backuppc'),
    _T('Tuesday','backuppc'),
    _T('Wednesday','backuppc'),
    _T('Thursday','backuppc'),
    _T('Friday','backuppc'),
    _T('Saturday','backuppc'),
    _T('Sunday','backuppc')
);

// Exclude periods
$exclude_periods = explode("\n",$profile['exclude_periods']);
$z = 0;

foreach ($host_config['BlackoutPeriods'] as $period) {
    
    list($from,$to,$days) = array($period['hourBegin'],$period['hourEnd'],$period['weekDays']);

    $days = explode(',',$days);
   
    // DAYS SELECT
    $sel = new MultipleSelect('days'.$z++);
    $sel->setElements($daynames);
    $sel->setElementsVal(array('1','2','3','4','5','6','7'));
    foreach ($days as $day)
        $sel->setSelected(trim($day));
    
    // Start hour
    $fields = array(
        new hourInputTpl('starthour[]'),
        new textTpl(_T('to','backuppc')),
        new hourInputTpl('endhour[]'),
        new textTpl(_T('on','backuppc')),
        $sel,
        new buttonTpl('removePeriod',_T('Remove','backuppc'),'removePeriod')
        );
    
    $values = array(
        float2hhmm($from),
        '',
        float2hhmm($to),
        '',
        ''
    );
    
    $f->add(
        new TrFormElement(_T('Do not backup from','backuppc'), new multifieldTpl($fields)),
        array("value" => $values,"required" => True)
    );

    
}

// Add Period button
$addPeriodBtn = new buttonTpl('addPeriod',_T('Add schedule','backuppc'));
$addPeriodBtn->setClass('btnPrimary');
$f->add(
    new TrFormElement('', $addPeriodBtn),
    array()
);

// =====================================================================

$f->pop();
$f->addValidateButton("bconfirm");
$f->display();
?>

<script src="modules/backuppc/lib/jquery-1.10.1.min.js"></script>
<script src="modules/backuppc/lib/jquery-ui.min.js"></script>
<script src="modules/backuppc/lib/jquery.maskedinput-1.3.min.js"></script>
<script src="modules/backuppc/lib/jquery.multiselect.js"></script>
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