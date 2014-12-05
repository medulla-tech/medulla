<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

include_once("modules/dashboard/includes/panel.class.php");
require_once("modules/pkgs/includes/xmlrpc.php");

$options = array(
    "class" => "AppstreamPanel",
    "id" => "appstream",
    "refresh" => 14400,
    "title" => _("Appstream"),
    "enable" => TRUE
);

class AppstreamPanel extends Panel {

    function display_content() {
		
        $featured_link_label = json_encode(_T('_X_ AppStream(s) available for subscription', 'pkgs'));
        $no_featured_text = json_encode(_T('No featured appstream found.', 'pkgs'));
        $excluded_packages = array_keys(getActivatedAppstreamPackages());
        $available = getAvailableAppstreamPackages();
        $excluded_packages = array_merge($excluded_packages, array_map(function($item){
            return $item['options']['package_name'];
        }, $available['product'])); 
        $excluded_packages = json_encode(array_unique($excluded_packages));

        print '<div id="appstream_panel_content"></div>';
        print <<<EOS
<script type="text/javascript">
var $=jQuery;
$(function(){
    var appstream_featured_url = 'http://serviceplace.mandriva.com/api/v1/services/appstream/1.0/?mandriva_featured=True&category=appstream';
    var panel = $('#appstream_panel_content');
    var excluded_packages = $excluded_packages;
    var featured_packages = [];
   $.get(appstream_featured_url, function(result){
        panel.html('');
        if (!result.length)
            return;
        for (var i=0; i<result.length; i++){
            item = result[i];
            var featured = true;
            for (var j=0; j<item.variable_options[0].data.choices.length; j++)
            {
                if (excluded_packages.indexOf(item.variable_options[0].data.choices[j][0]) != -1){
                    featured = false;
                    break;
                }
            }
            
            if (featured){
                featured_packages.push(item);
            }
        }
        if (featured_packages.length == 0)
        {
            panel.append($no_featured_text);
            return;
        }
        var featured_link = $('<a>').attr('href', 'http://serviceplace.mandriva.com/services/?p=140');
        featured_link.html($featured_link_label.replace('_X_', featured_packages.length));
        panel.append($('<center>').append(featured_link)); 
        panel.append('<br/>');
        panel.append('<br/>');

        for (var i=0; i<featured_packages.length; i++){
            item = featured_packages[i];
            console.log(item);  
            var appstream_link = $('<a>').attr('href', item.url);
            appstream_link.html(item.name);
            panel.append(appstream_link);
            
        }
    });
});
</script>
EOS;
    }
}
