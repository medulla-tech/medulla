/**
 * (c) 2016 Siveo, http://siveo.net
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


jQuery("#bvalid").click(function() {
    if(jQuery("#name").val() == "")
    {
        jQuery("#name").focus();
    }
    else
        sendForm();
});

function sendForm(){
    var url = "modules/kiosk/kiosk/ajaxAddProfile.php";

    // Create json which contains all the needed infos
    var datas = {};
    datas['name'] = jQuery("#name").val();
    datas['active'] = jQuery("#status").val();
    datas['packages'] = generate_json();
    // Send the infos to ajaxAddProfile.php
    jQuery.post(url, datas, function(result){

        // the datas printed in ajaxAddProfile.php are stored in result
        alert(result);
    });
}