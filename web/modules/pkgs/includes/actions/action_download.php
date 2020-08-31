<?php
/**
 * (c) 2020 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net/
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");

/*
Descriptor template
{
  "step": 0,
  "actionlabel": "74484b48",
  "action": "action_download",
  "url": "https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v7.8.9/npp.7.8.9.Installer.exe",
  "fullpath": "./npp.exe"
},


PARAMS :
  action - Action name executed
  step - Incremental execution order
  label - used to map a "goto" action on it
  url - Url to download.
  fullpath - Used to specify the final name of the downloaded file (optional).
             If fullpath is not specified, the file will have the url as name
*/

extract($_POST);



$packageList = xmpp_packages_list();
$options = "";

foreach($packageList as $id=>$package)
{
    if(isset($packageuuid) && $packageuuid == $package['uuid'])
    {
        $options .= "<option value='".$package['uuid']."' selected>".$package['name']."</option>";
    }
    else
        $options .= "<option value='".$package['uuid']."'>".$package['name']."</option>";
}

$lab =  (isset($actionlabel))? $actionlabel : uniqid();
$fullpath = (isset($fullpath))? $fullpath : "";
$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1><?php echo _T('Download File', 'pkgs'); ?></h1>
</div>

<div class="content">
    <div>
        <input type="hidden" name="action" value="action_download" />
        <input type="hidden" name="step" />
        <table id="tableToggle">
            <tr class="toggleable">
            <?php
            $url = (isset($url))? $url : "";
            echo'
                <th width="16%">'._T("Step label :","pkgs").'</th>
                <th width="25%">
                <input type="text" name="actionlabel" value="'.$lab.'"/>';
                echo'
                </th>
                <th></th>
                <th></th>
            </tr>';
            echo '<tr class="toggleable">';
                if(isset($packageuuid))
                {
                    echo '<td width="16%">
                        <input type="checkbox" checked
                          onclick="if(jQuery(this).is(\':checked\')){
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                  }
                                  else{
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                  }" />'._T("Alternate package","pkgs").'
                    </td>
                    <td width="25%">
                        <select name="packageuuid">'.$options.'</select>
                    </td>';
                }
                else{
                    echo '<td width="16%">
                        <input type="checkbox"
                          onclick="if(jQuery(this).is(\':checked\')){
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                  }
                                  else{
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                  }" />'._T("Alternate package","pkgs").'
                    </td>
                    <td width="25%">
                        <select disabled name="packageuuid">'.$options.'</select>
                    </td>';
                }
            echo '
                <td></td><td></td>
            </tr>';

        echo '<th width="16%">'._T('Download File:', 'pkgs').'</th>
                <th>
                    <input type="text" name="url" value="'.$url.'"/>
                </th>
            </table>';
            ?>
        <!-- All extra options are added here-->
    </div>
 <input class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
