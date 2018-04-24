/**
 * (c) 2018 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
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

jQuery(function(){

    jQuery('#jstree').jstree();

    jQuery('#jstree').on("changed.jstree", function (e, data) {
        var users = [];
        //data.selected contains the selected elements
        jQuery.each(data.selected, function(id, element){
            users.push(jQuery("#"+element).attr('data-root'))
        })
            jQuery("#users").load('/mmc/modules/kiosk/kiosk/ajaxGetUsersForOu.php', {'roots':users}, function(result){

            });
    });
    // 8 interact with the tree - either way is OK
    jQuery('button').on('click', function () {
        jQuery('#jstree').jstree(true).select_node('child_node_1');
        jQuery('#jstree').jstree('select_node', 'child_node_1');
        jQuery.jstree.reference('#jstree').select_node('child_node_1');
    });
});