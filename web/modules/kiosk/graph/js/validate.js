/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */

var kioskSending = false;

jQuery(document).ready(function(){
    function applyFilter(filter, items) {
        var value = jQuery(filter).val().toLowerCase();
        jQuery(items).each(function() {
            jQuery(this).toggle(jQuery(this).text().toLowerCase().indexOf(value) > -1);
        });
    }

    jQuery("#availableFilter").on("keyup", function() {
        applyFilter("#availableFilter", "#available-packages li");
    });

    jQuery("#profileFilter").on("keyup", function() {
        applyFilter("#profileFilter", "#profile-packages li");
    });
});

function kioskSubmitProfile() {
    if(kioskSending || !validateForm("profile-form"))
        return false;

    if(jQuery("#source").val() !== "entity" && kioskSelectedOus.length == 0) {
        alert(kioskForm.messages.ouRequired, '', 'modal-info');
        return false;
    }

    var button = jQuery("#profile-form [name='bvalid']");
    var datas = {
        'name': jQuery("#name").val(),
        'active': jQuery("#status").val(),
        'entity_id': jQuery("#entity_id").val(),
        'source': jQuery("#source").val(),
        'ous': kioskSelectedOus,
        'packages': kioskProfilePackages(),
        'auth_token': jQuery("#profile-form [name='auth_token']").val()
    };
    if(kioskForm.profile.id !== null)
        datas['id'] = kioskForm.profile.id;

    kioskSending = true;
    button.prop("disabled", true);

    var modalShown = false;
    var timer = setTimeout(function() {
        timer = null;
        modalShown = true;
        alert(kioskForm.messages.saving, '', 'modal-info');
        var popup = jQuery("#popup");
        popup.find(".js-alert-content").append('<div class="kiosk-saving-spinner"><span class="spinner spinner-lg"></span></div>');
        popup.find(".js-alert-actions").remove();
        popup.find("a.popup_close_btn").hide();
        jQuery("#overlay").off("click", closePopup);
        popup.css("margin-top", -(popup.outerHeight() / 2) + "px");
    }, 2000);

    function giveBack(message, klass) {
        if(timer !== null)
            clearTimeout(timer);
        if(modalShown) {
            jQuery("#popup, #overlay").stop(true, true);
            jQuery("#popup a.popup_close_btn").show();
        }
        alert(message, '', klass);
        kioskSending = false;
        button.prop("disabled", false);
    }

    jQuery.post(kioskForm.saveUrl, datas, null, "json").done(function(data){
        if(data && data.status === "ok") {
            window.location.replace(kioskForm.listUrl);
            return;
        }
        giveBack((data && data.message) ? data.message : kioskForm.messages.failed, 'modal-info');
    }).fail(function(){
        giveBack(kioskForm.messages.failed);
    });

    return false;
}
