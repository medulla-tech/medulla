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

var sending = false;
var savingModalDelay = 2000;

jQuery("#bvalid").click(function() {
    if(sending)
        return;

    if(jQuery("#name").val() == "")
        jQuery("#name").focus();

    else if(ous.length == 0)
        alert(MSG_OU_REQUIRED, '', 'alert-warning');
    else
    {
        sending = true;
        jQuery("#bvalid").prop("disabled", true);
        sendForm();
    }
});

function sendForm(){
    var action = jQuery("[name='action']").val()
    if(action == 'undefined')
        var url = "modules/kiosk/kiosk/ajaxAddProfile.php";
    else
    {
        action = action[0].toUpperCase() + action.substring(1)
        var url = "modules/kiosk/kiosk/ajax"+action+"Profile.php";
    }

    // Create json which contains all the needed infos
    var datas = {};
    datas['name'] = jQuery("#name").val();
    datas['active'] = jQuery("#status").val();
    datas['owner'] = jQuery("[name='owner']").val();
    datas['source'] = jQuery("#source").val();
    datas['id'] = jQuery("[name='id']").val();
    datas['ous'] = ous;
    datas['packages'] = generate_json();

    var redirect = function() {
        window.location.replace("main.php?module=kiosk&submod=kiosk&action=index");
    };
    var modalShown = false;

    var timer = setTimeout(function() {
        timer = null;
        modalShown = true;
        alert(MSG_SAVING_PROFILE, '', 'modal-info');
        var popup = jQuery("#popup");
        popup.find(".js-alert-content").append('<div class="kiosk-saving-spinner"><span class="spinner spinner-lg"></span></div>');
        popup.find(".js-alert-actions").remove();
        popup.find("a.popup_close_btn").hide();
        jQuery("#overlay").off("click", closePopup);
        popup.css("margin-top", -(popup.outerHeight() / 2) + "px");
    }, savingModalDelay);

    // Send the infos to ajaxAddProfile.php
    jQuery.post(url, datas, null, "json").done(function(data){
        if(timer !== null)
            clearTimeout(timer);
        if(data && data.status === "exists")
        {
            if(modalShown)
            {
                jQuery("#popup, #overlay").stop(true, true);
                jQuery("#popup a.popup_close_btn").show();
            }
            alert(data.message);
            sending = false;
            jQuery("#bvalid").prop("disabled", false);
            jQuery("#name").focus();
            return;
        }
        redirect();
    }).fail(function(){
        if(timer !== null)
            clearTimeout(timer);
        if(modalShown)
        {
            closePopup();
            jQuery("#popup").promise().done(function() {
                jQuery(this).find("a.popup_close_btn").show();
            });
        }
        sending = false;
        jQuery("#bvalid").prop("disabled", false);
    });
}
