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
var ous = [];
var selectedId = []
jQuery(function(){
    //
    // Enable - disable the OUs tree
    //
    // Behaviour by default : useful for edit mode
    var old_ous = ous;
    var old_users = null;
    if(jQuery("#no_ou").is(":checked") == false)
    {
        jQuery("#treeToggler").hide();
        jQuery("#jstree").hide();
        old_ous = ous;
        old_users = jQuery("#users").html();
        ous = "none";
        jQuery("#users").html("");
    }
    else
    {
        jQuery("#jstree").show();
        ous = old_ous;
        jQuery("#users").html(old_users);
    }

    jQuery("#no_ou").on("click", function(){
        if(jQuery("#no_ou").is(":checked") == false)
        {
            jQuery("#treeToggler").hide();
            jQuery("#jstree").hide();
            old_ous = ous;
            old_users = jQuery("#users").html();
            ous = "none";
            jQuery("#users").html("");
        }
        else
        {
            jQuery("#jstree").show();
            jQuery("#treeToggler").show();
            ous = old_ous;
            jQuery("#users").html(old_users);
        }
    });

    if(typeof(jQuery("input[name='ous']").val()) != 'undefined')
    {
        var ousToEdit = jQuery("input[name='ous']").val().split(';');

        // From the listed OUs :
        // So firstly, copy the tree, because after declaring it as tree, it's DOM is modified
        var tmpTree = jQuery('#jstree');

        // Locate the data-root attribute which contains the selected ou and get data-id attribute.
        // The data-id attribute is the same as the id attributed to the leafs of the tree.
        jQuery.each(ousToEdit, function(id, value){
            selectedId.push(jQuery(tmpTree).find("[data-root='"+value+"']").attr('data-id'));
        });

        jQuery.each(ousToEdit, function(id,value){
            console.log(jQuery("[data-root='"+value+"']").html());
        });
    }

    jQuery('#jstree').jstree();

    // Finally now the ids of selected ous are stored in selectedId variable. The ous are selected by default in
    // the tree.
    jQuery('#jstree').jstree('select_node', selectedId);

    //jQuery.jstree.reference('#jstree').select_node("[data-root='bonsecours']");
    jQuery('#jstree').on("changed.jstree", function (e, data) {
        ous = [];
        //data.selected contains the selected elements
        jQuery.each(data.selected, function(id, element){
            ous.push(jQuery("#"+element).attr('data-root'))
        })
        jQuery("#users").load('/mmc/modules/kiosk/kiosk/ajaxGetUsersForOu.php', {'roots':ous}, function(result){

        });
    });

    jQuery("#treeToggler").on("click", function(){
      if(jQuery("#treeToggler").val() == "+")
      {
        jQuery('#jstree').jstree('open_all');
        jQuery("#treeToggler").val("-")
      }
      else
      {
        jQuery('#jstree').jstree('close_all');
        jQuery("#treeToggler").val("+")
      }
    });

});
