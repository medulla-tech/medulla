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
var kioskSelectedOus = [];

jQuery(document).ready(function(){
    var source = jQuery("#source");
    var entity = jQuery("#entity_id");
    var row = jQuery("#ou-row");
    var label = jQuery("#ou-label");
    var tools = jQuery("#ou-tools");
    var filter = jQuery("#ouFilter");
    var toggleAll = jQuery("#ouToggleAll");
    var tree = jQuery("#ou-tree");
    var users = jQuery("#ou-users");
    var picked = [];
    var request = 0;
    var usersRequest = 0;

    tree.on("change", "input[type='checkbox']", function(){
        var index = picked.indexOf(this.value);
        if(this.checked && index === -1)
            picked.push(this.value);
        else if(!this.checked && index !== -1)
            picked.splice(index, 1);
        refreshSelection();
        showUsers();
    });

    tree.on("click", ".kiosk-ou-chevron", function(){
        setExpanded(jQuery(this), this.getAttribute("aria-expanded") !== "true");
        refreshToggleAll();
    });

    toggleAll.on("click", function(){
        var expand = !anyExpanded();
        tree.find(".kiosk-ou-chevron").each(function(){
            setExpanded(jQuery(this), expand);
        });
        refreshToggleAll();
    });

    filter.on("input", applyFilter).on("keydown", function(e){
        if(e.key === "Enter")
            e.preventDefault();
    });

    source.add(entity).on("change", loadTree);
    loadTree();

    function setExpanded(chevron, expanded) {
        chevron.attr("aria-expanded", expanded ? "true" : "false");
        chevron.closest("li").toggleClass("kiosk-ou-collapsed", !expanded);
    }

    function anyExpanded() {
        return tree.find(".kiosk-ou-chevron[aria-expanded='true']").length > 0;
    }

    function refreshToggleAll() {
        toggleAll.text(anyExpanded() ? kioskForm.messages.collapseAll : kioskForm.messages.expandAll);
    }

    function applyFilter() {
        var value = jQuery.trim(filter.val()).toLowerCase();
        var items = tree.find("li").removeClass("kiosk-ou-match");
        tree.toggleClass("kiosk-ou-filtering", value !== "");
        if(value === "") {
            items.show();
            return;
        }
        items.filter(function(){
            return jQuery(this).children(".kiosk-ou-row").text().toLowerCase().indexOf(value) !== -1;
        }).addClass("kiosk-ou-match");
        items.each(function(){
            var item = jQuery(this);
            item.toggle(item.hasClass("kiosk-ou-match")
                || item.parents("li.kiosk-ou-match").length > 0
                || item.find("li.kiosk-ou-match").length > 0);
        });
    }

    function refreshSelection() {
        kioskSelectedOus = [];
        tree.find("input[type='checkbox']").each(function(){
            var box = jQuery(this);
            var own = picked.indexOf(this.value) !== -1;
            var included = box.closest("li").parents("li").children(".kiosk-ou-row").children("input").filter(function(){
                return picked.indexOf(this.value) !== -1;
            }).length > 0;
            box.prop("checked", own || included).prop("disabled", included);
            box.closest(".kiosk-ou-row").toggleClass("kiosk-ou-included", included);
            if(own && !included)
                kioskSelectedOus.push(this.value);
        });
    }

    function showUsers() {
        var current = ++usersRequest;
        var counted = (source.val() === "ou_user" || source.val() === "ou_machine");
        if(!counted || kioskSelectedOus.length == 0) {
            users.empty().hide();
            return;
        }
        jQuery.post(kioskForm.usersUrl, {'source': source.val(), 'roots': kioskSelectedOus, 'entity_id': entity.val()}, function(html){
            if(current !== usersRequest)
                return;
            users.text(jQuery.trim(html));
            users.toggle(jQuery.trim(html) !== "");
        }, "html");
    }

    function loadTree() {
        var current = ++request;
        var profile = kioskForm.profile;
        var stored = (source.val() === profile.source && entity.val() === profile.entity);

        usersRequest++;
        tree.empty().removeClass("kiosk-ou-empty kiosk-ou-filtering");
        users.empty().hide();
        filter.val("");
        picked = [];
        kioskSelectedOus = [];

        if(source.val() === "entity" || !entity.val()) {
            row.hide();
            return;
        }

        var datas = {'source': source.val(), 'entity_id': entity.val()};
        if(stored)
            datas['profile_id'] = profile.id;

        jQuery.post(kioskForm.sourcesUrl, datas, function(html){
            if(current !== request)
                return;
            var groups = (source.val() === "group" || source.val() === "ldap");
            label.text(groups ? kioskForm.messages.groupLabel : kioskForm.messages.ouLabel);
            row.show();
            tree.html(html);

            var count = tree.find("li").length;
            if(count == 0) {
                tools.hide();
                tree.addClass("kiosk-ou-empty").text(kioskForm.messages.noValue);
                return;
            }

            if(stored) {
                tree.find("input[type='checkbox']").each(function(){
                    if(profile.ous.indexOf(this.value) !== -1 && picked.indexOf(this.value) === -1)
                        picked.push(this.value);
                });
            }

            var foldable = tree.find(".kiosk-ou-chevron").length > 1;
            filter.toggle(count > 10);
            toggleAll.toggle(foldable);
            tools.toggle(count > 10 || foldable);
            refreshToggleAll();
            refreshSelection();
            showUsers();
        }, "html");
    }
});
