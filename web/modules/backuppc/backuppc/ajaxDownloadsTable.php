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

// Setting max per page to 50
$conf["global"]["maxperpage"] = 50;

print '<div id="downloadTable">';

$download_status = get_download_status();

// Sorting function
function cmp($a,$b){
    return ($a['time']<$b['time'])? 1 : -1;
}

uasort($download_status,'cmp');

if ($count=count($download_status)) {
    
    printf("<br/><br/><h2>%s</h2>",_T('Requested restores','backuppc'));
    
    $params = array();
    $paths = array_keys($download_status);
    $names = array();
    $times = array();
    $status = array();
    
    // Host
    if (isset($_GET['host'])) 
        $host = $_GET['host'];
    elseif (isset($_GET['objectUUID'])) 
        $host = $_GET['objectUUID'];
    else
        return;
    
    // Icons
    $emptyAction = new EmptyActionItem();
    $downloadAction = new ActionItem(_T("Download", "backuppc"),"download","display","dir", "backuppc", "backuppc");
    $actions = array(); // Actions array
    
    $refresh = 0; // Refresh is disabled by default
    
    foreach ($download_status as $filepath => $dstatus)
    {
        if ($host != $dstatus['host'])
            continue;
        
        $times[] = strftime(_T("%A, %B %e %Y",'backuppc').' %H:%M',$dstatus['time']);
        
        // If it is not a direct restore
        if (strpos($filepath,'>DIRECT:') === FALSE ) {
            $params[] = array('dir'=>$filepath);
            $paths[] = $filepath;
            $name = basename($filepath);
            
            $actions[] = $downloadAction;
        }
        else {
            // Direct restore
            $params[] = array('dir'=>'');
            $paths[] = '';
            $name = sprintf('<a href="#"></a>%s (%s %s)',
                    _T('Latest direct restore to host','backuppc'),_T('to','backuppc'),
                    str_replace('//', '/', $dstatus['destdir']));
            
            $actions[] = $emptyAction;
        }
        
        
        if ($dstatus['status']==0) {
            $status[] = '<img src="modules/msc/graph/images/status/inprogress.gif" alt=""/>';
            $name = sprintf('<a href="#">%s</a>',$name);
            $refresh = 1; // We want a refresh after X second
        }
        else
            if ($dstatus['err']==0)
                $status[] = '<img src="modules/msc/graph/images/status/success.png" alt=""/>';
            else {
                $status[] = '<img src="modules/msc/graph/images/status/failed.png" alt=""/> '.$dstatus['errtext'];
                $name = sprintf('<a href="#">%s</a>',$name);
            }
        $names[] = $name;
    }
    
    $n = new OptimizedListInfos($names, _T("Destination", "backuppc"));
    $n->addExtraInfo($times, _T("Restore time", "backuppc"));
    $n->addExtraInfo($status, _T("Status", "backuppc"));
    $n->setCssClass("file");
    $filter1 = '';
    $n->setNavBar(new AjaxNavBar(0, $filter1));
    $n->setParamInfo($params);
    $n->addActionItemArray($actions);
    $n->start = 0;
    $n->end = 50;
    $n->setItemCount(count($names));
    $n->display();
}

print '</div>';
?>

<script type="text/javascript">
function refresh(){
        parentcontainer = jQuery('div#downloadTable').parent();
        jQuery.get(
            "<?php  echo 'main.php?module=backuppc&submod=backuppc&action=ajaxDownloadsTable&host='.$host; ?>",
             function(data){
                jQuery('div#downloadTable').remove();
                parentcontainer.append(data);
        });
}


<?php 
if ($refresh) {
   print "setTimeout('refresh();',3000);" ;
}
?>

</script>
