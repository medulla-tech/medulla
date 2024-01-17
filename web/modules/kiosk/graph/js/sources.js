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
var selectedId = [];
jQuery(document).ready(function(){
    let sourceSelector = "#source";
    let source = jQuery(sourceSelector);
    let jstree = jQuery("#jstree");
    let treeToggler = jQuery("#treeToggler");

    treeToggler.on("click", function(){
        toggleTree();
    });

    handleSourceChange();

    source.change(function() {
        handleSourceChange();
    });

    function handleSourceChange() {
        let selectedOU = source.val();

        if (selectedOU === "No Ou") {
            jstree.hide();
            treeToggler.hide();
        } else {
            var ous = [];
            var selectedId = [];
            loadAndShowTree(selectedOU);
        }
    }

    function loadAndShowTree(selectedOU) {
        // destroy the old jstree before loading the new data
        if(jstree.jstree(true)) {
            jstree.jstree("destroy");
        }

        treeToggler.val("+");

        jstree.load('/mmc/modules/kiosk/kiosk/ajaxSourceOu.php', {'ou': selectedOU.toLowerCase().replace(/ /g,"_")}, function(result){
            jstree.show();
            treeToggler.show();

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

        });

        jstree.show();
        treeToggler.show();
    }

    function toggleTree() {
        if(treeToggler.val() == "+") {
            jstree.jstree('open_all');
            treeToggler.val("-");
        } else {
            jstree.jstree('close_all');
            treeToggler.val("+");
        }
    }
});
